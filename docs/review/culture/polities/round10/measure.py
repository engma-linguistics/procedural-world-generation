"""Round 10's measures of one or more peoples runs with polities in the history on (polities_live.json, run.json).
argv: run_dir [run_dir ...]. Per run: the scheduled rows (happened, how: border, expedition, war band), conquests (war / invasion) and
the fates of the peoples on taken land (kept / thinned / expelled, heads lost) by the winner's tolerance, states over time, and the
tech calendar's writing dates of the largest peoples."""
import json
import sys
from collections import Counter
from pathlib import Path

WRITE = ("writing", "kingship", "law", "cities")


def load(d):
    d = Path(d)
    pl = json.loads((d / "polities_live.json").read_text())
    run = json.loads((d / "run.json").read_text())
    return pl, run


def tol_bin(att):
    if att is None:
        return "n/a (main)"
    t = att[0]
    return "tol < 0.4" if t < 0.4 else ("tol 0.4-0.6" if t < 0.6 else "tol >= 0.6")


def main(dirs):
    for d in dirs:
        pl, run = load(d)
        print(f"=== {Path(d).name} ({run.get('name')})")
        print("live step s", pl.get("made_s"), "tech s", pl.get("tech_s"), "constants", pl.get("constants", {}).get("CAMPAIGN_KM", "-"),
              pl.get("constants", {}).get("AGG_MID", "-"))
        for r in pl["invasions"]:
            lg = r["log"]
            took = lg.get("took") or []
            ex = lg.get("exped") or []
            print(f"  row {r['row']['id']:14s} happened {bool(took)!s:5s} took {len(took):3d} km2 {sum(t[3] for t in took):12,.0f} exped {len(ex):3d}"
                  f" (km {', '.join(str(e['km']) for e in ex[:6])}) exped_fail {lg.get('exped_fail', 0):3d} need_km {lg.get('exped_need', '-')}"
                  f" war_band {len(lg.get('war_band') or [])} steps {lg.get('steps')} state {lg.get('state')} victim {lg.get('victim')} border {lg.get('border')}")
        how = Counter()
        fates = {}
        lost = {}
        for s in pl["steps"]:
            for t in s.get("taken") or []:
                how[t["how"]] += 1
                b = tol_bin(t.get("winner_att"))
                for p, (f, n) in (t.get("fates") or {}).items():
                    fates.setdefault(b, Counter())[f] += 1
                    lost.setdefault(b, Counter())[f] += n
        print("  conquests", dict(how))
        for b in sorted(fates):
            print(f"  fates {b:12s}", dict(fates[b]), "heads lost", dict(lost[b]))
        pick = {}
        for s in pl["steps"]:
            for a in (3.0, 2.0, 1.0, 0.5, 0.0):
                if a not in pick or abs(s["ago"] - a) < abs(pick[a]["ago"] - a):
                    pick[a] = s
        print("  states (ago: states, largest Mkm2 people, ruled Mkm2, collapsed this step)",
              "; ".join(f"{a}: {s['states']}, {s['largest_mkm2']} {s['largest_people']}, {s['ruled_mkm2']}" for a, s in sorted(pick.items(), reverse=True)))
        tt = (run.get("meta") or {}).get("techtree") or {}
        kn = tt.get("known") or {}
        meta = run.get("meta") or {}
        grp = {ln["id"]: ln.get("group_of") for ln in meta.get("lineages") or []}
        meg = {ln["id"] for ln in meta.get("lineages") or [] if ln.get("megafauna") or ln.get("overlay")}
        pop = Counter()
        for lid, v in ((meta.get("present") or {}).get("lines") or {}).items():
            if v.get("overlay") or lid in meg:
                continue
            pop[grp.get(lid) or lid] += float(v.get("population") or 0)
        tot = sum(pop.values()) or 1.0
        print("  shares %", ", ".join(f"{p} {100 * n / tot:.1f}" for p, n in pop.most_common(8)))
        first = {t: max((float(v[t][0]) for v in kn.values() if v.get(t)), default=None) for t in WRITE}
        print("  first anyone (kyr ago)", {t: (round(v, 3) if v is not None else None) for t, v in first.items()})
        print("  writing by people", {p: round(float(kn[p]["writing"][0]), 3) for p in sorted(kn) if kn[p].get("writing")})
        att = pl.get("attitudes")
        if att:
            print("  attitudes summary", att.get("summary"), "peoples", {p: v for p, v in list(att.get("peoples", {}).items())[:40]})


if __name__ == "__main__":
    main(sys.argv[1:])
