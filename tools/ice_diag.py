"""Long-run ice and climate diagnostics (PW-555 stage 0): why a cold era does or doesn't end.

    uv run python tools/ice_diag.py --seed 11 [--myr 1000] [--level 6] [--out DIR] [--fields]
        [--moments 400 580] [--set k=v ...]
    uv run python tools/ice_diag.py --summary DIR/seed11_L6.json.gz [...]
    uv run python tools/ice_diag.py --plot DIR/seed11_L6.json.gz [...]     (PNG next to each file)
    uv run python tools/ice_diag.py --seed 1 --tect [--myr 2000] ...         (+ sea level and supercontinent channels)
    uv run python tools/ice_diag.py --run <run id> [--skip 300]             (a stored run's sea-level line)

Runs a simulation in memory (nothing goes to the store) with tectonics/diag.Recorder switched on, which
reads the run's state without changing it (the run is bit-identical to one without). Writes
DIR/seed<N>_L<l>.json.gz: per step the global temperature's parts (drift, CO2 term as counted and without levelling off,
ice albedo term, target), the CO2 source and sink against their baselines, sea level with its ice and
ocean-basin parts, the iced land; per climate update every sheet's budget (snow gained, melt, what the
sea takes, net), the frozen-sea share, the rain on the ice and the snowline land. --fields also writes
DIR/seed<N>_L<l>_fields.npz (ice, mass balance, warm month, rain per update, float16; ~60 MB per L6 Gyr).
--moments T ... pickles the time zoom's source (timezoom.source_from_sim, exact) at those times, for
tools/tz_mean.py and tools/ice_probe.py --source.

The summary prints the whole-history criteria (tools/ice_criteria.py: old and new bars) and, for each
deep cold era, what held it: the mean CO2 term (and how much its levelling off toward CO2_MAX withheld), the ice albedo
term, the drift, the sheets' net budget, and the volume of sheets the rule kept in deficit.

--tect (what tools/sealevel.py and tools/supercontinent.py measured; both folded in here, last present at
aae96637) also records, every step, the sea level's parts with land and crust %, the mean ocean depth and its
slow baseline, the ocean floor's mean age and its young (< 10 Myr) and capped-old (> 117 Myr) shares, the
ocean's share and the plate count (`tect`); every GEO_EVERY Myr the geography (`geo`: the largest landmass
and continental-crust mass, landmasses over 0.5%, plate speed, crust volume, the mantle under the largest
continent); and every rift, new margin and suture with its cause and its pieces' continental area
(`events`). The summary then adds a sea-level line (mean, sd, range, the 20 Myr swing, 4-point land drops,
steps at the sea_tect limiter, ocean age) and a supercontinent line (assemblies above 25% of the surface,
their spacing, landmass counts, rifts by cause); --plot draws the geography as a second PNG.
"""

from __future__ import annotations

import argparse
import gzip
import json
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planet  # noqa: E402,F401  (first: its thread caps)
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from planet.tectonics.diag import Recorder  # noqa: E402
from planet.tectonics.earth import CO2_MAX  # noqa: E402
from planet.tectonics.isostasy import ocean_depth  # noqa: E402
from planet.tectonics.plates import CMYR  # noqa: E402
from tools import ice_criteria as C  # noqa: E402


def parse_sets(kvs):
    sets = {}
    for kv in kvs:
        k, v = kv.split("=", 1)
        f = Params.__dataclass_fields__[k]
        sets[k] = v if f.type == "str" else (int(v) if f.type == "int" else bool(float(v)) if f.type == "bool" else float(v))
    return sets


# ---------------------------------------------------------------- --tect: sea level and the supercontinent cycle

TECT_EVENTS = ("rift", "subduction", "suture")
GEO_EVERY = 10.0  # Myr between geography samples
CLAMP = earth.SEA_TECT_MAX  # (the tanh limiter on sea_tect: a step "at" it is within 0.5 m)
ASSEMBLED = 25.0  # % of the surface: the largest landmass of an assembly


def tect_sample(sim) -> dict:
    ocean = ~sim.w_cont
    age = sim.w_age[ocean]
    return {
        "t": sim.t,
        "land": round(100 * float((sim.w_elev > 0).mean()), 2),
        "cont": round(100 * float(sim.w_cont.mean()), 2),
        "sl": round(float(sim.sea_level), 1),
        "ice": round(float(sim.sea_ice), 1),
        "tect": round(float(sim.sea_tect), 1),
        "depth": round(float(ocean_depth(age).mean()), 1) if age.size else 0.0,
        "depth_ref": round(float(sim.depth_ref), 1) if sim.depth_ref is not None else 0.0,
        "age": round(float(age.mean()), 1) if age.size else 0.0,
        "young": round(100 * float((age < 10).mean()), 2) if age.size else 0.0,
        "old": round(100 * float((age > 117).mean()), 2) if age.size else 0.0,
        "ocean": round(100 * float(ocean.mean()), 2),
        "plates": int(sim.plates.alive.sum()),
    }


def geo_sample(sim, v0) -> dict:
    g = sim.grid
    land = sim.w_elev > 0
    lab, nl = g.components(land)
    sizes = np.bincount(lab[lab >= 0]) if nl else np.zeros(1, int)
    clab, ncl = g.components(sim.w_cont)
    csizes = np.bincount(clab[clab >= 0]) if ncl else np.zeros(1, int)
    big = clab == int(csizes.argmax()) if ncl else np.zeros(g.n, bool)
    v = np.linalg.norm(sim.velocity(), axis=1) * CMYR
    rec = {
        "t": sim.t,
        "largest": round(100 * sizes.max() / g.n, 2),
        "largest_cont": round(100 * csizes.max() / g.n, 2),
        "masses": int((sizes > 0.005 * g.n).sum()),
        "land": round(100 * land.mean(), 2),
        "speed": round(float(v.mean()), 2),
        "ocean_age": round(float(sim.w_age[~sim.w_cont].mean()), 1),
        "plates": int(sim.plates.alive.sum()),
        "volume": round(float((sim.w_thick * sim.w_cont).sum()) / v0, 4),
        "max_elev": int(sim.w_elev.max()),
        "elev_p99": int(np.percentile(sim.w_elev[land], 99)) if land.any() else 0,
    }
    m = getattr(sim, "mantle", None)
    if m is not None:
        rec["mantle_under"] = round(float(m[big].mean()), 3) if big.any() else 0.0
        rec["mantle_cont"] = round(float(m[sim.w_cont].mean()), 3)
        rec["mantle_min"] = round(float(m.min()), 3)
        rec["mantle_max"] = round(float(m.max()), 3)
    return rec


def rift_cause(e, mantle: bool) -> str:
    """margin (new subduction), suture, or for rifts: without a mantle field heat / stress; with it, a
    continental rift over warm / cold / neutral mantle (cont-warm, cont-cold, cont) or an oceanic plate
    split (plate, plate-warm, plate-cold)."""
    if e.kind in ("subduction", "suture"):
        return "margin" if e.kind == "subduction" else "suture"
    if not mantle:
        return "heat" if "rifts apart" in e.text else "stress"
    kind = "cont" if e.text.startswith("continent") else "plate"
    for side in ("warm", "cold"):
        if f"{side} mantle" in e.text:
            return f"{kind}-{side}"
    return kind


class Tect:
    """Reads the run like Recorder: per step tect_sample, every GEO_EVERY Myr geo_sample, and the events."""

    def __init__(self, sim):
        self.v0 = float((sim.w_thick * sim.w_cont).sum())
        self.mantle = getattr(sim, "mantle", None) is not None
        self.seen = len(sim.events)
        self.tect, self.geo, self.events = [tect_sample(sim)], [geo_sample(sim, self.v0)], []

    def step(self, s):
        for e in s.events[self.seen:]:
            if e.kind in TECT_EVENTS:
                slots = {int(s.plates.label[k]): k for k in np.flatnonzero(s.plates.alive)}
                pieces = [round(100 * float((s.w_cont & (s.owner == slots[lb])).mean()), 2) if lb in slots else 0
                          for lb in e.plates]
                self.events.append({"t": e.t, "kind": e.kind, "cause": rift_cause(e, self.mantle), "pieces": pieces})
        self.seen = len(s.events)
        self.tect.append(tect_sample(s))
        if abs(s.t / GEO_EVERY - round(s.t / GEO_EVERY)) < 1e-6:
            self.geo.append(geo_sample(s, self.v0))

    def as_dict(self) -> dict:
        return {"tect": self.tect, "geo": self.geo, "events": self.events}


def from_run(run_id: str) -> dict:
    """A stored run's keyframes as a `tect` record (land, sea level and its parts, plates)."""
    d = json.loads((ROOT / "runs" / run_id / "run.json").read_text())
    tr = [{"t": f["t"], "land": f["stats"]["land_pct"], "sl": f["stats"]["sea_level_m"], "ice": f["stats"]["sea_ice_m"],
           "tect": f["stats"]["sea_tect_m"], "plates": f["stats"]["plates"]} for f in d["frames"]]
    return {"seed": d["meta"].get("seed"), "run": run_id, "level": d["meta"].get("level"), "tect": tr}


def sea_stats(d, skip: float = 0.0, every: float = 4.0, window: float = 20.0, drop: float = 4.0) -> dict:
    """Sea level on `every` Myr samples after `skip`: mean, sd, range, the largest change within `window` Myr,
    'land drops' (land falls by `drop` points of the surface within `window`; consecutive flags count once),
    the share below -150 / -430 m of sea level from ice, steps at the sea_tect limiter, ocean age, plates."""
    tr = [r for r in d["tect"] if r["t"] >= skip - 1e-9 and abs(r["t"] / every - round(r["t"] / every)) < 1e-6]
    t = np.array([r["t"] for r in tr])
    L = np.array([r["land"] for r in tr])
    s = np.array([r["sl"] for r in tr])
    k = int(round(window / every))
    flag = np.array([i + 1 < len(L) and L[i + 1:i + k + 1].min() <= L[i] - drop for i in range(len(L))])
    drops = int(flag[0]) + int((flag[1:] & ~flag[:-1]).sum()) if len(flag) else 0
    swing = max((np.abs(s[i + 1:i + k + 1] - s[i]).max() for i in range(len(s) - 1)), default=0.0)
    si = np.array([r["ice"] for r in tr])
    te = np.array([r["tect"] for r in tr])
    p = np.array([r["plates"] for r in tr])
    out = {"n": len(tr), "sl_mean": round(float(s.mean())), "sl_sd": round(float(s.std())),
           "sl_min": round(float(s.min())), "sl_max": round(float(s.max())), "swing20": round(float(swing)),
           "land_drops": drops, "drop_times": [float(x) for x in t[flag & np.concatenate([[True], ~flag[:-1]])]],
           "land_min": float(L.min()), "land_max": float(L.max()),
           "below150": round(100 * float((si < -150).mean()), 1), "below430": round(100 * float((si < -430).mean()), 1),
           "ice_mean": round(float(si.mean())), "ice_min": round(float(si.min())),
           "clamp": int((np.abs(te) >= CLAMP - 0.5).sum()), "tect_sd": round(float(te.std())),
           "plates_median": float(np.median(p)), "plates_min": int(p.min())}
    if "age" in tr[0]:
        ages = np.array([r["age"] for r in tr])
        out["age_mean"], out["age_sd"] = round(float(ages.mean()), 1), round(float(ages.std()), 1)
    return out


def sea_line(d, skip=0.0) -> str:
    st = sea_stats(d, skip)
    name = f"run {d['run']}" if d.get("run") else f"seed {d['seed']} L{d['level']}"
    age = f", ocean age {st['age_mean']}+-{st['age_sd']}" if "age_mean" in st else ""
    return (f"{name} sea level (>= {skip:g} Myr) {st['sl_mean']}+-{st['sl_sd']} m [{st['sl_min']}, {st['sl_max']}],"
            f" from ice mean {st['ice_mean']} (min {st['ice_min']}), below -150 / -430 m {st['below150']}% /"
            f" {st['below430']}%; 20-Myr swing max {st['swing20']} m; land {st['land_min']}-{st['land_max']}%,"
            f" 4-pt land drops {st['land_drops']} {st['drop_times']}; sea_tect sd {st['tect_sd']}, at the limiter"
            f" {st['clamp']} samples{age}; plates median {st['plates_median']:g} min {st['plates_min']}")


def assemblies(geo, thr=ASSEMBLED, gap=100.0):
    """[start, end, peak] of spells with the largest landmass >= thr; spells under `gap` Myr apart are one."""
    out = []
    for r in geo:
        if r["largest"] >= thr:
            if out and r["t"] - out[-1][1] <= gap:
                out[-1][1] = r["t"]
                out[-1][2] = max(out[-1][2], r["largest"])
            else:
                out.append([r["t"], r["t"], r["largest"]])
    return out


def geo_line(d, thr=ASSEMBLED) -> str:
    tr = d["geo"]
    late = [r for r in tr if r["t"] >= 200] or tr
    asm = assemblies(tr, thr)
    starts = [a[0] for a in asm]
    gaps = np.diff(starts).tolist() if len(starts) > 1 else []
    masses = [r["masses"] for r in late]
    between = [r["masses"] for r in late if r["largest"] < 20] or [0]
    rifts = [e for e in d["events"] if e["kind"] != "suture"]
    causes = {}
    for e in rifts:
        causes[e["cause"]] = causes.get(e["cause"], 0) + 1
    small = sum(1 for e in rifts if e["kind"] == "rift" and any(0.3 < x < 3.0 for x in e["pieces"]))
    return (f"supercontinent: assemblies>{thr:g}% at {[f'{a:g}-{b:g} ({c:.0f}%)' for a, b, c in asm]} gaps {gaps};"
            f" largest max {max(r['largest'] for r in tr):.1f}% median {np.median([r['largest'] for r in late]):.1f}%;"
            f" masses>0.5% median {np.median(masses):.0f} (range {min(masses)}-{max(masses)}; dispersed, largest<20%:"
            f" {np.median(between):.0f}); volume x{tr[-1]['volume']}; ocean age median"
            f" {np.median([r['ocean_age'] for r in late]):.0f}; speed median {np.median([r['speed'] for r in late]):.2f};"
            f" rifts {causes} (continental pieces <3%: {small});"
            f" sutures {sum(1 for e in d['events'] if e['kind'] == 'suture')}")


def run(seed, myr, level, sets, out: Path, fields=False, moments=(), tect=False):
    from planet import timezoom as Z
    sets = {"run_end": float(myr), **sets}  # (as timeline.simulate: the run's end is now)
    sim = Simulation(build_grid(level), seed, Params(**sets), 2.0)
    sim.diag = Recorder(fields=fields)
    tk = Tect(sim) if tect else None
    todo = sorted(float(m) for m in moments)
    tag = f"seed{seed}_L{level}"
    t0 = time.time()

    def on_step(s):
        s.diag.step(s)
        if tk is not None:
            tk.step(s)
        while todo and s.t >= todo[0] - 1e-9:
            src = Z.source_from_sim(s, f"seed {seed} L{level} @ {s.t:g} Myr")
            src = {k: v for k, v in src.items() if k != "grid"}
            src["sea_ice_run"], src["sea_tect_run"] = float(s.sea_ice), float(s.sea_tect)
            (out / f"{tag}_at{s.t:g}.pkl").write_bytes(pickle.dumps(src))
            todo.pop(0)
        if int(s.t) % 100 == 0 and abs(s.t - round(s.t)) < 1e-9:
            print(f"  {tag} {s.t:g} Myr  {time.time() - t0:.0f} s  ice {s.sea_ice:.0f} m  dT {s.dT:+.1f}", flush=True)

    sim.run(myr, on_step)
    d = {"seed": seed, "myr": myr, "level": level, "params": sets, "seconds": round(time.time() - t0),
         **sim.diag.as_dict(), **(tk.as_dict() if tk is not None else {})}
    path = out / f"{tag}.json.gz"
    with gzip.open(path, "wt") as f:
        json.dump(d, f)
    if fields:
        sim.diag.save_fields(out / f"{tag}_fields.npz")
    return path


def eras(d: dict, below: float = C.DEEP) -> list[dict]:
    """Each deep cold era (sea level from ice below `below`, after the spin-up) and what held it."""
    st = [r for r in d["steps"] if r["t"] >= C.SPINUP]
    up = {round(u["t"], 3): u for u in d["updates"]}
    t = np.array([r["t"] for r in st])
    si = np.array([r["sea_ice"] for r in st])
    out = []
    for a, b in C.spells(t, si < below):
        rows = [r for r in st if a <= r["t"] <= b]
        us = [up[k] for k in sorted(up) if a <= k <= b and "budget" in up[k]]
        m = lambda k: round(float(np.mean([r[k] for r in rows])), 2)
        e = {"t0": a, "t1": b, "myr": b - a + C.EVERY, "worst": round(min(r["sea_ice"] for r in rows)),
             "dT": m("dT_end"), "drift": m("drift"), "co2": m("co2"), "co2_term": m("co2_term"),
             "co2_withheld": round(m("co2_term_free") - m("co2_term"), 2), "albedo": m("albedo_term"),
             "sink": m("sink"), "src": m("src"), "iced_land": m("iced_land"),
             "clipped_pct": round(100 * float(np.mean([abs(r["co2"]) >= CO2_MAX / 2 for r in rows])), 0)}
        if us:
            e["net"] = round(float(np.mean([u["budget"]["net"] for u in us])), 3)
            e["deficit_vol"] = round(float(np.mean([u["budget"]["deficit_vol_m"] for u in us])))
            e["sea_frozen"] = round(float(np.mean([u["sea_frozen"] for u in us])), 3)
            e["precip_ice"] = round(float(np.mean([u["precip_ice"] for u in us])))
            e["lat_min"] = round(float(np.min([u["iced_lat_min"] for u in us if u["iced_lat_min"] is not None])), 1)
        out.append(e)
    return out


FB_BAND = (0.35, 0.9)  # C of CO2 warming per C of cooling: the thermostat's bar (PW-574; owner 2026-10-22, PW-576 C:
# ~0.35-0.5 is close enough, the sink's own answer)
TREND_MYR = 200.0  # Myr: the running mean taken out of every series for the high-passed gain


def gain(d: dict, spinup: float = C.SPINUP) -> dict | None:
    """The CO2 thermostat's gain after the spin-up (PW-572), by regression over the steps:
      g          d ln(sink)/dT, holding the land share fixed (sea level and tectonics move the land
                 independently of the climate; the review's thermo2): how hard the sink answers warmth
      fb         the CO2 warming per C of cooling it gives: co2_sensitivity / ln 2 x g / the sink's CO2 log-slope
      g_raw      the same slope without the land control
      parts      d ln(part)/dT of each part of the sink (they add up to g_raw): the erosion supply from the
                 ice-free land, the temperature factor, the plant factor (and the saturation's efficiency,
                 sink / supply, if logged); the ice-free land's area is shown beside them (it is in the supply)
      dT_drift   d dT / d drift: how much of the random drift reaches dT (1 = no brake)
      corr       corr(CO2 term, dT): negative = the CO2 term pushes against dT
      corr_src   the same with the volcanic source's part taken out (CO2 term and dT regressed on ln src)
    None for runs recorded before the sink's parts were logged."""
    from planet.tectonics import Params
    # the sink's CO2 log-slope (earth.co2_slope, logged as w_a; 0.4 before v1-finish-11's co2_law)
    WEATHER_CO2 = float(np.nanmedian([r.get("w_a") or np.nan for r in d["steps"] if r["t"] >= spinup] or [0.4]))
    if not np.isfinite(WEATHER_CO2):
        WEATHER_CO2 = 0.4
    st = [r for r in d["steps"] if r["t"] >= spinup and r.get("w_supply") and r.get("sink_raw", 0) > 0]
    if len(st) < 20 or "w_temp" not in st[0]:
        return None
    f = lambda k: np.array([r[k] if r.get(k) is not None else np.nan for r in st], float)
    dT, land, co2t, drift = f("dT"), f("land"), f("co2_term"), f("drift")
    ok = np.isfinite(f("w_temp")) & np.isfinite(f("w_plant"))
    ln = {"sink": np.log(f("sink_raw")), "area": np.log(f("w_area")), "supply": np.log(f("w_supply")),
          "temp": np.log(f("w_temp")), "plant": np.log(f("w_plant"))}
    if "w_eff" in st[0]:
        ln["eff"] = np.log(f("w_eff"))
    one = np.ones(ok.sum())
    slope = lambda y: float(np.polyfit(dT[ok], y[ok], 1)[0])
    g = float(np.linalg.lstsq(np.c_[dT[ok], land[ok], one], ln["sink"][ok], rcond=None)[0][0])
    sens = d.get("params", {}).get("co2_sensitivity", Params().co2_sensitivity) / np.log(2.0)  # C per e-fold
    lsrc = np.log(f("src"))[ok]
    res_c = co2t[ok] - np.polyval(np.polyfit(lsrc, co2t[ok], 1), lsrc)
    res_t = dT[ok] - np.polyval(np.polyfit(lsrc, dT[ok], 1), lsrc)
    # Instrumented on the drift. The drift is random and knows nothing of the geography, whereas the regressions
    # above mix the gain with the thermostat's own answer to geography (a sink on cold ground lowers the sink,
    # raises CO2 and warms the planet: a negative correlation by construction). iv(y) = cov(y, drift) / cov(dT, drift).
    cd = float(np.cov(dT, drift)[0, 1])
    iv = lambda y: float(np.cov(y[ok], drift[ok])[0, 1]) / cd
    lrel = np.log(f("sink"))
    # The same with each series' TREND_MYR running mean taken out: a kept reference lets a slow trend (the start's
    # relief building up, a drifting source) move the CO2 term, and over ~700 Myr such a trend lines up with the
    # drift's slowest wander by chance; the high-passed answer is the thermostat's on the drift's own time scale.
    n = max(1, int(round(TREND_MYR / 2 / max(float(np.median(np.diff(f("t")))), 1e-9))))
    def hp(y):
        pad = np.r_[np.full(n, y[:n].mean()), y, np.full(n, y[-n:].mean())]
        return y - np.convolve(pad, np.ones(2 * n + 1) / (2 * n + 1), "same")[n:-n]
    dh = hp(drift)
    cdh = float(np.cov(hp(dT)[ok], dh[ok])[0, 1])
    ivh = lambda y: float(np.cov(hp(y)[ok], dh[ok])[0, 1]) / cdh
    inst = {"co2_hp": round(-ivh(co2t), 2), "fb_hp": round(sens * ivh(ln["sink"]) / WEATHER_CO2, 2),
            "g": round(iv(ln["sink"]), 4), "fb": round(sens * iv(ln["sink"]) / WEATHER_CO2, 2),
            "fb_rel": round(sens * iv(lrel) / WEATHER_CO2, 2), "co2": round(-iv(co2t), 2),
            "parts": {k: round(iv(v), 4) for k, v in ln.items() if k not in ("sink", "area")}}
    return {"iv": inst, "g": round(g, 4), "fb": round(sens * g / WEATHER_CO2, 2), "g_raw": round(slope(ln["sink"]), 4),
            "parts": {k: round(slope(v), 4) for k, v in ln.items() if k != "sink"},
            "dT_drift": round(float(np.polyfit(drift, dT, 1)[0]), 2),
            "corr": round(float(np.corrcoef(co2t, dT)[0, 1]), 2),
            "corr_src": round(float(np.corrcoef(res_c, res_t)[0, 1]), 2),
            "T_local": round(slope(f("w_T")), 2), "rate": round(float(np.nanmedian(f("w_rate"))), 4)}


def gain_line(k: dict | None) -> str:
    if k is None:
        return "thermostat -- (no sink parts in this file; re-run with the current ice_diag)"
    pa = " ".join(f"{a} {v:+.3f}" for a, v in k["parts"].items())
    v = k["iv"]
    pv = " ".join(f"{a} {x:+.3f}" for a, x in v["parts"].items())
    return (f"thermostat (on the drift, {TREND_MYR:g} Myr trends out) CO2 {v['co2_hp']:+.2f} C per C of cooling "
            f"{'ok' if FB_BAND[0] <= v['co2_hp'] <= FB_BAND[1] else 'F'} (sink fb {v['fb_hp']:+.2f}); with the trends"
            f" CO2 {v['co2']:+.2f}; the sink answers {v['g']:+.3f}/C ({pv}) = fb "
            f"{v['fb']:+.2f}, {v['fb_rel']:+.2f} against the references\n"
            f"      regressions: fb {k['fb']:+.2f} C/C"
            f" (d ln sink/dT {k['g']:+.3f} with land fixed, {k['g_raw']:+.3f} raw; per part {pa}; local T {k['T_local']:.2f}"
            f"/C of dT), dT/drift {k['dT_drift']:.2f}, corr(CO2 term, dT) {k['corr']:+.2f} ({k['corr_src']:+.2f} without"
            f" the source), median erosion {1000 * k['rate']:.1f} m/Myr")


def summary(path, skip=0.0):
    d = C.load(path)
    r = C.evaluate(d)
    print(C.line(Path(path).name.split(".")[0], r))
    k = gain(d)
    print("    " + gain_line(k))
    if d.get("tect"):
        print("    " + sea_line(d, skip))
    if d.get("geo"):
        print("    " + geo_line(d))
    for e in eras(d):
        print(f"    era {e['t0']:g}-{e['t1']:g} ({e['myr']:g} Myr) worst {e['worst']} m: dT {e['dT']:+.1f} = drift "
              f"{e['drift']:+.1f} + CO2 {e['co2_term']:+.1f} (index {e['co2']:+.2f}, beyond CO2_MAX / 2 {e['clipped_pct']:g}% of"
              f" steps, withheld {e['co2_withheld']:+.1f}) + albedo {e['albedo']:+.1f}; sink x{e['sink']} src x{e['src']},"
              f" iced land {100 * e['iced_land']:.0f}%; sheets net {e.get('net')} m/kyr, in deficit {e.get('deficit_vol')} m;"
              f" frozen sea {e.get('sea_frozen')}, snow on ice {e.get('precip_ice')} mm, ice to {e.get('lat_min')} deg")
    return r, k


def plot(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = C.load(path)
    st = d["steps"]
    t = np.array([r["t"] for r in st])
    f = lambda k: np.array([r[k] for r in st], float)
    fig, ax = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
    ax[0].plot(t, f("sea_ice"), label="sea level from ice", color="#2a6fdb")
    ax[0].plot(t, f("sea_tect"), label="ocean-basin term", color="#999999")
    for y in (C.DEEP, C.VDEEP):
        ax[0].axhline(y, color="#cc4444", lw=0.6, ls="--")
    ax[0].set_ylabel("m"); ax[0].legend(loc="lower left", fontsize=8)
    ax[1].plot(t, f("dT_end"), label="dT", color="black")
    ax[1].plot(t, f("drift"), label="drift", color="#888888", lw=0.8)
    ax[1].plot(t, f("co2_term"), label="CO2 term (counted)", color="#d08a1a")
    ax[1].plot(t, f("co2_term_free"), label="CO2 term (without levelling off)", color="#d08a1a", lw=0.6, ls=":")
    ax[1].plot(t, f("albedo_term"), label="ice albedo term", color="#2a6fdb", lw=0.8)
    ax[1].set_ylabel("C"); ax[1].legend(loc="lower left", fontsize=8, ncol=3)
    ax[2].semilogy(t, np.maximum(f("sink"), 1e-3), label="weathering sink / reference", color="#3a9a4a")
    ax[2].semilogy(t, np.maximum(f("src"), 1e-3), label="volcanic source / reference", color="#b04040")
    ax[2].legend(loc="lower left", fontsize=8)
    up = [u for u in d["updates"] if "budget" in u]
    if up:
        tu = [u["t"] for u in up]
        for k, c in (("acc", "#2a6fdb"), ("melt", "#d04040"), ("sea", "#7a4ab0"), ("net", "black")):
            ax[3].plot(tu, [u["budget"][k] for u in up], label=k, color=c, lw=0.9)
        ax[3].plot(tu, [u["budget"]["deficit_vol_m"] / 100 for u in up], label="ice in deficit sheets (100 m)",
                   color="#999999", lw=0.8, ls="--")
    ax[3].set_ylabel("m sea level / kyr"); ax[3].legend(loc="lower left", fontsize=8, ncol=3)
    ax[3].set_xlabel("Myr")
    for a in ax:
        a.axvspan(0, C.SPINUP, color="#eeeeee", zorder=-1)
    fig.suptitle(f"seed {d['seed']} L{d['level']} {d['myr']:g} Myr: ice, temperature terms, CO2, sheet budgets")
    fig.tight_layout()
    png = Path(str(path).replace(".json.gz", ".png"))
    fig.savefig(png, dpi=90)
    print(png)
    if d.get("geo"):
        plot_geo(d, Path(str(path).replace(".json.gz", "_geo.png")))


def plot_geo(d, png: Path):
    import matplotlib.pyplot as plt
    tr = d["geo"]
    t = np.array([r["t"] for r in tr])
    has_m = "mantle_under" in tr[0]
    fig, ax = plt.subplots(4 if has_m else 3, 1, figsize=(10, 11 if has_m else 8.5), sharex=True)
    a = ax[0]
    a.plot(t, [r["largest"] for r in tr], color="#1f6f8b", label="largest landmass (% surface)")
    a.plot(t, [r["largest_cont"] for r in tr], color="#99c1b9", lw=1, label="largest continental-crust mass")
    a.axhline(ASSEMBLED, color="#c44", lw=0.8, ls="--")
    a.set_ylabel("% of surface")
    a.legend(loc="upper right", fontsize=8)
    a.set_title(f"seed {d['seed']}, level {d['level']}  {d.get('params') or ''}")
    a = ax[1]
    a.plot(t, [r["masses"] for r in tr], color="#444", label="landmasses > 0.5%")
    a.axhspan(5, 15, color="#9c9", alpha=0.2)
    a.set_ylabel("count")
    a.legend(loc="upper right", fontsize=8)
    a = ax[2]
    a.plot(t, [r["land"] for r in tr], label="land %")
    a.plot(t, [r["speed"] * 5 for r in tr], label="mean speed x5 (cm/yr)")
    a.plot(t, [r["ocean_age"] / 2 for r in tr], label="ocean age / 2 (Myr)")
    a.plot(t, [r["plates"] for r in tr], label="plates")
    colors = {"heat": "#d62728", "stress": "#ff7f0e", "margin": "#2ca02c", "suture": "#8c564b",
              "cont-warm": "#d62728", "cont": "#ff7f0e", "cont-cold": "#1f77b4"}
    for e in d["events"]:
        sut = e["kind"] == "suture"
        a.axvline(e["t"], ymin=0.93 if sut else 0.0, ymax=1.0 if sut else 0.07, color=colors.get(e["cause"], "#7f7f7f"),
                  lw=1)
    a.legend(loc="upper right", fontsize=8, ncol=2)
    a.set_ylabel("rifts (bottom ticks) / sutures (top)")
    if has_m:
        a = ax[3]
        a.plot(t, [r["mantle_under"] for r in tr], color="#b22", label="mantle under largest continent")
        a.plot(t, [r["mantle_cont"] for r in tr], color="#e88", lw=1, label="mantle under all continent")
        a.fill_between(t, [r["mantle_min"] for r in tr], [r["mantle_max"] for r in tr], color="#ccc", alpha=0.4,
                       label="mantle min..max")
        a.axhline(0, color="k", lw=0.5)
        a.set_ylabel("mantle T anomaly")
        a.legend(loc="upper right", fontsize=8)
    ax[-1].set_xlabel("Myr")
    fig.tight_layout()
    fig.savefig(png, dpi=90)
    print(png)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, nargs="*", default=[])
    ap.add_argument("--myr", type=float, default=1000)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--out", default="ice_diag_out")
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--fields", action="store_true")
    ap.add_argument("--moments", type=float, nargs="*", default=[])
    ap.add_argument("--tect", action="store_true", help="also record sea level, geography and rifts (see above)")
    ap.add_argument("--summary", nargs="*")
    ap.add_argument("--plot", nargs="*")
    ap.add_argument("--run", nargs="*", default=[], help="stored run ids: print their sea-level line")
    ap.add_argument("--skip", type=float, default=0.0, help="Myr left out of the sea-level line")
    a = ap.parse_args()
    for r in a.run:
        print(sea_line(from_run(r), a.skip))
    rows = [summary(p, a.skip) for p in a.summary or []]
    ks = [k for _, k in rows if k is not None]
    if len(rows) > 1:
        print(f"{len(rows)} runs: criteria N1-N4 pass on {sum(r['pass'] for r, _ in rows)}"
              + (f"; thermostat fb (trends out) in {FB_BAND[0]:g}-{FB_BAND[1]:g} C/C on {sum(FB_BAND[0] <= k['iv']['co2_hp'] <= FB_BAND[1] for k in ks)}"
                 f" of {len(ks)} (median {np.median([k['iv']['co2_hp'] for k in ks]):+.2f}, with trends {np.median([k['iv']['co2'] for k in ks]):+.2f}; the sink's own fb {np.median([k['iv']['fb_hp'] for k in ks]):+.2f}), CO2 term against drift-made dT on {sum(k['iv']['co2_hp'] > 0 for k in ks)}, corr(CO2 term, dT) < 0 on"
                 f" {sum(k['corr'] < 0 for k in ks)} (without the source {sum(k['corr_src'] < 0 for k in ks)})" if ks else ""))
    for p in a.plot or []:
        plot(p)
    out = Path(a.out)
    for s in a.seed:
        out.mkdir(parents=True, exist_ok=True)
        summary(run(s, a.myr, a.level, parse_sets(a.set), out, a.fields, a.moments, a.tect), a.skip)


if __name__ == "__main__":
    main()
