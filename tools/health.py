"""Multi-seed health sweep (PW-246): many seeds, Earth-ish envelopes over time.

    uv run python tools/health.py                       # the full sweep: 8 L6 + 3 L7 seeds, 1 Gyr (~45 min)
    uv run python tools/health.py --quick               # L6 only, 500 Myr (~5 min)
    uv run python tools/health.py --l6 1 21 --l7 --myr 300 --workers 3 --threads 2
    uv run python tools/health.py --manifest docs/review/health/<date>/sweep.json   # re-report, no new runs
    uv run python tools/health.py ... --keep-runs       # don't delete the sweep's runs afterwards

Runs `planet simulate` for each seed (planet/parallel.simulate_many: worker
processes, --workers at once with --threads numba threads each; default
default params, `--every 4`), plus one short re-run of the first L6 seed
whose stored layers are hashed against the sweep's run (determinism). Then
reads each run's frame stats (run.json) and keyframe layers (store.py),
measures every keyframe (measure_frame), checks each measure against an
Earth-ish envelope (ENVELOPES, RUN_ENVELOPES), and writes
docs/review/health/<date>/report.md (per-seed tables, outliers by seed and
time window), sweep.json (the runs and every keyframe's measures) and small
thumbnail strips per seed. Prints a short summary.

The L6 runs are deleted afterwards (the L7 ones kept: they cost ~50 min
each) unless --keep-runs. `--manifest` re-measures and rewrites report.md
(hand-written notes in it are lost: keep them in a separate file or re-add).

The envelopes are deliberately wide: a planet built by simulation need not
be Earth, but a run that leaves them is worth a look. Each one gives Earth's
value and where the band comes from.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from planet import parallel  # noqa: E402
from planet import store as S  # noqa: E402
from planet import timeline as T  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools.scorecard import GROUP  # noqa: E402  (Koppen class -> main group letter)
from planet.tectonics.earth import CO2_MAX  # noqa: E402
from tools import ice_criteria  # noqa: E402

L6_SEEDS = [1, 2, 11, 21, 3199, 42, 77, 505]  # 21: plate collapse; 2, 11: cold eras; 1, 3199: references
L7_SEEDS = [3199, 21, 11]
DETERMINISM_MYR = 100.0
PEAK_KM = 9.5  # PW-172
GIANT_LAKE_MKM2 = 1.0  # overview 2.9: "open lakes over 1 million km2"
EARTH_KM2 = 4 * np.pi * R_KM ** 2

# metric: (low, high, Earth's value, label, source). None = no bound on that side.
ENVELOPES = {
    "land_pct": (22, 42, 29.2, "land, % of surface", "tests/test_envelopes.py (22-42%); Earth 29.2%"),
    "cont_pct": (33, 50, 41, "continental crust, % of surface",
                 "tests/test_envelopes.py (33-50%); Earth ~41% with shelves (Cogley 1984)"),
    "cont_km": (31, 40, 39, "mean continental crust thickness, km",
                "target 35 km (PW-238, continental_thickness); Earth ~39 km (Christensen & Mooney 1995); "
                "known thinning to 32-33 km (PW-046)"),
    "plates": (5, 30, 15, "plates", "tests/test_envelopes.py (5-30; max_plates 30); Earth 7 major + ~8 minor; "
               "<= 4 is the PW-191 collapse"),
    "ocean_age": (25, 120, 64, "mean ocean-floor age, Myr",
                  "tests/test_envelopes.py (25-120); Earth ~64 Myr (Mueller et al. 2008); PW-051"),
    "speed": (2, 9, 4.5, "mean plate speed, cm/yr", "tests/test_envelopes.py (2-9 cm/yr); Earth ~4-5"),
    "sea_level": (-250, 300, 0, "sea level, m (ice + ocean basins)",
                  "Phanerozoic ~-130 (LGM) .. +250 m (earth.py; Haq & Schutter 2008); -250: PW-240's hard goal"),
    "sea_ice_m": (-250, None, -0, "sea level from land ice, m",
                  "Earth LGM ~-130 m; PW-240 goal -150 m typical / -250 m worst"),
    "sea_tect_m": (-250, 300, 0, "sea level from the ocean basins, m (the other part of sea_level)",
                   "PW-293/549: the floor's mean depth against the start's; Phanerozoic ~-100..+250 m without the "
                   "ice (Haq & Schutter 2008; Mueller et al. 2008)"),
    "ice_pct": (None, 10, 3.1, "land ice, % of surface",
                "Earth 3.1% now (earth.EARTH_ICE), ~7-8% at the LGM"),
    "temp": (8, 30, 14.5, "global mean temperature, C",
             "Earth 14.5 C; LGM ~8 C (Tierney et al. 2020); Phanerozoic hothouses to ~30 C (Scotese et al. 2021)"),
    "co2": (-CO2_MAX, CO2_MAX, 0.0, "CO2 index (ln(source/sink) / WEATHER_CO2)", "the forcing's clip in earth.py (+-CO2_MAX = 3); Earth 0"),
    "dry_pct": (12, 45, 30, "arid (Koppen B), % of land",
                "tests/test_envelopes.py (12-45%); Earth ~30% (Beck et al. 2018)"),
    "inland_pct": (8, 30, 18, "land draining inland, % of ice-free land (to a closed lake, salt pan or real pit)",
                   "Earth ~18% (overview 2.9); L6 known ~9.5-11% (PW-054, PW-243). `inland_raw_pct` (not checked) "
                   "follows the stored `downstream` to any end, as highlights does; since PW-239 the two agree but for ends under land ice"),
    "lake_pct": (0.2, 3.0, 1.8, "lakes, % of land",
                 "Earth ~1.8% of ice-free land (HydroLAKES, Messager et al. 2016); generated L6 worlds 0.5-1%"),
    "lake_max_mkm2": (None, GIANT_LAKE_MKM2, 0.37, "largest lake, million km2",
                      "Caspian 0.37 Mkm2; 1 Mkm2 = the overview's giant lake (2.9)"),
    "max_elev_km": (None, PEAK_KM, 8.85, "highest peak, km", "Everest 8.85 km; PW-172 (spikes above ~9.5 km)"),
    "trees_pct": (10, 50, 30, "tree cover, % of ice-free land (after forests appear)",
                  "Earth ~30% potential canopy (forest 55-60 of ~130 Mkm2, overview 2.18)"),
    "npp": (200, 700, 430, "land NPP, g C/m2/yr (after flowering trees appear)",
            "Earth ~56 Pg C/yr over ~130 Mkm2 = ~430; the model on Earth's terrain 50 Pg C/yr, ~385 (overview 2.18). "
            "Before flowering trees (plant group 4) stand-ins grow at 70%, so runs sit at ~150-280"),
    "landmasses": (3, 80, None, "landmasses (>= 3 cells)", "loose: a lone supercontinent or a shattered archipelago"),
    "largest_pct": (5, 35, 16.6, "largest landmass, % of surface",
                    "Afro-Eurasia 16.6%; a Pangaea ~30% (scorecard largest_max)"),
}
SPINUP = 300.0  # Myr: the warm-up, not judged (owner 2026-10-21: the coupled systems settle; was 50, for hollows and rivers)
GATED = {"trees_pct": 3, "npp": 4}  # measured once that plant group exists (+ 20 Myr): forests; flowering trees
# per-run checks: (low, high, Earth, label, source)
RUN_ENVELOPES = {
    "dT_range": (None, 25, 25, "global temperature range over the run, C",
                 "Phanerozoic 11-36 C (Scotese et al. 2021)"),
    "peak_frames": (None, 0, 0, f"keyframes with a peak above {PEAK_KM} km", "PW-172 (L7 seed 3199: 3 of 251)"),
    "giant_lake_frames": (None, 5, 0, "% of keyframes with a lake over 1 Mkm2", "overview 2.9 (L6: 3 of ~150 frames)"),
    "volume_ratio": (0.9, 1.1, 1.0, "continental crust volume, end / start", "scorecard volume_ratio (x1.006)"),
    "sea_ice_below_150": (None, 10, 0, "% of keyframes with ice sea level below -150 m", "PW-240"),
    "low_plates": (None, 2, 0, "% of keyframes with <= 4 plates", "PW-191 (L7 seed 21: 1%)"),
}
MEASURE_LAYERS = ("elevation", "crust", "crust_thickness", "crust_age", "ice", "lake_depth", "lake_kind", "downstream",
                  "climate", "tree_cover", "npp")


# ---------------------------------------------------------------------------
# Running the sweep
# ---------------------------------------------------------------------------
def sweep_specs(l6, l7, myr, every, determinism: bool) -> list[dict]:
    tag = time.strftime("%Y-%m-%d")
    specs = [{"seed": s, "level": lv, "myr": myr, "every": every, "name": f"health {tag} seed {s} L{lv}"}
             for lv, seeds in ((7, l7), (6, l6)) for s in seeds]  # (L7 first: the longest jobs start first)
    if determinism and l6:
        # the plant groups' timeline is scaled to the run's length (flora_end): pin it to the sweep's
        specs.append({"seed": l6[0], "level": 6, "myr": min(DETERMINISM_MYR, myr), "every": every,
                      "set": {"flora_end": float(myr)}, "name": f"health {tag} seed {l6[0]} L6 determinism",
                      "determinism": True})
    return specs


def simulate(specs: list[dict], workers: int | None, threads: int | None) -> dict:
    """Runs the specs at once; returns the manifest ({"runs": [{spec..., "id"}], "seconds", ...})."""
    t0 = time.time()
    done = []

    def on_done(i, run_id):
        done.append(run_id)
        print(f"  [{time.time() - t0:7.0f}s] {specs[i]['name']}: run {run_id} ({len(done)}/{len(specs)})", flush=True)

    clean = [{k: v for k, v in s.items() if k != "determinism"} for s in specs]
    ids = parallel.simulate_many(clean, workers, threads, on_done=on_done)
    return {"date": time.strftime("%Y-%m-%d %H:%M"), "workers": workers, "threads": threads,
            "seconds": round(time.time() - t0), "runs": [{**s, "id": i} for s, i in zip(specs, ids)]}


# ---------------------------------------------------------------------------
# Measures (pure functions of one keyframe's decoded layers; tested at L4)
# ---------------------------------------------------------------------------
def drain_ends(down: np.ndarray, land: np.ndarray) -> np.ndarray:
    """Where each cell's water ends, following `downstream` over land (-1:
    here; a sea cell ends it) by pointer doubling: a sea cell, or a closed
    lake / pit on land."""
    nxt = np.where(land & (down >= 0), down, np.arange(len(down)))
    for _ in range(64):
        n2 = nxt[nxt]
        if np.array_equal(n2, nxt):
            break
        nxt = n2
    return nxt


def inland_share(down: np.ndarray, land: np.ndarray, free: np.ndarray, real_end: np.ndarray | None = None):
    """% of `free` (ice-free land) whose water ends on land (the same
    definition as highlights._inland_basins: the outlet isn't a sea mouth);
    with real_end, only ends where it is True count. None before the first
    rivers are routed."""
    if not free.any() or not (land & (down >= 0)).any():
        return None
    end = drain_ends(down, land)
    inland = land[end] if real_end is None else land[end] & real_end[end]
    return 100.0 * float((free & inland).sum()) / float(free.sum())


def real_hollows(grid, elev: np.ndarray, lake_kind: np.ndarray) -> np.ndarray:
    """Cells where water can really end on this terrain: closed lakes and
    salt pans (lake_kind 2, 3), and pits with no lower or sea neighbour.
    (Since PW-239 a run frame's `downstream` is routed on its own terrain,
    so this is a check that its ends do hold water.)"""
    nb_min = np.minimum.reduceat(elev[grid.nbr_idx], grid.nbr_off[:-1])
    return (lake_kind >= 2) | ((elev > 0) & (nb_min >= elev))


def _round(v, nd):
    return None if v is None else round(v, nd)


def measure_frame(grid, L: dict, stats: dict) -> dict:
    """The health measures of one keyframe: L holds decoded layers
    (MEASURE_LAYERS, real units), stats the frame's run.json stats."""
    n = grid.n
    cell_km2 = EARTH_KM2 / n
    elev = np.asarray(L["elevation"], float)
    land = elev > 0
    ice = np.asarray(L["ice"], float)
    free = land & (ice <= 0)
    cont = np.asarray(L["crust"]) > 0
    thick = np.asarray(L["crust_thickness"], float)
    age = np.asarray(L["crust_age"], float)
    lake = land & (np.asarray(L["lake_depth"], float) > 0)
    down = np.asarray(L["downstream"]).astype(np.int64)
    nland, nfree = max(1, int(land.sum())), max(1, int(free.sum()))
    lab, nl = grid.components(lake)
    lake_max = float(np.bincount(lab[lab >= 0]).max()) * cell_km2 / 1e6 if nl else 0.0
    vol_ice = (ice[land] / 1000.0).sum() * cell_km2  # km3
    ocean_km2 = max(1.0, float((~land).sum()) * cell_km2)
    return {
        "t": round(float(stats["t"]), 1),
        "land_pct": round(100 * float(land.mean()), 2),
        "cont_pct": round(100 * float(cont.mean()), 2),
        "cont_km": round(float(thick[cont].mean()), 2) if cont.any() else 0.0,
        "cont_volume": round(float((thick * cont).sum()) / n, 4),  # km of crust per cell, globally
        "plates": int(stats["plates"]),
        "ocean_age": round(float(age[~cont].mean()), 1) if (~cont).any() else 0.0,
        "speed": float(stats["mean_speed_cmyr"]),
        "sea_level": float(stats["sea_level_m"]),
        # (its two parts, PW-555: the run's own when its frame stats have them, else the ice's from the ice
        # layer as earth.update_climate counts it and the basins' as the rest)
        "sea_ice_m": float(stats["sea_ice_m"]) if "sea_ice_m" in stats else round(-0.9 * vol_ice / ocean_km2 * 1000.0, 1),
        "sea_tect_m": float(stats["sea_tect_m"]) if "sea_tect_m" in stats else
        round(float(stats["sea_level_m"]) + 0.9 * vol_ice / ocean_km2 * 1000.0, 1),
        "ice_pct": float(stats["ice_pct"]),
        "temp": float(stats["global_temp_c"]),
        "co2": float(stats["co2"]),
        "dry_pct": round(100 * float((GROUP[np.asarray(L["climate"])[land]] == "B").mean()), 2) if land.any() else 0.0,
        "inland_pct": _round(inland_share(down, land, free, real_hollows(grid, elev, np.asarray(L["lake_kind"]))), 2),
        "inland_raw_pct": _round(inland_share(down, land, free), 2),
        "lake_pct": round(100 * float(lake.sum()) / nland, 3),
        "lake_max_mkm2": round(lake_max, 3),
        "max_elev_km": round(float(elev.max()) / 1000.0, 2),
        "trees_pct": round(float(np.asarray(L["tree_cover"], float)[free].sum()) / nfree, 2),
        "npp": round(float(np.asarray(L["npp"], float)[free].sum()) / nfree, 1),
        "landmasses": int(stats["landmasses"]),
        "largest_pct": float(stats["largest_landmass_pct"]),
    }


def group_from(meta: dict, group: int = 3) -> float:
    """When plant group `group` appeared in the run (3: the first trees), + 20 Myr; inf if never."""
    for g in meta.get("plant_groups") or []:
        if g["group"] == group and g["t"] is not None:
            return float(g["t"]) + 20.0
    return float("inf")


def out_of(v: float, lo, hi) -> float:
    """How far v is outside [lo, hi] (0 inside; negative below)."""
    if lo is not None and v < lo:
        return v - lo
    if hi is not None and v > hi:
        return v - hi
    return 0.0


def windows(ts: list, vals: list, lo, hi, gap: int = 2) -> list[dict]:
    """Spells of keyframes outside [lo, hi]: [{t0, t1, frames, worst}],
    joining spells less than `gap` frames apart."""
    out, cur, last = [], None, -10
    for i, (t, v) in enumerate(zip(ts, vals)):
        if v is None or t < SPINUP or out_of(v, lo, hi) == 0:
            continue
        if cur is not None and i - last <= gap:
            cur["t1"], cur["frames"] = t, cur["frames"] + 1
            if abs(out_of(v, lo, hi)) > abs(out_of(cur["worst"], lo, hi)):
                cur["worst"] = v
        else:
            cur = {"t0": t, "t1": t, "frames": 1, "worst": v}
            out.append(cur)
        last = i
    return out


def measure_run(run_dir: Path) -> dict:
    """Every keyframe's measures and the run's own checks."""
    run, arr = T.load_frames(run_dir, MEASURE_LAYERS)
    m = run["meta"]
    grid = build_grid(m["level"])
    frames = []
    for i, fr in enumerate(run["frames"]):
        L = {k: T.frame(run, arr, k, i, grid) for k in MEASURE_LAYERS}
        frames.append(measure_frame(grid, L, fr["stats"]))
    gates = {k: group_from(m, grp) for k, grp in GATED.items()}
    for f in frames:
        for k, gate in gates.items():
            if f["t"] < gate:
                f[k] = None
    late = [f for f in frames if f["t"] >= SPINUP] or frames  # (the run checks skip the spin-up too)
    nf = len(late)
    temps = [f["temp"] for f in late]
    v0 = frames[0]["cont_volume"] or 1.0
    checks = {
        "dT_range": round(max(temps) - min(temps), 1),
        "peak_frames": sum(f["max_elev_km"] > PEAK_KM for f in late),
        "giant_lake_frames": round(100 * sum(f["lake_max_mkm2"] > GIANT_LAKE_MKM2 for f in late) / nf, 1),
        "volume_ratio": round(frames[-1]["cont_volume"] / v0, 3),
        "sea_ice_below_150": round(100 * sum(f["sea_ice_m"] < -150 for f in late) / nf, 1),
        "low_plates": round(100 * sum(f["plates"] <= 4 for f in late) / nf, 1),
    }
    # the whole-history ice-age criteria (PW-555, tools/ice_criteria.py: its own 100 Myr spin-up)
    track = [{"t": f["t"], "ice": f["sea_ice_m"], "tect": f["sea_tect_m"], "dT": f["temp"] - 14.5,
              "ice_frac": f["ice_pct"], "land": f["land_pct"]} for f in frames]
    ice = ice_criteria.evaluate({"track": track})
    checks["ice_old"] = "ok" if ice["old"]["pass"] else "F"
    checks["ice_new"] = "ok" if ice["pass"] else "F: " + "; ".join(ice["fails"])
    checks["icehouse_pct"] = ice["icehouse"]["share_pct"]
    return {"id": run["id"], "seed": m["seed"], "level": m["level"], "myr": m["myr"],
            "seconds": m.get("generated_in_s"), "forests_from": gates["trees_pct"], "flowers_from": gates["npp"],
            "checks": checks, "frames": frames}


def outliers(r: dict) -> list[dict]:
    """A run's spells outside the envelopes, with a severity for ranking
    (the excess as a share of the band's width, times the spell's share of the run)."""
    ts = [f["t"] for f in r["frames"]]
    out = []
    for k, (lo, hi, *_rest) in ENVELOPES.items():
        width = (hi if hi is not None else 0) - (lo if lo is not None else 0)
        width = abs(width) or abs(hi or lo or 1)
        for w in windows(ts, [f[k] for f in r["frames"]], lo, hi):
            sev = abs(out_of(w["worst"], lo, hi)) / width * (0.2 + w["frames"] / len(ts))
            out.append({"seed": r["seed"], "level": r["level"], "metric": k, **w, "severity": round(sev, 3)})
    for k, (lo, hi, *_rest) in RUN_ENVELOPES.items():
        v = r["checks"][k]
        if out_of(v, lo, hi):
            out.append({"seed": r["seed"], "level": r["level"], "metric": k, "t0": None, "t1": None,
                        "frames": None, "worst": v, "severity": round(abs(out_of(v, lo, hi)) / max(1.0, abs(hi or lo or 0)), 3)})
    return out


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def layer_hashes(run_dir: Path, frames: int) -> dict:
    """sha256 of each stored layer's first `frames` keyframes."""
    run, arr = T.load_frames(run_dir)
    return {k: hashlib.sha256(np.ascontiguousarray(a[:frames]).tobytes()).hexdigest()[:16] for k, a in arr.items()}


def determinism(full_dir: Path, short_dir: Path) -> dict:
    short = json.loads((short_dir / "run.json").read_text())
    full = json.loads((full_dir / "run.json").read_text())
    n = len(short["frames"])
    a, b = layer_hashes(full_dir, n), layer_hashes(short_dir, n)
    differ = sorted(k for k in b if a.get(k) != b[k])
    stats_differ = [s["stats"]["t"] for s, f in zip(short["frames"], full["frames"]) if s["stats"] != f["stats"]]
    return {"frames": n, "t_end": short["frames"][-1]["t"], "layers": len(b), "layers_differ": differ,
            "stats_differ_at": stats_differ, "identical": not differ and not stats_differ}


# ---------------------------------------------------------------------------
# Thumbnails
# ---------------------------------------------------------------------------
def thumbnail(grid, L: dict, idx: np.ndarray) -> np.ndarray:
    """A small satellite-like map: sea by depth, land by tree cover and dryness
    shaded by height, ice white, lakes blue. (h, w, 3) uint8."""
    e = np.asarray(L["elevation"], float)[idx]
    ice = np.asarray(L["ice"], float)[idx] > 0
    lake = np.asarray(L["lake_depth"], float)[idx] > 0
    q = lambda x, k: np.round(np.clip(x, 0, 1) * k) / k  # (a few colour steps: small PNGs)
    tree = q(np.asarray(L["tree_cover"], float)[idx] / 80.0, 4)[..., None]
    dry = (GROUP[np.asarray(L["climate"])[idx]] == "B")[..., None]
    deep, shelf = np.array([18, 38, 78.0]), np.array([52, 98, 150.0])
    sea = deep + (shelf - deep) * q(1 + e / 4000.0, 3)[..., None]
    bare = np.where(dry, np.array([196, 170, 120.0]), np.array([150, 140, 105.0]))
    green = np.array([48, 100, 40.0])
    landc = bare + (green - bare) * tree
    h = q(e / 5000.0, 4)[..., None]
    landc = landc + (np.array([120, 105, 95.0]) - landc) * h * 0.8
    img = np.where((e > 0)[..., None], landc, sea)
    img[lake & (e > 0)] = (40, 90, 160)
    img[ice & (e > 0)] = (240, 244, 248)
    return np.clip(img, 0, 255).astype(np.uint8)


def thumbnails(run_dir: Path, path: Path, times: list[float], width: int = 200) -> list[float]:
    """One PNG strip of the run at the keyframes nearest `times`; returns their times."""
    from planet.images import write_png
    from planet.world import nearest_cell_map
    names = ("elevation", "ice", "lake_depth", "tree_cover", "climate")
    run, arr = T.load_frames(run_dir, names)
    grid = build_grid(run["meta"]["level"])
    idx = nearest_cell_map(grid, width, width // 2)
    ft = np.array([f["t"] for f in run["frames"]])
    picks = [int(np.argmin(np.abs(ft - t))) for t in times]
    panels = []
    for i in picks:
        panels += [thumbnail(grid, {k: T.frame(run, arr, k, i, grid) for k in names}, idx),
                   np.full((width // 2, 3, 3), 255, np.uint8)]
    write_png(path, np.concatenate(panels[:-1], 1))
    return [float(ft[i]) for i in picks]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def _f(v, nd=1) -> str:
    if v is None:
        return "-"
    if isinstance(v, float) and np.isinf(v):
        return "never"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def _stat_row(vals: list) -> tuple:
    v = np.array([x for x in vals if x is not None], float)
    if not len(v):
        return None, None, None
    return float(np.min(v)), float(np.median(v)), float(np.max(v))


def report(manifest: dict, results: list[dict], det: dict | None, out_dir: Path, thumbs: dict) -> str:
    sweep = [r for r in results if not r.get("determinism")]
    allout = sorted((o for r in sweep for o in outliers(r)), key=lambda o: -o["severity"])
    md = [f"# Health sweep {manifest['date']}", "",
          f"Commit {manifest.get('commit', '?')}. {len(sweep)} runs (default params, `--every {sweep[0]['every']:g}`)"
          f" at {manifest.get('workers')} workers x {manifest.get('threads')} numba threads; "
          f"simulations {manifest['seconds'] / 60:.1f} min wall{manifest.get('load_note', '')}. "
          "Made by `tools/health.py` (PW-246).", ""]
    md += ["## Runs", "", "| seed | L | Myr | run | sim s | trees / flowering trees from | dT range C | peaks > 9.5 km | "
           "giant-lake frames % | crust volume end/start | ice SL < -150 m % | <= 4 plates % | ice bar old | "
           "ice bar new (ice-v2-criteria.md) | icehouse % |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sweep:
        c = r["checks"]
        md.append(f"| {r['seed']} | {r['level']} | {r['myr']:g} | {r['id']} | {_f(r['seconds'], 0)} | "
                  f"{_f(r['forests_from'], 0)} / {_f(r['flowers_from'], 0)} | {c['dT_range']} | {c['peak_frames']} | {c['giant_lake_frames']} | "
                  f"{c['volume_ratio']} | {c['sea_ice_below_150']} | {c['low_plates']} | {c.get('ice_old', '')} | "
                  f"{c.get('ice_new', '')} | {c.get('icehouse_pct', '')} |")
    keys = list(ENVELOPES)
    md += ["", f"## Medians by seed (after {SPINUP:g} Myr; tree cover after forests, NPP after flowering trees appear)", "",
           "| seed | L | " + " | ".join(keys) + " |", "|---|---|" + "---|" * len(keys)]
    for r in sweep:
        late = [f for f in r["frames"] if f["t"] >= SPINUP]
        md.append(f"| {r['seed']} | {r['level']} | " + " | ".join(_f(_stat_row([f[k] for f in late])[1], 1) for k in keys)
                  + " |")
    md += ["", "Measured on the run's keyframes (no slicing). A keyframe's rivers and lakes are routed on its own "
           "terrain (PW-239), so `inland_raw_pct` (every routed end on land, as highlights counts it) and `inland_pct` "
           "(ends that are closed lakes, salt pans or real pits) agree but for ends under land ice. Land ice and land "
           "shares use cells (near-equal area)."]
    md += ["", "## Envelopes", "", "| metric | low | high | Earth | source |", "|---|---|---|---|---|"]
    for k, (lo, hi, earth, label, src) in ENVELOPES.items():
        md.append(f"| {label} (`{k}`) | {_f(lo)} | {_f(hi)} | {_f(earth, 2)} | {src} |")
    for k, (lo, hi, earth, label, src) in RUN_ENVELOPES.items():
        md.append(f"| {label} (`{k}`, per run) | {_f(lo)} | {_f(hi)} | {_f(earth)} | {src} |")
    md += ["", f"## Top outliers (of {len(allout)} spells; severity = excess / band width x (0.2 + share of the run))",
           "", "| seed | L | metric | Myr | frames | worst | envelope | severity |", "|---|---|---|---|---|---|---|---|"]
    for o in allout[:30]:
        lo, hi = (ENVELOPES.get(o["metric"]) or RUN_ENVELOPES[o["metric"]])[:2]
        when = "run" if o["t0"] is None else f"{o['t0']:g}-{o['t1']:g}"
        md.append(f"| {o['seed']} | {o['level']} | {o['metric']} | {when} | {_f(o['frames'])} | {_f(o['worst'], 2)} | "
                  f"{_f(lo)}..{_f(hi)} | {o['severity']} |")
    md += ["", f"## Per seed: min / median / max after the {SPINUP:g} Myr spin-up, and spells outside the envelopes", ""]
    for r in sweep:
        md += [f"### Seed {r['seed']}, L{r['level']} (run {r['id']})", ""]
        if r["id"] in thumbs:
            p, ts = thumbs[r["id"]]
            md += [f"![seed {r['seed']} L{r['level']}]({p.name})", "",
                   f"*At {', '.join(f'{t:g}' for t in ts)} Myr: sea by depth, land green by tree cover / tan where "
                   "arid, shaded by height, ice white, lakes blue.*", ""]
        md += ["| metric | min | median | max | outside (Myr: worst) |", "|---|---|---|---|---|"]
        ts = [f["t"] for f in r["frames"]]
        for k, (lo, hi, *_rest) in ENVELOPES.items():
            vals = [f[k] for f in r["frames"]]
            a, b, c = _stat_row([v for v, t in zip(vals, ts) if t >= SPINUP])
            sp = windows(ts, vals, lo, hi)
            spells = "; ".join(f"{w['t0']:g}-{w['t1']:g}: {_f(w['worst'], 2)}" for w in sp[:4])
            if len(sp) > 4:
                spells += f"; +{len(sp) - 4} more"
            md.append(f"| {k} | {_f(a, 2)} | {_f(b, 2)} | {_f(c, 2)} | {spells} |")
        md.append("")
    md += ["## Determinism", ""]
    if det:
        md.append(f"Seed {det['seed']} L6 re-run to {det['t_end']:g} Myr (run {det['short']}) against the sweep's run "
                  f"{det['full']}: {det['frames']} keyframes x {det['layers']} layers, "
                  + ("**bit-identical** (layer hashes and frame stats)." if det["identical"] else
                     f"**differs**: layers {det['layers_differ']}, stats at {det['stats_differ_at'][:10]} Myr."))
    else:
        md.append("(not run)")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Multi-seed health sweep (PW-246)")
    ap.add_argument("--l6", type=int, nargs="*", default=L6_SEEDS, help="level-6 seeds")
    ap.add_argument("--l7", type=int, nargs="*", default=L7_SEEDS, help="level-7 seeds (none: --l7 alone)")
    ap.add_argument("--myr", type=float, default=1000.0)
    ap.add_argument("--every", type=float, default=4.0, help="Myr between keyframes")
    ap.add_argument("--workers", type=int, help="runs at once (default: all of them, up to a quarter of the cores)")
    ap.add_argument("--threads", type=int, default=2, help="numba threads per worker")
    ap.add_argument("--quick", action="store_true", help="L6 only, 500 Myr")
    ap.add_argument("--no-determinism", action="store_true")
    ap.add_argument("--manifest", type=Path, help="report on the runs of an earlier sweep.json (no new runs)")
    ap.add_argument("--out", type=Path, help="output folder (default docs/review/health/<date>)")
    ap.add_argument("--keep-runs", action="store_true", help="keep the runs (default: delete them, except L7)")
    ap.add_argument("--thumb-width", type=int, default=180)
    a = ap.parse_args()
    if a.quick:
        a.l7, a.myr = [], min(a.myr, 500.0)
    from planet.provenance import code_version
    code = code_version()
    if a.manifest:
        manifest = json.loads(a.manifest.read_text())
        for spec in manifest["runs"]:
            spec.setdefault("determinism", "determinism" in spec.get("name", ""))
    else:
        specs = sweep_specs(a.l6, a.l7, a.myr, a.every, not a.no_determinism)
        workers = a.workers or parallel.default_workers(len(specs))
        print(f"health: {len(specs)} runs, {workers} workers x {a.threads} threads", flush=True)
        manifest = simulate(specs, workers, a.threads)
        manifest["commit"] = f"{code['commit']}{'+dirty' if code['dirty'] else ''}"
    out = a.out or ROOT / "docs" / "review" / "health" / manifest["date"][:10]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    results = []
    for spec in manifest["runs"]:
        d = S.find_run(spec["id"])
        r = {**measure_run(d), "every": spec.get("every", 4.0), "determinism": spec.get("determinism", False)}
        results.append(r)
    det = None
    short = next((s for s in manifest["runs"] if s.get("determinism")), None)
    full = short and next((s for s in manifest["runs"] if not s.get("determinism") and s["seed"] == short["seed"]
                           and s["level"] == short["level"]), None)
    if short and full:
        det = {**determinism(S.find_run(full["id"]), S.find_run(short["id"])), "seed": short["seed"],
               "full": full["id"], "short": short["id"]}
    thumbs = {}
    for r in results:
        if r["determinism"]:
            continue
        p = out / f"seed{r['seed']}_L{r['level']}.png"
        times = [r["myr"] * f for f in (0.1, 0.4, 0.7, 1.0)]
        thumbs[r["id"]] = (p, thumbnails(S.find_run(r["id"]), p, times, a.thumb_width))
    md = report(manifest, results, det, out, thumbs)
    (out / "report.md").write_text(md)
    S.write_json(out / "sweep.json", {**manifest, "determinism": det,
                                      "results": [{k: v for k, v in r.items() if k != "frames"} for r in results]})
    (out / "frames.json.gz").write_bytes(gzip.compress(json.dumps(
        {r["id"]: r["frames"] for r in results}, separators=(",", ":")).encode(), 9))
    sweep = [r for r in results if not r["determinism"]]
    allout = sorted((o for r in sweep for o in outliers(r)), key=lambda o: -o["severity"])
    print(f"health: simulations {manifest['seconds']} s, measures {time.time() - t0:.0f} s -> {out}/report.md")
    for o in allout[:12]:
        when = "whole run" if o["t0"] is None else f"{o['t0']:g}-{o['t1']:g} Myr ({o['frames']} frames)"
        print(f"  seed {o['seed']} L{o['level']} {o['metric']}: {o['worst']} ({when})")
    if det:
        print(f"  determinism: {'identical' if det['identical'] else 'DIFFERS ' + str(det['layers_differ'])}")
    if not a.keep_runs and not a.manifest:
        from planet import store
        for spec in manifest["runs"]:
            if spec["level"] < 7:
                store.delete("run", spec["id"])
        print("  deleted the L6 runs (kept L7: " + " ".join(s["id"] for s in manifest["runs"] if s["level"] >= 7) + ")")


if __name__ == "__main__":
    main()
