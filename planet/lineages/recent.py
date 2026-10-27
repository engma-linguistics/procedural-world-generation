"""The recent pass: the last ~30 kyr of a glacial time zoom at century steps.

Not new physics: the time zoom's frames (every 2 kyr) interpolated in time,
rain the time zoom doesn't store: a full climate.compute at every 2 kyr on the
time zoom's surface, ice, temperature offset and orbit (PW-599; as a finished
world's first climate), interpolated in time between (without it, the source
keyframe's rain scaled by exp(0.07 dT) with the local warming, as the time zoom
scales its rain), plus
seeded short-period variability that acts on habitat only: a red-noise global
anomaly (centuries) and regional episodes (cold spells, droughts) and, when
the window holds a deglaciation, one Younger Dryas-like cold reversal. The
ice and the coastline are the time zoom's. Design: docs/proposals/lineages.md.

    uv run python -m planet recent <timezoom-or-finished-world> [--kyr 30] [--step 0.1] [--every 0.5]

Time is kyr relative to the present (the chosen moment of the time zoom):
-30.0 ... 0.0. Stored as a run of kind 'timezoom' with meta.phase 'recent',
so the viewer's time-zoom UI plays it.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM
from ..grid import Grid, build_grid
from ..provenance import code_version
from .gridops import dist_km

TZ_LAYERS = ("elevation", "ice", "temperature", "climate", "tree_cover")
RAIN_K = 0.07  # per C: the time zoom's rain scaling (Clausius-Clapeyron)
STAT_KEYS = ("sea_level_m", "sea_level_change_m", "ice_pct", "ice_volume_mkm3", "ice_sea_equiv_mkm3", "max_ice_m",
             "global_temp_c", "obliquity", "eccentricity", "perihelion", "precession_index", "insol_65n_jul_anom",
             "insol_ice_summer_anom", "dT_global", "glacial_index", "land_pct", "max_elev_m")


@dataclass
class RecentParams:
    """Knobs of the recent pass (--set key=value). Times in kyr."""
    kyr: float = 30.0  # window length before the present
    step: float = 0.1  # the lineage model's step in this window (a century)
    every: float = 0.5  # a stored (viewer) frame every this
    seed: int | None = None  # variability seed; default from the time zoom's id and the present
    noise_sd: float = 0.35  # C: global red-noise anomaly (AR(1)) ...
    noise_tau: float = 0.3  # kyr: ... its memory
    episodes_per_kyr: float = 1 / 6  # regional cold spells and droughts
    reversal: bool = True  # a cold reversal in a deglaciation inside the window (Younger Dryas-like)
    climate_every: float = 2.0  # kyr: a full climate.compute on the time zoom's frames this far apart (0: rain scaled from the keyframe)


@dataclass
class Episode:
    kind: str  # 'cold spell' | 'drought' | 'cold reversal'
    t0: float  # kyr (relative to present, negative) when it starts ...
    t1: float  # ... and ends
    lat: float
    lon: float
    radius_km: float
    amp: float  # C (cold) or rain factor - 1 (drought, negative)
    hemi: int = 0  # cold reversal: the hemisphere (+1 N, -1 S), poleward of 40 deg

    def weight(self, t: float) -> float:
        ramp = min(0.05, (self.t1 - self.t0) / 4)  # 50-yr onsets and ends
        if t <= self.t0 or t >= self.t1:
            return 0.0
        return float(min(1.0, (t - self.t0) / ramp, (self.t1 - t) / ramp))


def _cap(grid: Grid, lat: float, lon: float, radius_km: float) -> np.ndarray:
    d = dist_km(grid, lat, lon)
    return np.where(d < radius_km, 0.5 * (1 + np.cos(np.pi * d / radius_km)), 0.0)


class Pass:
    """The recent pass in memory: fields at any time of the window (kyr rel. to present)."""

    def __init__(self, tz_ref: str, now_kyr: float | None = None, params: RecentParams | None = None,
                 world_ref: str | None = None):
        p = self.params = params or RecentParams()
        self.tz_dir = S.find_run(tz_ref)
        self.run, self.arr = T.load_frames(self.tz_dir, TZ_LAYERS)
        if self.run.get("kind") != "timezoom":
            raise ValueError(f"{tz_ref} is not a glacial time zoom")
        m = self.run["meta"]
        self.grid = build_grid(m["level"])
        self.ts = np.array([f["t"] for f in self.run["frames"]], float)
        self.now = float(self.ts[-1] if now_kyr is None else now_kyr)
        if not self.ts[0] <= self.now <= self.ts[-1]:
            raise ValueError(f"now {self.now:g} kyr is outside the time zoom (0-{self.ts[-1]:g} kyr)")
        self.start = max(float(self.ts[0]), self.now - p.kyr) - self.now  # (negative)
        if p.seed is None:
            p.seed = int(self.run["id"], 16) % 100000 + int(round(self.now * 10))
        self.rng = np.random.default_rng(p.seed)
        self._rain_ref(world_ref)
        self._variability()
        self._clim: tuple[np.ndarray, np.ndarray] | None = None  # (node times kyr rel. to the present, rain per node)
        self.climate_s = 0.0

    # -- the time zoom's frames, interpolated ---------------------------------------------------
    def _bracket(self, t: float) -> tuple[int, int, float]:
        a = self.now + t
        j = int(np.clip(np.searchsorted(self.ts, a), 1, len(self.ts) - 1))
        i = j - 1
        w = float(np.clip((a - self.ts[i]) / (self.ts[j] - self.ts[i]), 0, 1))
        return i, j, w

    def _lerp(self, name: str, t: float) -> np.ndarray:
        i, j, w = self._bracket(t)
        a, b = (T.frame(self.run, self.arr, name, k).astype(float) for k in (i, j))
        return a * (1 - w) + b * w

    def _rain_ref(self, world_ref):
        """Annual rain at a reference moment and that moment's temperature."""
        m = self.run["meta"]
        self.flow = None  # the world's river flow (lineages' contact corridors), if a world is given
        self.world_seed = None  # ...and its seed: the landmasses' names (names.py, PW-853)
        self.world_names: dict = {}  # ...and the owner's own names for some of them (planet name, PW-867)
        if world_ref:
            from .. import world as W
            w = W.load(S.find_world(world_ref))
            self.rain0, self.temp0 = w["layers"]["precipitation"].astype(float), w["layers"]["temperature"].astype(float)
            self.rain_src = f"world {w['meta'].get('id', world_ref)}"
            self.world_seed = w["meta"].get("seed")
            from .. import names as NM
            self.world_names = NM.load_overrides(S.find_world(world_ref).stem)
            if "flow" in w["layers"]:
                self.flow = w["layers"]["flow"].astype(float)
            return
        if m.get("source_run") and m["source_run"] != "earth":
            src = S.find_run(m["source_run"])
            run, arr = T.load_frames(src, ("precipitation", "temperature"))
            ts = np.array([f["t"] for f in run["frames"]])
            k = int(np.argmin(np.abs(ts - m["at_myr"])))
            self.rain0 = T.frame(run, arr, "precipitation", k).astype(float)
            self.temp0 = T.frame(run, arr, "temperature", k).astype(float)
            self.rain_src = f"run {m['source_run']} @ {ts[k]:g} Myr"
            return
        # (Earth's time zoom without a world: a rough rain from the climate classes)
        cl = T.frame(self.run, self.arr, "climate", 0).astype(int)
        guess = np.full(cl.shape, 600.0)
        guess[cl <= 1] = 2200; guess[cl == 2] = 1200; guess[(cl == 3) | (cl == 4)] = 120; guess[(cl == 5) | (cl == 6)] = 350
        self.rain0, self.temp0 = guess, T.frame(self.run, self.arr, "temperature", 0).astype(float)
        self.rain_src = "climate classes (rough)"

    def _climate(self):
        """The rain of a full climate at the time zoom's frames in the window (PW-599), made once: climate.compute on
        each frame's bed, ice, global temperature and orbit, as finish.py does for a finished world (its first
        climate, before the vegetation's feedback). Frames at least climate_every apart, with the one just before
        the window so the first steps interpolate."""
        if self._clim is not None:
            return self._clim
        from .. import climate, finish
        t0 = time.time()
        m = self.run["meta"]
        key = self._clim_key()
        hit = self._clim_read(key)
        if hit is not None:
            self._clim = hit
            self.climate_s = time.time() - t0
            return self._clim
        lo, ts = self.now + self.start, self.ts
        keep, last = [], -1e9
        before = np.flatnonzero(ts <= lo + 1e-9)
        for k in ([int(before[-1])] if len(before) else []) + [int(k) for k in np.flatnonzero((ts > lo + 1e-9) & (ts <= self.now + 1e-9))]:
            if ts[k] - last >= self.params.climate_every - 1e-9:
                keep.append(k)
                last = ts[k]
        tilt = float(m["params"].get("tilt", 23.44 if m["source_run"] == "earth" else 23.4))
        rain = []
        for k in keep:
            surf, ice = (T.frame(self.run, self.arr, n, k).astype(float) for n in ("elevation", "ice"))
            s = self.run["frames"][k]["stats"]
            st = {"stats": s, "elevation": surf - ice, "ice": ice, "dT": s["global_temp_c"] - 14.5}
            orbit = finish.orbit_dt(self.run, st) if all(k in s for k in finish.ORBIT_STATS) else None  # (a time zoom stores its orbit)
            c = climate.compute(self.grid, st["elevation"], st["dT"], tilt, ice, orbit_dt=orbit)
            rain.append(np.asarray(c["precip"], float))
        self._clim = (ts[keep] - self.now, np.stack(rain))
        self._clim_write(key)
        self.climate_s = time.time() - t0
        return self._clim

    # (the full climates cost minutes at L7 and depend only on the time zoom, the window and the code: kept in the
    # time zoom's folder, named by a key so a changed zoom, window or model never reads an old one; PW-740)
    def _clim_key(self) -> str:
        import hashlib
        st = (self.tz_dir / "run.json").stat()
        h = hashlib.sha256(f"{self.run['id']}:{st.st_size}:{st.st_mtime_ns}:{self.now!r}:{self.start!r}:"
                           f"{self.params.climate_every!r}".encode())
        h.update(S.code_digest().encode())
        return h.hexdigest()

    def _clim_read(self, key: str):
        try:
            with np.load(self.tz_dir / "recent_rain.npz", allow_pickle=False) as z:
                if str(z["_key"]) == key:
                    return z["tn"], z["rain"]
        except (OSError, ValueError, KeyError):
            pass
        return None

    def _clim_write(self, key: str) -> None:
        p = self.tz_dir / "recent_rain.npz"
        try:
            tmp = p.with_name("recent_rain.tmp.npz")
            np.savez(tmp, _key=np.array(key), tn=self._clim[0], rain=self._clim[1])
            tmp.replace(p)
        except OSError:
            pass

    def _rain_at(self, t: float) -> np.ndarray | None:
        """The full climate's rain at t (linear between its frames), or None outside them / when it is off."""
        if self.params.climate_every <= 0:
            return None
        tn, rn = self._climate()
        if t < tn[0] - 1e-9 or t > tn[-1] + 1e-9:
            return None
        if len(tn) == 1:
            return rn[0]
        j = int(np.clip(np.searchsorted(tn, t), 1, len(tn) - 1))
        w = float(np.clip((t - tn[j - 1]) / (tn[j] - tn[j - 1]), 0, 1))
        return rn[j - 1] * (1 - w) + rn[j] * w

    # -- variability ----------------------------------------------------------------------------
    def _variability(self):
        p, rng, g = self.params, self.rng, self.grid
        n = int(round((0 - self.start) / p.step)) + 1
        self.steps = self.start + np.arange(n) * p.step
        a = np.exp(-p.step / p.noise_tau)
        x = np.zeros(n)
        x[0] = rng.normal(0, p.noise_sd)
        for k in range(1, n):
            x[k] = a * x[k - 1] + rng.normal(0, p.noise_sd * np.sqrt(1 - a * a))
        self.noise = x
        self.episodes: list[Episode] = []
        span = -self.start
        land0 = self._land(0.0)
        lat = g.lat
        for _ in range(rng.poisson(span * p.episodes_per_kyr)):
            kind = "cold spell" if rng.random() < 0.55 else "drought"
            dur = rng.uniform(0.2, 0.8)
            t0 = rng.uniform(self.start, -dur)
            w = np.where(land0, 1.0, 0.0) * (np.abs(lat) > 25 if kind == "cold spell" else np.abs(lat) < 50)
            if w.sum() == 0:
                continue
            c = int(rng.choice(g.n, p=w / w.sum()))
            amp = -rng.uniform(1.0, 2.5) if kind == "cold spell" else -rng.uniform(0.25, 0.5)
            self.episodes.append(Episode(kind, round(t0, 2), round(t0 + dur, 2), round(float(lat[c]), 1),
                                         round(float(g.lon[c]), 1), round(float(rng.uniform(1500, 3000))), round(amp, 2)))
        if p.reversal:
            gi = np.array([f["stats"].get("glacial_index", 0.0) for f in self.run["frames"]])
            sel = (self.ts >= self.now + self.start) & (self.ts <= self.now)
            idx = np.flatnonzero(sel)
            if len(idx) > 1:
                hi = idx[np.argmax(gi[idx])]
                after = idx[idx > hi]
                if len(after) and gi[hi] - gi[after].min() >= 0.4:
                    lo = after[np.argmin(gi[after])]
                    mid = 0.5 * (self.ts[hi] + self.ts[lo]) - self.now
                    ice = T.frame(self.run, self.arr, "ice", int(hi))
                    hemi = 1 if (ice[g.lat > 0] > 0).sum() >= (ice[g.lat < 0] > 0).sum() else -1
                    self.episodes.append(Episode("cold reversal", round(mid - 0.6, 2), round(mid + 0.6, 2),
                                                 50.0 * hemi, 0.0, 0.0, -2.0, hemi))
        self.episodes.sort(key=lambda e: e.t0)
        self._caps = [(_cap(g, e.lat, e.lon, e.radius_km) if e.kind != "cold reversal"
                       else np.clip((np.abs(lat) - 40) / 10, 0, 1) * (np.sign(lat) == e.hemi)) for e in self.episodes]
        self._amp = 0.5 + np.abs(lat) / 90.0  # polar amplification of a global change

    def anomaly(self, t: float) -> tuple[np.ndarray, np.ndarray, float]:
        """(temperature anomaly C, rain factor, global noise C) at t."""
        k = int(np.clip(round((t - self.start) / self.params.step), 0, len(self.noise) - 1))
        dT = self.noise[k] * self._amp
        rf = np.ones(self.grid.n)
        for e, cap in zip(self.episodes, self._caps):
            w = e.weight(t)
            if w <= 0:
                continue
            if e.kind == "drought":
                rf = rf * (1 + e.amp * w * cap)
            else:
                dT = dT + e.amp * w * cap
        return dT, rf, float(self.noise[k])

    # -- fields ---------------------------------------------------------------------------------
    def _land(self, t: float) -> np.ndarray:
        return (self._lerp("elevation", t) > 0) | (self._lerp("ice", t) > 0.5)

    def fields(self, t: float, variability: bool = True) -> dict:
        """The habitat inputs at t (kyr rel. to present)."""
        i, j, w = self._bracket(t)
        elev, ice, temp = self._lerp("elevation", t), self._lerp("ice", t), self._lerp("temperature", t)
        clim = T.frame(self.run, self.arr, "climate", i if w < 0.5 else j)
        trees = self._lerp("tree_cover", t) if "tree_cover" in self.arr else np.zeros(self.grid.n)
        dT, rf, g = self.anomaly(t) if variability else (0.0, 1.0, 0.0)
        rain = self._rain_at(t)
        if rain is None:  # (outside the full climate's frames, or switched off: the keyframe's rain scaled)
            rain = self.rain0 * np.clip(np.exp(RAIN_K * (temp - self.temp0)), 0.5, 1.5)
        temp = temp + dT
        rain = rain * np.exp(RAIN_K * dT) * rf
        return {"elevation": elev, "ice": ice, "temperature": temp, "precipitation": rain, "climate": clim,
                "tree_cover": trees, "land": (elev > 0) | (ice > 0.5), "noise_c": g}

    def stats(self, t: float) -> dict:
        i, j, w = self._bracket(t)
        a, b = self.run["frames"][i]["stats"], self.run["frames"][j]["stats"]
        out = {"t": round(t, 3)}
        for k in STAT_KEYS:
            if k in a and k in b:
                out[k] = round(a[k] * (1 - w) + b[k] * w, 3)
        out["ice_age"] = (a if w < 0.5 else b).get("ice_age")
        out.update(mean_speed_cmyr=0, max_speed_cmyr=0, plates=a.get("plates"), landmasses=a.get("landmasses"),
                   largest_landmass_pct=a.get("largest_landmass_pct"))
        return out

    def frame_times(self) -> np.ndarray:
        e = self.params.every
        n = int(np.floor(-self.start / e + 1e-9))
        return np.round(-np.arange(n, -1, -1) * e, 4)

    def meta(self) -> dict:
        m = self.run["meta"]
        return {"timezoom": self.run["id"], "timezoom_name": self.run["name"], "now_kyr": self.now,
                "source_run": m.get("source_run"), "source_name": m.get("source_name"), "at_myr": m.get("at_myr"),
                "recent": asdict(self.params), "rain_from": self.rain_src,
                "episodes": [asdict(e) for e in self.episodes]}


def events(ps: Pass) -> list[dict]:
    out = []
    for e in ps.episodes:
        dur = round((e.t1 - e.t0) * 1000)
        if e.kind == "cold reversal":
            txt = f"cold reversal during the deglaciation: {e.amp:+g} C poleward of 40 deg{'N' if e.hemi > 0 else 'S'} for {dur} years"
        elif e.kind == "cold spell":
            txt = f"{dur}-year cold spell, {e.amp:+g} C within {e.radius_km:g} km"
        else:
            txt = f"{dur}-year drought, rain x{1 + e.amp:.2f} within {e.radius_km:g} km"
        out.append({"t": round(e.t0, 2), "kind": e.kind, "text": txt, "lat": e.lat, "lon": e.lon})
    return out


def save(ps: Pass, name: str | None = None) -> Path:
    """Store the recent pass as a run (kind timezoom, meta.phase 'recent')."""
    g, m = ps.grid, ps.run["meta"]
    t0 = time.time()
    times = ps.frame_times()
    specs = {k: ps.run["layers"][k] for k in TZ_LAYERS if k in ps.run["layers"]}
    specs["precipitation"] = S.LAYERS["precipitation"]
    data = {k: [] for k in specs}
    frames = []
    src_frames = ps.run["frames"]
    for t in times:
        f = ps.fields(float(t))
        temp_store = f["temperature"]
        for k in specs:
            v = temp_store if k == "temperature" else f[k]
            data[k].append(S.encode(np.round(v) if k in ("elevation", "ice", "temperature", "precipitation") else v, specs[k]))
        i, _, _ = ps._bracket(float(t))
        frames.append({"t": float(t), "stats": {**ps.stats(float(t)), "variability_c": round(f["noise_c"], 2)},
                       "omega": {}, "hotspots": src_frames[i].get("hotspots", []), "volcanoes": src_frames[i].get("volcanoes", [])})
    arrays = {k: np.stack(v) for k, v in data.items()}
    statics = {k: ps.run["layers"][k] for k in ("plate", "crust", "crust_age", "plate_boundary") if k in ps.run["layers"]}
    st = S.read_layers(ps.tz_dir, statics)
    arrays.update({k: np.asarray(v) for k, v in st.items()})
    specs.update(statics)
    run_id = S.new_id()
    out = S.path_of("run", run_id)
    layers = S.write_layers(out, arrays, specs)
    S.write_grid(g)
    label = name or f"recent {-ps.start:g} kyr: {ps.run['name']} @ {ps.now:g} kyr"
    S.write_json(out / "run.json", {
        "format": "procgen-run/2", "kind": "timezoom", "id": run_id, "name": label,
        "meta": {"kind": "timezoom", "phase": "recent", "time_unit": "kyr", **ps.meta(),
                 "kyr": round(-ps.start, 3), "step_kyr": ps.params.step, "every": ps.params.every,
                 "dt": ps.params.every, "myr": -ps.start / 1000.0, "frames": len(frames),
                 "seed": m.get("seed"), "level": g.level, "cells": g.n, "cell_size_km": round(g.spacing * R_KM),
                 "params": m.get("params", {}), "static_layers": list(statics),
                 "code": code_version(), "generated_in_s": round(time.time() - t0, 1),
                 "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{g.level}.json", "legend": S.legends(), "layers": layers,
        "events": events(ps), "frames": frames})
    report(out, ps)
    T.update_index()
    return out


def report(out: Path, ps: Pass) -> Path:
    m = ps.meta()
    lines = [f"# Recent pass {out.name}: last {-ps.start:g} kyr of time zoom {m['timezoom']} before {ps.now:g} kyr",
             f"source: {m['source_name']} @ {m['at_myr']} Myr; rain from {m['rain_from']}; seed {ps.params.seed}",
             f"steps {ps.params.step:g} kyr, frames every {ps.params.every:g} kyr", "", "## Episodes"]
    lines += [f"  {e['t']:>7.2f} kyr  {e['kind']:<13} {e['text']}  ({e['lat']}, {e['lon']})" for e in events(ps)] or ["  (none)"]
    lines += ["", "## Over time", "    t(kyr)  sea(m)  ice%  global_T  noise(C)"]
    for t in ps.frame_times()[::max(1, len(ps.frame_times()) // 30)]:
        s = ps.stats(float(t))
        k = int(np.clip(round((t - ps.start) / ps.params.step), 0, len(ps.noise) - 1))
        lines.append(f"  {t:>8.2f}  {s.get('sea_level_change_m', 0):>6.1f}  {s.get('ice_pct', 0):>4.1f}  "
                     f"{s.get('global_temp_c', 0):>8.2f}  {ps.noise[k]:>+6.2f}")
    path = out / "run.txt"
    S.write_atomic(path, "\n".join(lines) + "\n")
    return path


def resolve(ref: str) -> tuple[str, float | None, str | None]:
    """A time zoom id, or a finished world's id -> (time zoom, now kyr, world)."""
    if S.exists("run", ref):
        return ref, None, None
    if S.exists("world", ref.removesuffix(".json")):
        h = S.read_header(S.find_world(ref))
        tz = h["meta"].get("timezoom")
        if not tz:
            raise ValueError(f"world {ref} was not finished from a time zoom")
        return tz, float(h["meta"]["timezoom_kyr"]), h.get("id", ref.removesuffix(".json"))
    raise ValueError(f"no time zoom or world {ref!r}")
