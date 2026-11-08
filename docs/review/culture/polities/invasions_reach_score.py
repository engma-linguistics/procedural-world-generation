"""Re-score strong one-century invasion rows (PW-1450, lane 198), read-only on a finished peoples run.

    uv run python docs/review/culture/polities/invasions_reach_score.py RUN_DIR N OUT.json [--jobs 6]

The rows (lane 177's set, rebuilt: its exact rows were not saved): the N peoples (a group rolled up into its people, dragons apart)
that rule the most polity-centuries in the run with no rows; one strong row per ordered pair (N x (N - 1) rows), each scored alone
(one derive per row, so rows never shadow each other), in one century: the invaders' peak century as a state or empire (the most
land), else as a chiefdom, else the present. Also scores the run with no rows (the baseline doc) and, per row, the plain wars
(not the row's) in the row's window step against the no-row doc's.
"""

from __future__ import annotations

import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401

import numpy as np  # noqa: E402

from planet.lineages import polities as PO  # noqa: E402


def _top(lines, p):
    by = {l["id"]: l for l in lines}
    seen = set()
    while (by.get(p) or {}).get("group_of") and p not in seen:
        seen.add(p)
        p = by[p]["group_of"]
    return p


def _land(doc):
    """people (rolled up) -> {ago: (state cells, chiefdom cells)}; and per step the plain wars as (winner rec, loser rec)."""
    run_dir = Path(doc["_dir"])
    lines = json.loads((run_dir / "run.json").read_text())["meta"]["lineages"]
    drag = {l["id"] for l in lines if "dragon" in l["id"]}
    out: dict = {}
    for st, mp in zip(doc["steps"], doc["maps"]):
        ago = st["ago"]
        for e in mp:
            rec = doc["polities"][e[0]]
            ppl = PO._at(rec["peoples"], ago)[1]
            if ppl in drag or e[1] == 3:
                continue
            t = _top(lines, ppl)
            n = len(PO._unpack(e[2]))
            d = out.setdefault(t, {}).setdefault(ago, [0, 0])
            d[0 if e[1] in (1, 2) else 1] += n
    return out


def _wars(doc):
    """{ago: sorted [(winner id, loser id)]} of plain wars (how == 'war'), from the cards."""
    w: dict = {}
    for rec in doc["polities"]:
        for ago, lid, how in rec["took"]:
            if how == "war":
                w.setdefault(round(ago, 4), []).append((rec["id"], lid))
    return {a: sorted(v) for a, v in w.items()}


def _one(args):
    run_dir, row = args
    doc = PO.derive(Path(run_dir), invasions=[row] if row else None)
    doc["made_s"] = 0
    return doc


def main():
    run_dir, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
    base = _one((run_dir, None))
    sha = hashlib.sha1(json.dumps(base, sort_keys=True, default=float).encode()).hexdigest()  # (the no-row doc, made_s zeroed: main vs branch)
    base["_dir"] = run_dir
    land = _land(base)
    cent = {p: sum(1 for v in d.values() if v[0] + v[1] > 0) for p, d in land.items()}
    peoples = sorted(cent, key=lambda p: (-cent[p], p))[:n]
    year = {}
    for p in peoples:
        d = land[p]
        st = max(d, key=lambda a: (d[a][0], a)) if any(v[0] for v in d.values()) else None
        ch = max(d, key=lambda a: (d[a][1], a)) if any(v[1] for v in d.values()) else None
        year[p] = st if st is not None else (ch if ch is not None else 0.0)
    rows = [{"id": f"{a}>{b}", "who": {"people": a}, "whom": {"people": b}, "from_kyr": year[a], "to_kyr": year[a], "strength": "strong"}
            for a in peoples for b in peoples if a != b]
    with ProcessPoolExecutor(jobs) as ex:
        docs = list(ex.map(_one, [(run_dir, r) for r in rows]))
    bw = _wars(base)
    res = []
    for r, d in zip(rows, docs):
        o = d["invasions"]["rows"][0]
        dw = _wars(d)
        ago = r["from_kyr"]
        took = {t["loser_id"] for t in o["took"]}
        same = [x for x in bw.get(round(ago, 4), []) if x[1] not in took]
        here = [x for x in dw.get(round(ago, 4), []) if x[1] not in took]
        before_same = all(dw.get(a) == v for a, v in bw.items() if a > ago + 1e-6) and all(a <= ago + 1e-6 or a in bw for a in dw)
        res.append({"row": r, "happened": o["happened"], "why": o["why"], "km2": o["km2"], "took": o["took"], "reach": o.get("reach"),
                    "war_band": o.get("war_band"), "plain_wars_window": [len(same), len(here), sorted(same) == sorted(here)],
                    "plain_wars_before_same": before_same, "plain_wars_total": [sum(map(len, bw.values())), sum(map(len, dw.values()))]})
    base.pop("_dir")
    Path(out).write_text(json.dumps({"run": run_dir, "peoples": peoples, "year": year, "centuries": {p: cent[p] for p in peoples},
                                     "plain_wars_base": sum(map(len, bw.values())), "base_sha": sha, "rows": res}, indent=1, default=float))
    print(f"{sum(x['happened'] for x in res)} of {len(res)} happened; peoples {peoples}")


if __name__ == "__main__":
    main()
