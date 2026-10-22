"""Long-run ice and climate diagnostics (PW-555 stage 0): why a cold era does or doesn't end.

    uv run python tools/ice_diag.py --seed 11 [--myr 1000] [--level 6] [--out DIR] [--fields]
        [--moments 400 580] [--set k=v ...]
    uv run python tools/ice_diag.py --summary DIR/seed11_L6.json.gz [...]
    uv run python tools/ice_diag.py --plot DIR/seed11_L6.json.gz [...]     (PNG next to each file)

Runs a simulation in memory (nothing goes to the store) with tectonics/diag.Recorder switched on, which
reads the run's state without changing it (the run is bit-identical to one without). Writes
DIR/seed<N>_L<l>.json.gz: per step the global temperature's parts (drift, CO2 term clipped and unclipped,
ice albedo term, target), the CO2 source and sink against their baselines, sea level with its ice and
ocean-basin parts, the iced land; per climate update every sheet's budget (snow gained, melt, what the
sea takes, net), the frozen-sea share, the rain on the ice and the snowline land. --fields also writes
DIR/seed<N>_L<l>_fields.npz (ice, mass balance, warm month, rain per update, float16; ~60 MB per L6 Gyr).
--moments T ... pickles the time zoom's source (timezoom.source_from_sim, exact) at those times, for
tools/tz_mean.py and tools/ice_probe.py --source.

The summary prints the whole-history criteria (tools/ice_criteria.py: old and new bars) and, for each
deep cold era, what held it: the mean CO2 term (and how much the clip at CO2_MAX withheld), the ice albedo
term, the drift, the sheets' net budget, and the volume of sheets the rule kept in deficit.
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
from planet.tectonics.diag import Recorder  # noqa: E402
from tools import ice_criteria as C  # noqa: E402


def parse_sets(kvs):
    sets = {}
    for kv in kvs:
        k, v = kv.split("=", 1)
        f = Params.__dataclass_fields__[k]
        sets[k] = v if f.type == "str" else (int(v) if f.type == "int" else float(v))
    return sets


def run(seed, myr, level, sets, out: Path, fields=False, moments=()):
    from planet import timezoom as Z
    sets = {"flora_end": float(myr), **sets}  # (as timeline.simulate: plant groups scaled to the run)
    sim = Simulation(build_grid(level), seed, Params(**sets), 2.0)
    sim.diag = Recorder(fields=fields)
    todo = sorted(float(m) for m in moments)
    tag = f"seed{seed}_L{level}"
    t0 = time.time()

    def on_step(s):
        s.diag.step(s)
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
         **sim.diag.as_dict()}
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
             "clipped_pct": round(100 * float(np.mean([abs(r["co2"]) >= 3.0 for r in rows])), 0)}
        if us:
            e["net"] = round(float(np.mean([u["budget"]["net"] for u in us])), 3)
            e["deficit_vol"] = round(float(np.mean([u["budget"]["deficit_vol_m"] for u in us])))
            e["sea_frozen"] = round(float(np.mean([u["sea_frozen"] for u in us])), 3)
            e["precip_ice"] = round(float(np.mean([u["precip_ice"] for u in us])))
            e["lat_min"] = round(float(np.min([u["iced_lat_min"] for u in us if u["iced_lat_min"] is not None])), 1)
        out.append(e)
    return out


def summary(path):
    d = C.load(path)
    r = C.evaluate(d)
    print(C.line(Path(path).name.split(".")[0], r))
    for e in eras(d):
        print(f"    era {e['t0']:g}-{e['t1']:g} ({e['myr']:g} Myr) worst {e['worst']} m: dT {e['dT']:+.1f} = drift "
              f"{e['drift']:+.1f} + CO2 {e['co2_term']:+.1f} (index {e['co2']:+.2f}, clipped {e['clipped_pct']:g}% of"
              f" steps, withheld {e['co2_withheld']:+.1f}) + albedo {e['albedo']:+.1f}; sink x{e['sink']} src x{e['src']},"
              f" iced land {100 * e['iced_land']:.0f}%; sheets net {e.get('net')} m/kyr, in deficit {e.get('deficit_vol')} m;"
              f" frozen sea {e.get('sea_frozen')}, snow on ice {e.get('precip_ice')} mm, ice to {e.get('lat_min')} deg")


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
    ax[1].plot(t, f("co2_term_free"), label="CO2 term (unclipped)", color="#d08a1a", lw=0.6, ls=":")
    ax[1].plot(t, f("albedo_term"), label="ice albedo term", color="#2a6fdb", lw=0.8)
    ax[1].set_ylabel("C"); ax[1].legend(loc="lower left", fontsize=8, ncol=3)
    ax[2].semilogy(t, np.maximum(f("sink"), 1e-3), label="weathering sink / baseline", color="#3a9a4a")
    ax[2].semilogy(t, np.maximum(f("src"), 1e-3), label="volcanic source / baseline", color="#b04040")
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, nargs="*", default=[])
    ap.add_argument("--myr", type=float, default=1000)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--out", default="ice_diag_out")
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--fields", action="store_true")
    ap.add_argument("--moments", type=float, nargs="*", default=[])
    ap.add_argument("--summary", nargs="*")
    ap.add_argument("--plot", nargs="*")
    a = ap.parse_args()
    for p in a.summary or []:
        summary(p)
    for p in a.plot or []:
        plot(p)
    out = Path(a.out)
    for s in a.seed:
        out.mkdir(parents=True, exist_ok=True)
        summary(run(s, a.myr, a.level, parse_sets(a.set), out, a.fields, a.moments))


if __name__ == "__main__":
    main()
