"""Round 16's diagnosis (lane 241, PW-1583): why the history's polities stay small. Read-only. argv: label=run_dir ...
A run_dir whose polities_live.json is hidden (a mirror without it) gives the ledger read-out on that run's peoples.
Per source, over the last 3 kyr: counts by tier, the largest state/empire and what made it wide (a confederation, provinces taken
from a polity, or neither: a plain city-state inside STATE_MAX_KM), and the largest plain one."""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.grid import shared_grid
from planet.lineages import polities as PO


def load(d: Path):
    run = json.loads((d / "run.json").read_text())
    g = shared_grid(run["meta"]["level"])
    km2 = 4 * np.pi * PO.R_EARTH_KM ** 2 / g.n
    lp = d / "polities_live.json"
    if lp.exists():
        D, src = json.loads(lp.read_text()), "live"
    else:
        D, src = PO.derive(d), "ledger"
    confed = {r["id"]: {round(a, 3) for a, _ in r.get("confed", [])} for r in D["polities"]}
    return D, src, confed, km2


def one(label, d):
    D, src, confed, km2 = load(Path(d))
    recs = D["polities"]
    rows = []
    for s, m in zip(D["steps"], D["maps"]):
        a = round(s["ago"], 3)
        if a > 3.0 + 1e-9:
            continue
        cnt = {t: sum(e[1] == i for e in m) for i, t in enumerate(PO.TIERS)}
        info = []
        for e in m:
            if e[1] not in (1, 2):
                continue
            n = len(PO._unpack(e[2]))
            prov = e[-1] if isinstance(e[-1], dict) else {}
            kind = "confed" if a in confed.get(e[0], ()) else ("provinces" if prov else "plain")
            if kind == "provinces":  # (wide: one of its provinces was a state or empire when taken, WIDE_BY "conquest")
                was = [PO._at(recs[int(r)]["tiers"], recs[int(r)]["fell_kyr"] + 1e-6)[1] for r in prov if recs[int(r)].get("fell_kyr") is not None]
                kind = f"prov{len(prov)}" + ("W" if any(t in ("state", "empire") for t in was) else "")
            info.append((n * km2 / 1e6, kind, e[0]))
        big = max(info, default=(0.0, "-", None))
        plain = max((x for x in info if x[1] == "plain"), default=(0.0, "-", None))
        rows.append((a, cnt, big, plain, sum(x[1] == "confed" for x in info), len(info)))
    sz = [r[2][0] for r in rows]
    kinds: dict = {}
    for r in rows:
        kk = r[2][1] if not r[2][1].startswith("prov") else ("provinces, one was a state" if r[2][1].endswith("W") else "provinces of chiefdoms")
        kinds[kk] = kinds.get(kk, 0) + 1
    print("  largest per century (ago: Mkm2 kind): " + ", ".join(f"{r[0]:.1f}: {r[2][0]:.2f} {r[2][1]}" for r in rows if r[5]))
    print(f"=== {label} [{src}] {Path(d).name}")
    for a in (3.0, 2.0, 1.0, 0.0):
        r = min(rows, key=lambda r: abs(r[0] - a))
        print(f"  {a:.0f} kyr ago: {r[1]} confeds {r[4]} | largest {r[2][0]:.2f} ({r[2][1]}) | largest plain {r[3][0]:.2f}")
    print(f"  last 3 kyr: largest median {st.median(sz):.2f} peak {max(sz):.2f}; largest is {kinds}; "
          f"largest plain median {st.median([r[3][0] for r in rows]):.2f} peak {max(r[3][0] for r in rows):.2f}; "
          f"states median {st.median([r[5] for r in rows])}, confeds median {st.median([r[4] for r in rows])}")
    lost = [r for r in recs if (r.get("fell_how") or "").startswith(("conquered", "invaded"))]
    by_tier: dict = {}
    for r in lost:
        t = PO._at(r["tiers"], r["fell_kyr"] + 1e-6)[1]
        by_tier[t] = by_tier.get(t, 0) + 1
    print(f"  conquered polities by their tier when taken: {by_tier}")
    first = max((round(s["ago"], 3) for s, m in zip(D["steps"], D["maps"]) if any(e[1] in (1, 2) for e in m)), default=None)
    if src == "live":
        took = [t for r in recs for t in r.get("took", [])]
        print(f"  first state {first} kyr ago; conquests (all run): {len(took)}; in last 3 kyr {sum(t[0] <= 3.0 for t in took)}")
    else:
        took = [(t[0], recs[t[1]]) for r in recs for t in r.get("took", [])]
        lst = [t for t in took if t[0] <= 3.0]
        st_l = sum(any(x[1] in ("state", "empire") for x in rr["tiers"]) for _, rr in lst)
        print(f"  first state {first} kyr ago; conquests (all run): {len(took)}; in last 3 kyr {len(lst)} (losers ever a state: {st_l})")


for arg in sys.argv[1:]:
    lab, d = arg.split("=", 1)
    one(lab, d)
