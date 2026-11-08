"""Counts of what planet/language/inputs.py derives from a peoples run, to sanity-check the derivation (PW-986).

    uv run python tools/language/inputs_report.py a24559
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from planet import store as S
from planet.language import inputs as I


def main(ref: str = "a24559") -> None:
    t = time.time()
    r = I.Run(S.find_run(ref))
    print(f"run {r.id}: {len(r.demes)} demes, {len(r.frames_kyr)} frames {r.frames_kyr[0]}..{r.frames_kyr[-1]} kyr ago, seed {r.seed}")
    alive = [len(r.demes_alive(i)) for i in range(len(r.frames_kyr))]
    print("demes alive (every 4th frame):", ", ".join(f"{r.kyr(i)}:{alive[i]}" for i in range(0, len(alive), 4)), f"now:{alive[-1]}")
    pairs = [len(r.frame(i).pairs) for i in range(len(r.frames_kyr))]
    print(f"contact pairs per frame: min {min(pairs)} max {max(pairs)} now {pairs[-1]}")
    ev = Counter()
    for i in range(1, len(r.frames_kyr)):
        e = r.events_in(i)
        for k, v in e.items():
            ev[k] += len(v)
    print("events in the window:", dict(ev))
    comps = r.start_components(0.05)
    print(f"start components (same people, contact > 0.05): {len(comps)} over {alive[0]} demes")
    tr = r.triggers
    print("triggers by kind:", dict(Counter(x.kind for x in tr)), "total", len(tr))
    for k in ("elite", "takeover", "city", "swamp", "trade"):
        ex = [x for x in tr if x.kind == k][:1]
        for x in ex:
            print(f"  e.g. {k}: deme {x.ruled_deme} ({r.people_of(x.ruled_deme)}) under {x.ruler_deme} ({r.people_of(x.ruler_deme)}) "
                  f"{x.start_kyr}->{x.end_kyr} s={x.strength:.2f}: {x.source}")
    arr = [a for i in range(len(r.frames_kyr)) for a in r.crop_arrivals(i)]
    print(f"crop/animal arrivals: {len(arr)} (with donor {sum(a[2] is not None for a in arr)}, origins {sum(a[3] for a in arr)}, "
          f"known at start {len(r.known_at_start())})")
    print("  by concept:", dict(Counter(a[1] for a in arr).most_common(8)))
    R = r.rivers()
    big = sorted(R.values(), key=lambda x: -x["flow"])[:5]
    print(f"rivers: {len(R)} (flow >= {I.RIVER_FLOW}, >= {I.RIVER_MIN_CELLS} cells); largest:", [(x["id"], x["cells"], round(x["flow"])) for x in big])
    print(f"lakes: {len(r.lakes())}")
    d = r.demes_alive(len(r.frames_kyr) - 1)[0]
    print(f"deme {d} landscape now:", r.deme_landscape(d, len(r.frames_kyr) - 1))
    print(f"deme {d} niche now:", r.niche_weights(d, len(r.frames_kyr) - 1), "l2", round(r.l2_share(d, len(r.frames_kyr) - 1), 3))
    print(f"took {time.time() - t:.1f} s")


if __name__ == "__main__":
    main(*sys.argv[1:])
