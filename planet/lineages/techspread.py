"""How fast one tech spread through a peoples run (lane 184, D49's follow-up): read after the run from what it stored.

In plain words: for one tech (writing by default) this says when each people and each culture first knew it and how (invented, or
taken from whom), and draws the curve of its spread: at every century step of the settlement ledger, the share of the settled
people (everyone living in a village, town or city of the ledger) whose people knew it by then, and the share of the cells with a
town. Its headline numbers are the years from the first invention to a quarter, half and nine-tenths of the settled people, and to
the last big people (one holding BIG_SHARE or more of the world's settled people at the present). Nothing here re-runs the history:
it reads meta.techtree.known (planet/lineages/techtree.py), settlements.json and cultures.json. The globe view of the same tech
is the Technology tab's Map (the 'technology' layer).

For each people it also says when it was first ready (it knew the tech's own needs, techtree.toml `needs`) and when it was first
in touch with a people who knew the tech (meta.contacts), so a wait reads as "not ready" or "ready, at the border, slow to take".
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

VERSION = 1  # (bump when the read-out changes: the server's cached docs are remade)
BIG_SHARE = 0.01  # judgement: a "big" people holds 1% or more of the world's settled people at the present
SETTLED_KINDS = ("chief", "minority")  # (as polities.SETTLED_KINDS: a people's own places; mines and pits are workplaces)
SHARES = (0.25, 0.5, 0.9)


def _holders(s: dict, A: np.ndarray) -> list:
    """The site's holder people at each step (polities._site_tables' holder(), for every step at once)."""
    h = [s.get("holder")] * len(A)
    for a, p in s.get("holders") or []:  # (oldest first: a later change overrides from its date on)
        for k in np.flatnonzero(A <= a + 1e-6):
            h[k] = p
    return h


def _contact_from(meta: dict, known: dict, tech: str) -> dict:
    """people -> the first kyr ago it was in touch (meta.contacts) with a people who knew the tech by then; None: never."""
    out: dict = {}
    for p in (meta.get("contacts") or {}).get("pairs", []):
        a, b = p["a"], p["b"]
        if a not in known or b not in known:
            continue
        ser = p.get("series") or []
        fr = float(p["first_contact_kyr"])
        to = 0.0 if p.get("in_contact_now") else (min(q[0] for q in ser) if ser else fr)
        for x, y in ((a, b), (b, a)):
            v = (known[x] or {}).get(tech)
            if not v:
                continue
            at = min(float(v[0]), fr)  # (the giver knows it and they are in touch)
            if at >= to and (out.get(y) is None or at > out[y]):
                out[y] = at
    return out


def _ledger(run_dir: Path, meta: dict | None = None):
    """(meta, the ledger, its steps A (kyr ago, oldest first), its settled sites, their people per step, town_min)."""
    from . import polities as PO
    d = Path(run_dir)
    meta = meta or json.loads((d / "run.json").read_text())["meta"]
    if not meta.get("settlements"):
        raise SystemExit("this run has no settlement ledger: run the peoples again")
    S = json.loads((d / meta["settlements"]["file"]).read_text())
    step = float(S.get("step_kyr") or 0.1)
    n = int(round(float(S["from_kyr"]) / step)) + 1
    A = np.array([round(float(S["from_kyr"]) - k * step, 4) for k in range(n)])
    sites = [s for s in S["sites"] if s["kind"] in SETTLED_KINDS]
    pop, _, town_min = PO._site_tables(SimpleNamespace(S={**S, "sites": sites}), list(A))
    return meta, S, A, sites, pop, town_min


def town_footprint(run_dir: Path) -> dict:
    """Each people's town cells (cells where it holds a place of town size) at every ledger step, for the tech tree's D52 arms B
    and E (techtree.ARM_DEFAULTS): {people: (agos oldest first, counts)}, plus "_cell_km2". Read-only."""
    meta, S, A, sites, pop, town_min = _ledger(run_dir)
    cells: dict = {}  # people -> step -> set of cells
    for i, s in enumerate(sites):
        live = np.flatnonzero(pop[i] > 0)
        if not len(live):
            continue
        hs = _holders(s, A)
        for k in live:
            if pop[i, k] >= town_min(s, A[k]):
                cells.setdefault(hs[k], [set() for _ in A])[k].add(s["cell"])
    out: dict = {lid: (A.copy(), np.array([len(c) for c in v], float)) for lid, v in cells.items()}
    out["_cell_km2"] = float(meta["settlements"].get("cell_km2") or 0.0)
    return out


def derive(run_dir: Path, tech: str = "writing", tt: dict | None = None) -> dict:
    """The spread doc of one tech in a peoples run. Read-only. tt: a tech tree doc to read instead of the stored meta.techtree
    (techtree.rebuild's, to ask how today's rules would have spread it over the same history)."""
    d = Path(run_dir)
    meta = json.loads((d / "run.json").read_text())["meta"]
    tt = tt or meta.get("techtree") or {}
    known = tt.get("known") or {}
    techs = {t["id"]: t for t in tt.get("techs") or []}
    if tech not in techs:
        raise ValueError(f"no tech {tech!r} in this run's tree")
    meta, S, A, sites, pop, town_min = _ledger(d, meta)
    n = len(A)
    lines = {l["id"]: l for l in meta.get("lineages") or []}
    name = lambda lid: ((lines.get(lid) or {}).get("name") or lid).split(" (")[0]
    when = {lid: float(v[tech][0]) for lid, v in known.items() if v.get(tech)}
    pop_by: dict = {}  # people -> settled people per step
    knew = np.zeros(n)
    tot = pop.sum(axis=0)
    town_cells_all = [dict() for _ in range(n)]  # step -> cell -> (people, pop) of its biggest town
    for i, s in enumerate(sites):
        live = np.flatnonzero(pop[i] > 0)
        if not len(live):
            continue
        hs = _holders(s, A)
        for k in live:
            h = hs[k]
            pv = pop[i, k]
            pop_by.setdefault(h, np.zeros(n))[k] += pv
            if h in when and when[h] >= A[k] - 1e-9:
                knew[k] += pv
            if pv >= town_min(s, A[k]):
                c = town_cells_all[k]
                if s["cell"] not in c or pv > c[s["cell"]][1]:
                    c[s["cell"]] = (h, pv)
    share = np.where(tot > 0, knew / np.maximum(tot, 1e-9), 0.0)
    towns_n = np.array([len(c) for c in town_cells_all])
    towns_k = np.array([sum(1 for h, _ in c.values() if h in when and when[h] >= A[k] - 1e-9) for k, c in enumerate(town_cells_all)])
    tshare = np.where(towns_n > 0, towns_k / np.maximum(towns_n, 1), 0.0)
    first = max(when.values()) if when else None
    total_now = float(tot[-1]) or 1.0

    def reached(x, sh):
        k = np.flatnonzero(sh >= x)
        return float(A[k[0]]) if len(k) else None

    needs = techs[tech].get("needs") or []
    touch = _contact_from(meta, known, tech)
    peoples = []
    for lid in sorted(set(known) | set(pop_by), key=lambda l: (-when.get(l, -1.0), l)):
        if lid not in known:
            continue
        v = (known[lid] or {}).get(tech)
        nd = [(known[lid] or {}).get(x) for x in needs]
        ready = min(float(x[0]) for x in nd) if nd and all(nd) else (None if nd else None)
        ser = pop_by.get(lid)
        now = float(ser[-1]) if ser is not None else 0.0
        peak = float(ser.max()) if ser is not None else 0.0
        if not v and peak <= 0:
            continue  # (a people that never had it and never had a place: foragers or dragons, not in the measure)
        peoples.append({"id": lid, "name": name(lid), "ago": float(v[0]) if v else None, "how": v[1] if v else None,
                        "from": v[2] if v else None, "from_name": name(v[2]) if v and v[2] else None,
                        "ready": ready, "touch": touch.get(lid), "settled_now": int(round(now)), "settled_peak": int(round(peak)),
                        "share_now": round(now / total_now, 4), "big": now >= BIG_SHARE * total_now})
    big = [p for p in peoples if p["big"]]
    last_big = min((p for p in big if p["ago"] is not None), key=lambda p: p["ago"], default=None)
    C = json.loads((d / meta["cultures"]["file"]).read_text())["cultures"] if meta.get("cultures") else []
    cultures = []
    for c in C:
        w = when.get(c["people"])
        if w is None or (c.get("ended_kyr") is not None and c["ended_kyr"] > w):
            continue  # (its people never knew it, or the culture had ended before they did)
        born = float(c["born_kyr"])
        v = known[c["people"]][tech]
        cultures.append({"id": c["id"], "name": c["name"], "people": c["people"], "ago": min(w, born), "born": born,
                         "how": v[1] if w <= born else "from its start", "from": v[2] if w <= born else None,
                         "alive": c.get("ended_kyr") is None})
    cultures.sort(key=lambda c: -c["ago"])
    r = lambda x: None if x is None else round(x, 3)
    return {"format": "procgen-techspread/1", "version": VERSION, "tech": tech, "tech_name": techs[tech]["name"], "needs": needs,
            "steps": [r(a) for a in A], "share_people": [round(float(x), 4) for x in share], "share_towns": [round(float(x), 4) for x in tshare],
            "settled": [int(round(float(x))) for x in tot], "towns": towns_n.tolist(),
            "stats": {"first_kyr": first, "first_by": [name(l) for l, w in when.items() if w == first],
                      "inventions": sum(1 for v in known.values() if (v.get(tech) or [None, None])[1] == "invented"),
                      "reach_kyr": {str(x): r(reached(x, share)) for x in SHARES},
                      "reach_towns_kyr": {str(x): r(reached(x, tshare)) for x in SHARES},
                      "big_peoples": len(big), "big_never": [p["name"] for p in big if p["ago"] is None],
                      "last_big": {"name": last_big["name"], "ago": last_big["ago"]} if last_big else None,
                      "share_now": round(float(share[-1]), 4), "big_share": BIG_SHARE},
            "peoples": peoples, "cultures": cultures}


def report(doc: dict) -> list[str]:
    """Plain lines: the headline numbers of a spread doc."""
    from .years import years_ago
    s = doc["stats"]
    f = s["first_kyr"]
    if f is None:
        return [f"{doc['tech_name']}: nobody in this run came to it"]
    out = [f"{doc['tech_name']}: first {years_ago(f)} ({', '.join(s['first_by'])}); {s['inventions']} inventions"]
    for x, a in s["reach_kyr"].items():
        out.append(f"  {float(x):.0%} of settled people: " + (f"{years_ago(a)} ({(f - a) * 1000:,.0f} years after the first)" if a is not None else "never"))
    lb = s["last_big"]
    if lb:
        out.append(f"  last big people ({s['big_peoples']} hold {s['big_share']:.0%}+ each): {lb['name']}, {years_ago(lb['ago'])} ({(f - lb['ago']) * 1000:,.0f} years after)")
    if s["big_never"]:
        out.append(f"  big peoples that never had it: {', '.join(s['big_never'])}")
    out.append(f"  share of settled people knowing it now: {s['share_now']:.0%}")
    return out
