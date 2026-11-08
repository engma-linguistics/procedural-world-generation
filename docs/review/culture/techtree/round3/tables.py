"""Round 3 tables from lag.py's JSONs: python tables.py LABEL=a.json[,b.json...] ...  (one label per arm, its runs comma-separated).
Lags in years; medians over draws; cases pooled over draws. Eras by the exposure date (kyr ago): old > 5, mid 5-2, late < 2."""
import json, sys
from collections import Counter, defaultdict

import numpy as np

ERAS = (("> 5 kyr ago", 5.0, 1e9), ("5-2 kyr ago", 2.0, 5.0), ("last 2 kyr", -1.0, 2.0))


def era(e):
    return next(n for n, lo, hi in ERAS if lo < e <= hi)


def lag_rows(D, ready=False):
    """{(kind, era): [n, n taken within 100 yr, lags of the taken, n >= 300 yr, n >= 1000 yr, n never]} pooled over draws."""
    out = defaultdict(lambda: [0, 0, [], 0, 0, 0])
    for d in D["draws"]:
        for p, t, k, E, tp, rd, how, km in d["cases"]:
            if ready:
                if rd is None:
                    continue
                E = rd
                if tp is not None and tp >= E:
                    continue
            lag = (E - (tp if tp is not None else 0.0)) * 1000
            for kk in (k, "all"):
                r = out[(kk, era(E))]
                r[0] += 1
                r[1] += tp is not None and lag <= 100
                if tp is not None:
                    r[2].append(lag)
                r[3] += lag >= 300
                r[4] += lag >= 1000
                r[5] += tp is None
    return out


def print_lags(label, D, ready):
    rows = lag_rows(D, ready)
    print(f"\n**{D['run']} {label}**, lag from {'ready (exposed and holding the needs)' if ready else 'exposure'}; "
          f"{len(D['draws'])} draws pooled\n")
    print("| kind | era | cases | taken within 100 yr | median lag of the taken (yr) | 90th pct (yr) | lag >= 300 yr | >= 1,000 yr | never (lacks it today) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for k in ("farming", "metal", "admin", "other", "all"):
        for e, _, _ in ERAS:
            r = rows.get((k, e))
            if not r or not r[0]:
                continue
            n = r[0]
            med = f"{np.median(r[2]):,.0f}" if r[2] else "-"
            p90 = f"{np.percentile(r[2], 90):,.0f}" if r[2] else "-"
            print(f"| {k} | {e} | {n:,} | {r[1] / n:.0%} | {med} | {p90} | {r[3] / n:.0%} | {r[4] / n:.0%} | {r[5] / n:.0%} |")


def tail(label, D, cut=1000):
    """The slow tail: cases ready (exposed, needs held) and still not holding it cut years later."""
    who, what, how, ways, towns = Counter(), Counter(), Counter(), Counter(), Counter()
    n = 0
    for d in D["draws"]:
        P = d["people"]
        for p, t, k, E, tp, rd, h, km in d["cases"]:
            if rd is None:
                continue
            if (rd - (tp if tp is not None else 0.0)) * 1000 < cut or (tp is not None and tp >= rd):
                continue
            n += 1
            who[p] += 1
            what[t] += 1
            how[h or "never"] += 1
            ways[P[p]["way"] or ("group" if P[p]["group_of"] else "none")] += 1
            towns["towns" if (P[p]["towns_first"] is not None and P[p]["towns_first"] >= rd) else "no towns then"] += 1
    nd = len(D["draws"])
    print(f"\n**{D['run']} {label}: the slow tail** (ready, and >= {cut:,} yr until held or still lacking): {n / nd:.0f} cases per draw")
    print("- peoples: " + ", ".join(f"{p} {c / nd:.0f}" for p, c in who.most_common(10)))
    print("- techs: " + ", ".join(f"{t} {c / nd:.1f}" for t, c in what.most_common(12)))
    print("- how held in the end: " + ", ".join(f"{h} {c / max(n, 1):.0%}" for h, c in how.most_common()))
    print("- way of life: " + ", ".join(f"{h} {c / max(n, 1):.0%}" for h, c in ways.most_common()))
    print("- towns of its own by the ready date: " + ", ".join(f"{h} {c / max(n, 1):.0%}" for h, c in towns.most_common()))


def shares(label, D):
    dates = D["draws"][0]["dates"]
    print(f"\n**{D['run']} {label}**: share of today's peoples with hands holding the tech by each date (kyr ago; median of draws); "
          "last column: share of today's population (median)\n")
    print("| tech | " + " | ".join(f"{x:g}" for x in dates) + " | pop now |")
    print("|---|" + "---|" * (len(dates) + 1))
    for t in D["draws"][0]["shares"]:
        v = np.median([[x / d["n_hand"] for x in d["shares"][t]] for d in D["draws"]], axis=0)
        pp = np.median([d["shares_pop"][t] for d in D["draws"]])
        print(f"| {t} | " + " | ".join(f"{x:.0%}" for x in v) + f" | {pp:.0%} |")


def admin_split(label, D):
    """The admin techs' lag from ready, for peoples with a town of their own by the ready date (settled) and without."""
    out = {"settled": [], "not settled": []}
    nev = {"settled": 0, "not settled": 0}
    for d in D["draws"]:
        P = d["people"]
        for p, t, k, E, tp, rd, how, km in d["cases"]:
            if k != "admin" or rd is None or (tp is not None and tp >= rd):
                continue
            tf = P[p]["towns_first"]
            g = "settled" if tf is not None and tf >= rd else "not settled"
            if g == "settled":
                out[g].append((rd - (tp if tp is not None else 0.0)) * 1000)
                nev[g] += tp is None
            else:  # (lag counted from the later of ready and its first town, if it has one)
                r2 = tf if tf is not None else None
                if r2 is not None and (tp is None or tp < r2):
                    out["settled"].append((r2 - (tp if tp is not None else 0.0)) * 1000)
                    nev["settled"] += tp is None
                else:
                    out[g].append((rd - (tp if tp is not None else 0.0)) * 1000)
                    nev[g] += tp is None
    print(f"\n**{D['run']} {label}: admin techs, lag from ready (and from its first town, if later), by towns of its own**\n")
    print("| taker | cases | median (yr) | 90th pct (yr) | >= 1,000 yr | never |")
    print("|---|---|---|---|---|---|")
    for g, v in out.items():
        if v:
            v = np.asarray(v)
            print(f"| {g} | {len(v):,} | {np.median(v):,.0f} | {np.percentile(v, 90):,.0f} | {(v >= 1000).mean():.0%} | {nev[g] / len(v):.0%} |")


def atlas(label, D):
    """Present-day finish against the Atlas: share of peoples with hands (count) and of population holding each."""
    print(f"\n**{D['run']} {label}: at the present, peoples with hands (median of draws)**\n")
    print("| tech | share of peoples | share of population |")
    print("|---|---|---|")
    for t in ("cultivation", "copper", "iron", "chiefdoms", "kingship", "writing"):
        if t in D["draws"][0]["shares"]:
            print(f"| {t} | {np.median([d['shares'][t][-1] / d['n_hand'] for d in D['draws']]):.0%} | "
                  f"{np.median([d['shares_pop'][t] for d in D['draws']]):.0%} |")
    tw = [np.mean([v["towns_now"] is not None and v["towns_now"] >= 1 for v in d["people"].values()]) for d in D["draws"]]
    print(f"\nPeoples with hands with a town of their own now: {np.median(tw):.0%}")


def sea(label, D):
    by = defaultdict(list)
    for d in D["draws"]:
        for p, v in d["sea"].items():
            by[p].append(v)
    print(f"\n**{D['run']} {label}: sea and swimming peoples** (median of draws)\n")
    print("| people | realm | techs held | behind the world (yr) | goods held |")
    print("|---|---|---|---|---|")
    for p, vs in sorted(by.items()):
        b = [v["behind_kyr"] for v in vs if v["behind_kyr"] is not None]
        print(f"| {p} | {vs[0]['realm']}{' (swims)' if vs[0]['swims'] else ''} | {np.median([v['n'] for v in vs]):.0f} | "
              f"{np.median(b) * 1000:,.0f} | {', '.join(vs[0]['have'][:12]) or '-'} |" if b else
              f"| {p} | {vs[0]['realm']} | {np.median([v['n'] for v in vs]):.0f} | - | - |")


def main():
    for arg in sys.argv[1:]:
        label, files = arg.split("=", 1)
        for f in files.split(","):
            D = json.loads(open(f).read())
            print(f"\n### {D['run']}: {label} (arms {D['draws'][0]['arms']})")
            print_lags(label, D, False)
            print_lags(label, D, True)
            tail(label, D)
            admin_split(label, D)
            shares(label, D)
            atlas(label, D)
            sea(label, D)


if __name__ == "__main__":
    main()
