"""usage: fmtally.py DIAG_DIR [...] -> PW-866's measures side by side, per draw and tallied per queue:
- the deep-time bar on 300 Myr to the end (passrate4.judge, PW-865 option C; a frozen-over world, 40%+ of the land under ice, also fails, PW-1091);
- the finish checks at the very end, as passrate4 judges them (true mean -6..+3 C, least land ice of the last 12 Myr
  1-25%, wet-eq trees >= 20%);
- the finish moment (planet.highlights.finish_moment: the latest step of the finish window that passes
  highlights.habitable, the same checks at that moment), how far back it sits, and which candidates it skipped;
- bar + finish checks at the finish moment (the target: ~70%).
It reads the steps' habitability fields (tectonics.output.habitability, recorded by diag.Recorder.step), so each
finish-window step is one of the run's keyframes. Harness only."""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import highlights as H  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

with redirect_stdout(io.StringIO()):  # (passrate4 runs on import; with no dirs it prints only empty tallies)
    _argv, sys.argv = sys.argv, [sys.argv[0]]
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v1-finish-12"))
    import passrate4 as P  # noqa: E402
    sys.argv = _argv

rows, tally = [], {}


def add(q, k, v):
    tally.setdefault((q, k), []).append(bool(v))


for d in map(Path, sys.argv[1:]):
    for p in sorted(d.glob("seed*_L*.json.gz")):
        raw = C.load(p)
        s = C.series(raw)
        bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"])
        steps = [r for r in raw["steps"] if r["t"] > 0]
        end = float(steps[-1]["t"])
        level = p.name.split("_")[1].split(".")[0]
        q = f"{level} {end / 1000:g} Gyr"
        win = float(raw["params"].get("finish_window", 10.0))
        frames = [{"t": r["t"], "stats": r} for r in steps]
        fm = H.finish_moment(frames, win)
        last = raw["updates"][-1]
        rel = last["temp"] - P.PREIND_T
        il = [100 * r["iced_land"] for r in steps if r["t"] >= end - 12 and "iced_land" in r]
        e_t = P.HUMAN_RANGE[0] <= rel <= P.HUMAN_RANGE[1]
        e_i = P.LAND_ICE_NONE <= min(il) < P.LAND_ICE_LGM
        e_w = (last.get("wet_eq_trees") or -1) >= P.WET_TREES
        end_all = e_t and e_i and e_w
        at = next(r for r in steps if abs(r["t"] - fm["t"]) < 1e-9)
        fails = H.habitable(at)
        skipped = [r["t"] for r in steps if r["t"] > fm["t"] + 1e-9]
        why_skip = {}
        for r in steps:
            if r["t"] > fm["t"] + 1e-9:
                for k in H.habitable(r):
                    why_skip[k] = why_skip.get(k, 0) + 1
        for k, v in [("bar 300-end", bar["ok"]), ("end: T", e_t), ("end: land ice", e_i), ("end: wet trees", e_w),
                     ("end: all three", end_all), ("bar + end checks", bar["ok"] and end_all),
                     ("moment: passes", fm["passes"]), ("moment: T", "temperature" not in fails),
                     ("moment: land ice", "land ice" not in fails), ("moment: wet trees", "wet-tropics trees" not in fails),
                     ("bar + moment checks", bar["ok"] and fm["passes"])]:
            add(q, k, v)
        rows.append((q, d.name, p.name.split("_")[0], bar, rel, min(il), last.get("wet_eq_trees"), end_all, fm, at,
                     len(skipped), why_skip))

print(f"{'queue':>9} {'dir':>12} {'seed':>11} {'bar':>4} | end: {'T-PI':>5} {'ice':>5} {'wet':>4} {'all':>3} | "
      f"moment: {'back':>4} {'T-PI':>5} {'ice':>5} {'wet':>4} {'ok':>3} {'cand':>4} {'pass':>4}  skipped (why)")
for q, dn, seed, bar, rel, imin, wet, ea, fm, at, nsk, ws in sorted(rows, key=lambda r: (r[0], r[1], r[2])):
    w = "-" if wet is None else f"{wet:.0f}"
    aw = "-" if at.get("wet_eq_trees_pct") is None else f"{at['wet_eq_trees_pct']:.0f}"
    sk = ", ".join(f"{k} {n}" for k, n in sorted(ws.items())) if nsk else ""
    print(f"{q:>9} {dn:>12} {seed:>11} {'ok' if bar['ok'] else P.flags(bar).strip()[:4]:>4} | "
          f"     {rel:+5.1f} {imin:5.1f} {w:>4} {'yes' if ea else 'no':>3} | "
          f"        {fm['before_end_myr']:4.1f} {at['true_temp_c'] - H.PREIND_T:+5.1f} {at['iced_land_pct']:5.1f} "
          f"{aw:>4} {'yes' if fm['passes'] else 'NO':>3} {fm['candidates']:>4} {fm['passing']:>4}  "
          f"{nsk} later {sk and '(' + sk + ')'}")
print("\ntallies:")
for (q, k), v in sorted(tally.items()):
    print(f"  {q:>9} {k}: {sum(v)}/{len(v)}")
backs = [r[8]["before_end_myr"] for r in rows if r[8]["passes"]]
if backs:
    print(f"look-back of passing moments (Myr): median {np.median(backs):g}, max {max(backs):g}, "
          f"at the end {sum(b == 0 for b in backs)}/{len(backs)}")

# set-level sanity (owner 2026-10-27, wording 2026-10-30): nearly all worlds frozen over (40%+ of the land under ice),
# or nearly all hellhouse, means the sim is wrong. The three ice terms are tallied beside it.
for q in sorted({r[0] for r in rows}):
    rs = [r for r in rows if r[0] == q]
    ib, hl = sum(bool((r[3] or {}).get("frozen")) for r in rs), sum(bool((r[3] or {}).get("hell")) for r in rs)
    gm, ih = sum(bool((r[3] or {}).get("glacial_max")) for r in rs), sum(bool((r[3] or {}).get("icehouse")) for r in rs)
    print(f"{q}: icehouse {ih}/{len(rs)}, glacial maximum {gm}/{len(rs)}, frozen over {ib}/{len(rs)}, hellhouse {hl}/{len(rs)}" + ("  << SIM SUSPECT" if max(ib, hl) >= 0.8 * len(rs) else ""))
