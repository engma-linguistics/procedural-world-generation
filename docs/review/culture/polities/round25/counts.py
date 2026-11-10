"""Round 25 (lane 281b, PW-1596): why the live state counts run under the read-out's. Read-only.

argv: run_dir [run_dir ...] [--readout]
Per run (the polities doc: derive, i.e. the live map when the run has polities_live.json; --readout: derive's own read-out even on
a switch-on run, the live map hidden, as round24/first_state.py):
- states (state or empire) standing at 3,000 / 2,000 / 1,000 / 0 years ago;
- by each of those dates, the state records founded so far (ever a state or empire up to then), and how those that had ended
  ended: conquered/invaded (a war took the capital), faded or collapsed (no seat any more);
- the ruled land in states (Mkm2) and the median state's size, at the same dates.
A state count lower with the same number founded and more conquered is consolidation (states die in wars); lower with fewer
founded is the seat test (fewer seats reach a state)."""
import json
import statistics as st
import sys
from pathlib import Path

from planet.lineages import polities as PO

DATES = (3.0, 2.0, 1.0, 0.0)


def main(argv):
    readout = "--readout" in argv
    if readout:
        PO._from_live = None
        _ex = Path.exists
        Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    for d in [Path(a) for a in argv if not a.startswith("--")]:
        D = PO.derive(d)
        km2 = D.get("cell_km2") or json.loads((d / "run.json").read_text())["meta"].get("cell_km2", 0)
        recs = {r["id"]: r for r in D["polities"]}
        steps = [(float(s["ago"]), m) for s, m in zip(D["steps"], D["maps"])]
        print(f"== {d.name} source={'readout' if readout else ('live' if (d / 'polities_live.json').exists() else 'readout')} cell_km2={km2}")
        for t in DATES:
            ago, mp = min(steps, key=lambda s: abs(s[0] - t))
            sizes = [len(PO._unpack(e[2])) * km2 / 1e6 for e in mp if e[1] in (1, 2)]
            ever = [r for r in recs.values() if any(a >= t - 1e-9 and tr in ("state", "empire") for a, tr in r.get("tiers") or [])]
            ended = [r for r in ever if r.get("fell_kyr") is not None and float(r["fell_kyr"]) >= t - 1e-9]
            how: dict = {}
            for r in ended:
                h = str(r.get("fell_how") or "?").split(" by ")[0]
                h = "conquered" if h.startswith(("conquered", "invaded")) else h
                how[h] = how.get(h, 0) + 1
            print(f"  {t * 1000:5,.0f} ya: states {len(sizes):3d} | ever a state by then {len(ever):3d}, ended {len(ended):3d} "
                  f"({', '.join(f'{k} {v}' for k, v in sorted(how.items()))}) | ruled {sum(sizes):6.2f} Mkm2, median "
                  f"{(st.median(sizes) if sizes else 0):.3f} Mkm2")


if __name__ == "__main__":
    main(sys.argv[1:])
