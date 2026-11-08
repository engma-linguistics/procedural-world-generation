"""Round 3b (lane 207b): arm S's side effects, compared across trees from lag.py's JSONs.
python compare3b.py BASE=a.json OTHER=b.json ...   (one run per call; the first label is the baseline for "fast techs identical").

Per tree: the settled admin cases never taken (tables.admin_split's split: a town of its own by the ready date), split by whether it
has a town now; writing, kingship and cultivation at 0.5 kyr ago (median of draws); printing, paper and libraries among the peoples
holding writing at 0.5 kyr ago (pooled over draws); writing among the peoples with no town of their own by 0.5 kyr ago; and the
fast techs' dates compared people by people, draw by draw, against the first tree."""
import json, sys

import numpy as np

FAST = ("cultivation", "herding", "plough", "copper", "bronze", "iron", "towns", "cities", "pottery", "fire_making", "boats", "chiefdoms")
AT = 0.5


def held(v, t, at=AT):
    d = v["dates"].get(t)
    return d is not None and d >= at - 1e-9


def settled_never(D):
    """(settled admin cases, never taken, of those with a town now, of those without)."""
    n = nv = now = gone = 0
    for d in D["draws"]:
        P = d["people"]
        for p, t, k, E, tp, rd, how, km in d["cases"]:
            if k != "admin" or rd is None or (tp is not None and tp >= rd):
                continue
            tf = P[p]["towns_first"]
            if tf is None:
                continue
            if tf < rd and tp is not None and tp >= tf:
                continue  # (tables.admin_split: counted from its first town; held by then)
            n += 1
            if tp is None:
                nv += 1
                if (P[p]["towns_now"] or 0) >= 1:
                    now += 1
                else:
                    gone += 1
    return n, nv, now, gone


def summary(label, D, B=None):
    n, nv, now, gone = settled_never(D)
    row0 = {"settled never, town now": now / max(n, 1)}
    med = lambda f: np.median([f(d) for d in D["draws"]])
    hand = lambda d: list(d["people"].values())
    share = lambda t: med(lambda d: np.mean([held(v, t) for v in hand(d)]))
    W = [v for d in D["draws"] for v in hand(d) if held(v, "writing")]
    among = {t: (sum(held(v, t) for v in W) / max(len(W), 1)) for t in ("paper", "libraries", "printing")}
    pr_med = med(lambda d: np.mean([held(v, "printing") for v in hand(d) if held(v, "writing")] or [0.0]))
    nt = [v for d in D["draws"] for v in hand(d) if (v["towns_first"] is None or v["towns_first"] < AT) and not v["hosted"]]
    hs = [v for d in D["draws"] for v in hand(d) if v["hosted"]]
    W0 = [v for d in D["draws"] for v in hand(d) if held(v, "writing", 0.0)]
    row = {"settled cases": n, "settled never": nv / max(n, 1), **row0, "never, town now": now, "never, no town now": gone,
           "cultivation": share("cultivation"), "writing": share("writing"), "kingship": share("kingship"), "law": share("law"),
           "coinage": share("coinage"), "printing (all)": share("printing"), "paper | writing": among["paper"],
           "libraries | writing": among["libraries"], "printing | writing": among["printing"], "printing | writing, median": pr_med,
           "no town by 0.5: n": len(nt), "no town by 0.5: writing": np.mean([held(v, "writing") for v in nt]) if nt else float("nan"),
           "no town by 0.5: cultivation": np.mean([held(v, "cultivation") for v in nt]) if nt else float("nan"),
           "groups and overlays: n": len(hs), "groups and overlays: writing": np.mean([held(v, "writing") for v in hs]) if hs else float("nan"),
           "printing | writing, today": sum(held(v, "printing", 0.0) for v in W0) / max(len(W0), 1)}
    if B is not None:
        diff = tot = 0
        for d, b in zip(D["draws"], B["draws"]):
            assert d["seed"] == b["seed"]
            for p, v in d["people"].items():
                if p not in b["people"]:
                    continue
                for t in FAST:
                    tot += 1
                    diff += v["dates"].get(t) != b["people"][p]["dates"].get(t)
        row["fast dates differing"] = f"{diff} of {tot}"
    return row


def main():
    rows, B = {}, None
    for arg in sys.argv[1:]:
        label, f = arg.split("=", 1)
        D = json.loads(open(f).read())
        rows[label] = summary(label, D, B)
        B = B or D
        run = D["run"]
    labels = list(rows)
    print(f"\n**{run}** (8 draws)\n")
    print("| measure | " + " | ".join(labels) + " |")
    print("|---|" + "---|" * len(labels))
    for k in rows[labels[-1]]:
        cells = []
        for l in labels:
            v = rows[l].get(k, "")
            cells.append(f"{v:.0%}" if isinstance(v, float) else str(v))
        print(f"| {k} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
