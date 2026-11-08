"""Spread 1 tables from measure.py's output. argv: out_dir run.json ... (each measure.py output). Prints markdown to stdout.
Living peoples only. "body-less" peoples (no hands at all: the dragons) are listed apart; the shares are over peoples with hands.
Years behind (two clocks):
- behind the world: a people holding c of the world's techs (those some living people holds) is as far along as the world was
  when its c-th tech was first found anywhere; behind = that date (years ago).
- behind the leader: the same against the people holding the most today, by the leader's own dates."""
import json, math, sys
from collections import Counter, defaultdict

import numpy as np

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from planet.lineages import techtree as _TT  # noqa: E402

EARTH = {i: t.get("earliest_kyr") for i, t in _TT.load()["techs"].items()}

BENCH = ["cultivation", "herding", "pottery", "weaving", "copper", "bronze", "iron", "steel", "plough", "wheel", "sails",
         "towns", "chiefdoms", "cities", "kingship", "law", "writing", "coinage", "paper", "printing", "gunpowder", "lodestone_compass"]


def rank(x):
    return np.argsort(np.argsort(x)).astype(float)


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return float("nan")
    return float(np.corrcoef(rank(a[ok]), rank(b[ok]))[0, 1])


def behind(dates_sorted, c):
    """dates_sorted: first dates (kyr ago) of the world's techs, oldest first; c techs held -> kyr ago when the c-th was found."""
    if c <= 0:
        return dates_sorted[0]
    return dates_sorted[min(c, len(dates_sorted)) - 1]


def per_draw(d):
    P = d["people"]
    hand = {p: v for p, v in P.items() if len(v["known"]) > 30}  # (dragons hold their 10 body techs only)
    world = sorted({t for v in hand.values() for t in v["known"]})
    first = {t: max(v["known"][t][0] for v in hand.values() if t in v["known"]) for t in world}
    ds = sorted(first.values(), reverse=True)
    lead = max(hand, key=lambda p: len(hand[p]["known"]))
    lds = sorted((v[0] for t, v in hand[lead]["known"].items() if t in first), reverse=True)
    out = {}
    for p, v in hand.items():
        c = sum(1 for t in v["known"] if t in first)
        out[p] = {"n": c, "share": c / len(world), "behind_world": behind(ds, c), "behind_lead": behind(lds, c)}
    return hand, world, first, lead, out


def main():
    runs = [json.load(open(f)) for f in sys.argv[1:]]
    for R in runs:
        rid = R["run"]
        draws = R["draws"]
        print(f"\n## Run {rid} ({len(draws)} draws, seeds {draws[0]['seed']}-{draws[-1]['seed']}, era cap {R['era']})\n")
        pd = [per_draw(d) for d in draws]
        P0 = draws[0]["people"]
        nb = [p for p, v in P0.items() if len(v["known"]) <= 30]
        print(f"Living peoples: {len(P0)}; with hands {len(P0) - len(nb)}; body-limited (no hands): {len(nb)} "
              f"({', '.join(nb)}), each holding {sorted({len(v['known']) for v in P0.values() if len(v['known']) <= 30})} techs.\n")
        # ---- the world's techs, and how many a people holds
        wn = [len(x[1]) for x in pd]
        sh = np.array([[o["share"] for o in x[4].values()] for x in pd]).ravel()
        print(f"World set (techs some living people with hands holds): median {int(np.median(wn))} of "
              f"{len(draws[0]['techs'])} in the tree (era-capped). Share of the world set a people holds, all draws pooled: "
              f"p10 {np.percentile(sh, 10):.2f}, median {np.median(sh):.2f}, p90 {np.percentile(sh, 90):.2f}, min {sh.min():.2f}.\n")
        # ---- benchmark techs
        print("| tech | era | peoples holding (median of draws) | population holding | world first (kyr ago, median) | "
              "median wait first -> each holder (yr) | holders who invented it |")
        print("|---|---|---|---|---|---|---|")
        for t in BENCH:
            if t not in draws[0]["techs"]:
                continue
            shp, shn, fst, wait, own = [], [], [], [], []
            for d, (hand, world, first, lead, o) in zip(draws, pd):
                hp = [p for p in hand if t in hand[p]["known"]]
                shp.append(len(hp) / len(hand))
                tot = sum(hand[p]["pop"] or 0 for p in hand)
                shn.append(sum(hand[p]["pop"] or 0 for p in hp) / tot)
                if hp:
                    f = first[t]
                    fst.append(f)
                    wait += [1000 * (f - hand[p]["known"][t][0]) for p in hp]
                    own += [hand[p]["known"][t][1] in ("invented", "tamed") for p in hp]
            n = len(next(iter(pd))[0])
            print(f"| {t} | {draws[0]['techs'][t]['era']} | {np.median(shp):.0%} ({min(shp):.0%}-{max(shp):.0%}) | "
                  f"{np.median(shn):.0%} | {np.median(fst) if fst else float('nan'):.1f} | "
                  f"{np.median(wait) if wait else float('nan'):,.0f} | {np.mean(own) if own else 0:.0%} |")
        # ---- over time: share of today's peoples with hands holding each benchmark tech at a few dates (median of draws)
        AT = (4.0, 3.0, 2.0, 1.0, 0.5, 0.0)
        print("\nShare of today's peoples with hands holding the tech at each date (kyr ago; median of draws; a people "
              "not yet begun counts as not holding). Earth = the tree's own Earth date (techtree.toml earliest_kyr, its cited source):\n")
        print("| tech | Earth's first (kyr ago) | " + " | ".join(f"{a:g}" for a in AT) + " |")
        print("|---|---|" + "---|" * len(AT))
        for t in BENCH:
            if t not in draws[0]["techs"]:
                continue
            cells = []
            for a in AT:
                v = [sum(1 for p in hand if t in hand[p]["known"] and hand[p]["known"][t][0] >= a - 1e-9) / len(hand) for (hand, *_r) in pd]
                cells.append(f"{np.median(v):.0%}")
            print(f"| {t} | {EARTH.get(t, '-')} | " + " | ".join(cells) + " |")
        # ---- per era and track: share held
        print("\nShare of (people, tech) pairs held, by era of the tech (world-set techs only, peoples with hands, draws pooled):\n")
        print("| era | world-set techs | held by median people | pairs held |")
        print("|---|---|---|---|")
        for era in ("stone age", "bronze age", "classical", "medieval", "renaissance"):
            ns, held, tot = [], 0, 0
            for d, (hand, world, first, lead, o) in zip(draws, pd):
                ts = [t for t in world if d["techs"][t]["era"] == era]
                ns.append(len(ts))
                per = [sum(t in hand[p]["known"] for t in ts) / max(len(ts), 1) for p in hand]
                held += sum(per)
                tot += len(per)
            print(f"| {era} | {int(np.median(ns))} | {np.median([sum(t in hand[p]['known'] for t in [t for t in world if draws[0]['techs'][t]['era'] == era]) / max(1, len([t for t in world if draws[0]['techs'][t]['era'] == era])) for (hand, world, *_r) in pd for p in hand]):.0%} | {held / tot:.0%} |")
        # ---- spread of fast and slow: by spread factor
        # ---- people table
        print("\nPer people (peoples with hands), medians over draws. behind = years behind the world clock / the leader's clock "
              "(see the script's docstring); gaps = the techs it lacks whose prerequisites it holds, by first obstacle (median count).\n")
        print("| people | kind | way | population | area Mkm2 | neighbours now | landmasses (main lm cells) | specialists s | techs held "
              "| behind world (yr) | behind leader (yr) | top gaps |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        rows = []
        for p in pd[0][4]:
            v = draws[0]["people"][p]
            bw = [x[4][p]["behind_world"] * 1000 for x in pd if p in x[4]]
            bl = [x[4][p]["behind_lead"] * 1000 for x in pd if p in x[4]]
            n = [x[4][p]["n"] for x in pd if p in x[4]]
            g = Counter()
            for d in draws:
                if p in d["people"]:
                    g.update(Counter(d["people"][p]["gaps"].values()))
            g = {k: c / len(draws) for k, c in g.items()}
            rows.append((np.median(bw), p, v, np.median(bl), np.median(n), g, min(n), max(n)))
        for bw, p, v, bl, n, g, lo, hi in sorted(rows, key=lambda r: -r[0]):
            lm = v["lm"] or {}
            top = ", ".join(f"{k} {c:.0f}" for k, c in sorted(g.items(), key=lambda kv: -kv[1])[:3])
            print(f"| {p} | {v['stem']} | {v['way'] or '-'} | {v['pop']:,} | {v['area_mkm2']:.1f} | {len(v['neighbours'])} | "
                  f"{lm.get('landmasses', '-')} ({lm.get('main_lm_cells', '-')}) | {v['s']:.3f} | {n:.0f} ({lo}-{hi}) | {bw:,.0f} | {bl:,.0f} | {top} |")
        # ---- correlates of being behind
        bwv = np.array([r[0] for r in rows])
        att = {"log population": [math.log10(max(r[2]["pop"] or 1, 1)) for r in rows],
               "log area": [math.log10(max(r[2]["area_mkm2"] or 1e-3, 1e-3)) for r in rows],
               "neighbours now": [len(r[2]["neighbours"]) for r in rows],
               "border km now": [sum(r[2]["neighbours"].values()) for r in rows],
               "specialist share s": [r[2]["s"] for r in rows],
               "insularity": [r[2]["insularity"] or 0 for r in rows],
               "main landmass cells": [(r[2]["lm"] or {}).get("main_lm_cells", np.nan) for r in rows],
               "'land' gaps": [r[5].get("land", 0) for r in rows],
               "'stock' gaps": [r[5].get("stock", 0) for r in rows],
               "fronts en route": [r[5].get("front_en_route", 0) for r in rows],
               "started (kyr ago)": [r[2]["started_kyr"] or np.nan for r in rows]}
        print("\nSpearman rank correlation of years behind the world (median over draws) with each attribute, peoples with hands "
              f"(n = {len(rows)}; a positive value: more of it, further behind):\n")
        print("| attribute | rho |")
        print("|---|---|")
        for k, a in att.items():
            print(f"| {k} | {spearman(a, bwv):+.2f} |")
        # ---- gap reasons, all peoples
        tot = Counter()
        for d in draws:
            for p, v in d["people"].items():
                if len(v["known"]) > 30:
                    tot.update(v["gaps"].values())
        s = sum(tot.values())
        print("\nAll frontier gaps (a tech some living people holds, whose prerequisites this people holds, that it lacks), by first obstacle, "
              "draws pooled:\n")
        print("| obstacle | share |")
        print("|---|---|")
        for k, c in tot.most_common():
            print(f"| {k} | {c / s:.0%} |")


if __name__ == "__main__":
    main()
