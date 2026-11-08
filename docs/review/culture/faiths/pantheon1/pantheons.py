"""PW-1521 prototype read-out (scout 220): the regional pantheons today's beings already imply. Review script, not shipped code.

Reads a stored peoples run (read-only), replays its gods as main does (gods.inputs + polities + gods.replay), and at the present asks:
where do cultures of different peoples meet, both open to other gods (tolerant, faith not missionary), around a mixed town or under one
state? In each such region, which beings of different peoples already look alike (the same leading domain, cos >= gods.FUSE_COS: the
ones interpretatio would call one god) and which stay one people's own? Nothing is written into the run.

    PLANET_DATA=<data root> uv run python docs/review/culture/faiths/pantheon1/pantheons.py <run id> <out dir>

Every threshold below is a JUDGEMENT for the read-out, not a proposal for the model.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from planet import store as S
from planet.lineages import gods as G

TOL_OPEN = 0.5  # a culture at least this tolerant (attitudes.py) is open to other peoples' gods
IND_GOD = 0.45  # a being at least this individuated (temples: gods.CONVERT_MIN) is a god that can travel; spirits stay bound to their land
MIX_MIN = 10  # a town or city where at least two peoples each hold this % is a meeting place (settlements.json "who")
REGION_MIN_PEOPLES = 2
UNION = len(sys.argv) > 3 and sys.argv[3] == 'union'


def lineage_root(docs: list, i: int) -> int:
    while docs[i]["parent"] is not None and docs[docs[i]["parent"]]["how"] in ("founded", "born", "split", "converted"):
        i = docs[i]["parent"]
    return i


def main(run: str, out: Path):
    run_dir = S.root() / "runs" / run
    from planet.lineages import polities as PO
    A = G.read_authored(run_dir)
    inp = G.inputs(run_dir)
    rule = G.rule_table(PO.derive(run_dir, invasions=A["invasions"]), inp["C"], inp["frames"]) if (run_dir / "settlements.json").exists() else None
    d = G.replay(inp, G.MODE_DEFAULT, A["faiths"], rule)
    out.mkdir(parents=True, exist_ok=True)
    C, F = inp["C"], inp["frames"][-1]
    docs = d["beings"]
    W = np.zeros((len(docs), len(G.DOMAINS)))
    for b in docs:
        for dom, v in b["top"]:
            W[b["id"], G.DOMAINS.index(dom)] = v
    tol = {int(c): v["now"][0] for c, v in d["attitudes"]["cultures"].items()}
    fdoc = {f["id"]: f for f in d["faiths"]["list"]}
    live = {int(c): v for c, v in d["cultures"].items() if v["living"] and v["faith_now"] is not None}
    people = {c: C[c]["people"] for c in live}

    def is_open(c):
        f = fdoc.get(live[c]["faith_now"]) or {}
        return tol.get(c, 0.0) >= TOL_OPEN and not f.get("missionary")

    # meeting places: mixed towns and cities now, located in the culture holding their cell at the last frame
    cul_at = dict(zip(F["cell"].tolist(), F["cul"].tolist()))
    sites = json.loads((run_dir / "settlements.json").read_text())["sites"]
    mixed = defaultdict(list)
    for s in sites:
        if s["tier_now"] in ("town", "city"):
            who = {p: v for p, v in (s.get("who") or {}).items() if p != "others" and v >= MIX_MIN}
            c = cul_at.get(s["cell"])
            if len(who) >= 2 and c in live:
                mixed[c].append((s["tier_now"], s["place"], who))
    # one state over several peoples
    state_of = {}
    for e in (rule or {}).get("now") or []:
        for c in e["cells"]:
            state_of.setdefault(int(c), []).append(e["id"])
    # gathering links: touching cultures of different peoples, both open
    edges = defaultdict(set)
    for (a, b), n in F["contacts"].items():
        if a in live and b in live and people[a] != people[b] and is_open(a) and is_open(b):
            edges[a].add(b)
            edges[b].add(a)
    # regions: each open meeting-place culture with its open neighbours of other peoples (one hop: a pantheon gathers around a market
    # or a capital). UNION=True joins hubs that touch: on these runs that percolates into one continent-wide region (the write-up)
    hubs = sorted(c for c in mixed if is_open(c) and edges.get(c))
    groups = [[h] for h in hubs]
    if UNION:
        parent = {h: h for h in hubs}

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for h in hubs:
            for x in edges[h]:
                if x in parent:
                    parent[find(x)] = find(h)
        gg = defaultdict(list)
        for h in hubs:
            gg[find(h)].append(h)
        groups = list(gg.values())
    regions = []
    for hs in groups:
        comp = sorted(set(hs) | {x for h in hs for x in edges[h]})
        states = Counter(s for c in comp for s in state_of.get(c, []))
        shared_state = any(len({people[c] for c in comp if s in state_of.get(c, [])}) >= 2 for s in states)
        if len({people[c] for c in comp}) >= REGION_MIN_PEOPLES:
            regions.append((comp, hs, shared_state))
    rows = []
    for comp, hubs, shared_state in sorted(regions, key=lambda r: -len(r[0])):
        gods = [b for c in comp for b in (docs[i] for i in live[c]["living"]) if b["individuation"] >= IND_GOD]
        by_dom = defaultdict(list)
        for b in gods:
            by_dom[b["top"][0][0]].append(b)
        domain_gods, own = [], defaultdict(list)
        for dom, bs in sorted(by_dom.items()):
            ps = {people[b["culture"]] for b in bs}
            if len(ps) >= 2:
                cen = W[[b["id"] for b in bs]].mean(0)
                alike = [b for b in bs if G._cos(W[b["id"]], cen) >= G.FUSE_COS]
                ps_alike = sorted({people[b["culture"]] for b in alike})
                roots = {lineage_root(docs, b["id"]) for b in alike}
                if len(ps_alike) >= 2:
                    domain_gods.append({"domain": dom, "peoples": ps_alike, "beings": len(alike), "lineages": len(roots),
                                        "max_ind": round(max(b["individuation"] for b in alike), 2),
                                        "high": sum(b["high"] for b in alike)})
                    continue
            for b in bs:
                own[people[b["culture"]]].append(b)
        own_gods = {p: sorted({b["role"] for b in bs if b["high"]} or {max(bs, key=lambda b: b["individuation"])["role"]})
                    for p, bs in own.items()}
        rows.append({"cultures": len(comp), "peoples": dict(Counter(people[c] for c in comp).most_common()),
                     "cells": int(sum(F["present"].get(c, 0) for c in comp)),
                     "hubs": [{"culture": C[c]["name"], "places": [f"{t} {pl} ({', '.join(f'{p} {v}%' for p, v in who.items())})"
                                                                   for t, pl, who in mixed[c][:3]]} for c in hubs[:6]],
                     "shared_state": shared_state, "gods_beings": len(gods), "domain_gods": domain_gods,
                     "peoples_own": own_gods,
                     "faiths": dict(Counter(fdoc[live[c]["faith_now"]]["name"] for c in comp).most_common(4))})
    n_live = len(live)
    summary = {"run": run, "living_cultures_with_faith": n_live,
               "open_cultures": sum(is_open(c) for c in live),
               "cultures_with_mixed_town": len([c for c in mixed if c in live]),
               "regions": len(rows),                "land_share_in_regions": round(sum(F["present"].get(c, 0) for c in {c for comp, _, _ in regions for c in comp}) / max(1, sum(F["present"].get(c, 0) for c in live)), 3),
               "regions_with_domain_gods": sum(1 for r in rows if r["domain_gods"]),
               "domain_gods_total": sum(len(r["domain_gods"]) for r in rows),
               "region_sizes_cultures": sorted((r["cultures"] for r in rows), reverse=True),
               "distinct_cultures_in_regions": len({c for comp, _, _ in regions for c in comp}),
               "domain_gods_per_region": sorted((len(r["domain_gods"]) for r in rows), reverse=True),
               "region_peoples": sorted((len(r["peoples"]) for r in rows), reverse=True)}
    (out / f"{run}_pantheons.json").write_text(json.dumps({"summary": summary, "regions": rows}, indent=1))
    print(json.dumps(summary, indent=1))
    for r in rows[:2] + rows[len(rows) // 2:len(rows) // 2 + 2]:
        print("\n== region:", r["cultures"], "cultures,", r["peoples"], "| hubs", len(r["hubs"]), "| shared state", r["shared_state"])
        for h in r["hubs"][:2]:
            print("   hub:", h["culture"], "|", "; ".join(h["places"][:2]))
        for g in r["domain_gods"]:
            print(f"   domain god of {g['domain']}: {', '.join(g['peoples'])} ({g['beings']} beings, {g['lineages']} lineages, max ind {g['max_ind']}, leading in {g['high']})")
        for p, gs in list(r["peoples_own"].items())[:8]:
            print(f"   {p}'s own: {'; '.join(gs[:3])}")


if __name__ == "__main__":
    main(sys.argv[1], Path(sys.argv[2]))
