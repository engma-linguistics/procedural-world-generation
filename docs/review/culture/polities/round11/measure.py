"""Round 11's measures (lane 204) of live-polities peoples runs (polities_live.json, run.json). argv: run_dir [run_dir ...].
Per run: the scheduled rows (happened, conquests, expeditions and their km), conquests (war / invasion), the fates of the peoples on
taken land (kept / thinned / expelled, heads lost) by the winner's tolerance x aggression at the conquest (winner_att), states over
time, the largest shares and the first writing dates. Round 10's measure.py, plus the aggression split (PW-1487)."""
import json
import sys
from collections import Counter
from pathlib import Path

WRITE = ("writing", "kingship", "law", "cities")


def cell(att):
    if att is None:
        return "n/a"
    t, a = att[0], att[1]
    return ("intolerant" if t < 0.5 else "tolerant") + "/" + ("martial" if a >= 0.45 else "plain")


def main(dirs):
    for d in dirs:
        d = Path(d)
        pl = json.loads((d / "polities_live.json").read_text())
        run = json.loads((d / "run.json").read_text())
        print(f"=== {d.name} ({run.get('name')})  live step s {pl.get('made_s')}  CAMPAIGN_KM {pl.get('constants', {}).get('CAMPAIGN_KM')}")
        for r in pl["invasions"]:
            lg = r["log"]
            took = lg.get("took") or []
            ex = lg.get("exped") or []
            km = sorted(e["km"] for e in ex)
            print(f"  row {r['row']['id']:14s} happened {bool(took)!s:5s} took {len(took):3d} km2 {sum(t[3] for t in took):12,.0f} exped {len(ex):3d}"
                  f" km {km[0] if km else '-'}..{km[-1] if km else '-'} miss {lg.get('exped_fail', 0):3d}"
                  f" need {lg.get('exped_need', lg.get('exped_need_gt', '-'))} war_band {len(lg.get('war_band') or [])}")
        how = Counter()
        fates, lost = {}, {}
        for s in pl["steps"]:
            for t in s.get("taken") or []:
                how[t["how"]] += 1
                b = cell(t.get("winner_att"))
                for _p, (f, n) in (t.get("fates") or {}).items():
                    fates.setdefault(b, Counter())[f] += 1
                    lost.setdefault(b, Counter())[f] += n
        print("  conquests", dict(how))
        tf, tl = Counter(), Counter()
        for b in sorted(fates):
            tf.update(fates[b])
            tl.update(lost[b])
            print(f"  fates {b:20s} kept {fates[b]['kept']:4d} thinned {fates[b]['thinned']:3d} expelled {fates[b]['expelled']:3d}"
                  f"  heads lost {sum(lost[b].values()):9,d}")
        print(f"  fates all                  kept {tf['kept']:4d} thinned {tf['thinned']:3d} expelled {tf['expelled']:3d}  heads lost {sum(tl.values()):9,d}")
        pick = {}
        for s in pl["steps"]:
            for a in (2.0, 1.0, 0.5, 0.0):
                if a not in pick or abs(s["ago"] - a) < abs(pick[a]["ago"] - a):
                    pick[a] = s
        print("  states (ago: n, largest Mkm2 people)", "; ".join(f"{a}: {s['states']}, {s['largest_mkm2']} {s['largest_people']}"
                                                         for a, s in sorted(pick.items(), reverse=True)))
        meta = run.get("meta") or {}
        grp = {ln["id"]: ln.get("group_of") for ln in meta.get("lineages") or []}
        meg = {ln["id"] for ln in meta.get("lineages") or [] if ln.get("megafauna") or ln.get("overlay")}
        pop = Counter()
        for lid, v in ((meta.get("present") or {}).get("lines") or {}).items():
            if v.get("overlay") or lid in meg:
                continue
            pop[grp.get(lid) or lid] += float(v.get("population") or 0)
        tot = sum(pop.values()) or 1.0
        print("  shares %", ", ".join(f"{p} {100 * n / tot:.1f}" for p, n in pop.most_common(6)))
        kn = (meta.get("techtree") or {}).get("known") or {}
        first = {t: max((float(v[t][0]) for v in kn.values() if v.get(t)), default=None) for t in WRITE}
        print("  first anyone (kyr ago)", {t: (round(v, 3) if v is not None else None) for t, v in first.items()})


if __name__ == "__main__":
    main(sys.argv[1:])
