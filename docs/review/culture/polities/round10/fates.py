"""Fates of the same conquests (ago, winner, loser) in two live-polities runs: a baseline and a branch; with a third arg, each non-kept
fate with the winner's [tolerance, aggression]. argv: base_run branch_run [v]"""
import json, sys
from collections import Counter
def rows(d):
    pl = json.load(open(f"{d}/polities_live.json"))
    out = {}
    for r in pl["polities"]:
        for t in r.get("took") or []:
            pass
    for s in pl["steps"]:
        for t in s.get("taken") or []:
            out.setdefault((round(s["ago"],3), t.get("winner_people") or t.get("winner"), t.get("loser_people") or t.get("loser")), []).append(t)
    return pl, out
pa, a = rows(sys.argv[1]); pb, b = rows(sys.argv[2])
print("keys of a taken entry:", list(next(iter(b.values()))[0].keys()))
c = Counter()
for k, ts in sorted(b.items(), key=lambda x: -x[0][0]):
    for t in ts:
        fb = t.get("fates") or {}
        fa = {}
        for ta in a.get(k, []): fa.update(ta.get("fates") or {})
        for p, (f, n) in fb.items():
            c[(fa.get(p, ["-"])[0], f)] += 1
            if f != "kept" and len(sys.argv) > 3: print(k, t.get("winner_att"), p, fa.get(p), [f, n])
print(c)
