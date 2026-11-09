"""Lane 245: which of the ledger's parts give the read-out its state count? Re-make a run's settlement ledger with CONST overrides
in a mirror folder (no polities_live.json), derive the polities from it, count states. Read-only on the run.
argv: run_dir out_root arm [arm ...]; an arm is name:KEY=VAL,KEY=VAL (empty: the ledger as is)."""
import json
import os
import statistics as st
import sys
import time
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO
from planet.lineages import settlements as SE

run = Path(sys.argv[1])
root = Path(sys.argv[2])
for arm in sys.argv[3:]:
    name, _, kv = arm.partition(":")
    over = {}
    for x in filter(None, kv.split(",")):
        k, v = x.split("=")
        over[k] = float(v)
    m = root / f"{run.name}_{name}"
    m.mkdir(parents=True, exist_ok=True)
    for f in run.iterdir():
        if f.name in ("polities_live.json", "settlements.json", "polities.json"):
            continue
        t = m / f.name
        if not t.exists():
            os.symlink(f, t)
    t0 = time.time()
    if over:
        out = SE.derive(run, **over)
        (m / "settlements.json").write_text(json.dumps(out["doc"]))
    elif not (m / "settlements.json").exists():
        os.symlink(run / "settlements.json", m / "settlements.json")
    t1 = time.time()
    D = PO.derive(m)
    S = json.loads((m / "settlements.json").read_text())
    km2 = None
    from planet.grid import shared_grid
    rj = json.loads((run / "run.json").read_text())
    g = shared_grid(rj["meta"]["level"])
    km2 = 4 * np.pi * PO.R_EARTH_KM ** 2 / g.n
    steps = [(s["ago"], [(e[0], e[1], PO._unpack(e[2])) for e in mp]) for s, mp in zip(D["steps"], D["maps"])]
    at = lambda a: min(steps, key=lambda s: abs(s[0] - a))[1]  # noqa: E731
    n = lambda a: sum(t in (1, 2) for _, t, _ in at(a))  # noqa: E731
    ch = lambda a: sum(t == 0 for _, t, _ in at(a))  # noqa: E731
    big = [max((len(c) * km2 / 1e6 for _, t, c in mp if t in (1, 2)), default=0.0) for a, mp in steps if a <= 3.0 + 1e-9]
    cities = lambda a: sum(1 for s in S["sites"] if s["kind"] in PO.SETTLED_KINDS and s["founded_kyr"] >= a and (s["abandoned_kyr"] is None or s["abandoned_kyr"] < a)  # noqa: E731
                           and np.interp(-a, [-x for x, _ in s["series"]], [p for _, p in s["series"]]) >= 10000)
    print(f"{run.name} {name:12s} {over} | states 2,000/1,000/0 ya {n(2.0)}/{n(1.0)}/{n(0.0)} | chiefdoms {ch(2.0)}/{ch(1.0)}/{ch(0.0)} | "
          f"city sites {cities(2.0)}/{cities(1.0)}/{cities(0.0)} | largest median {st.median(big):.2f} peak {max(big):.2f} | "
          f"ledger {t1 - t0:.0f}s derive {time.time() - t1:.0f}s", flush=True)
