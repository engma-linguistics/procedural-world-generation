"""After-run fronts of the watched techs, logged as live_run.py logs the live ones; then the two side by side. argv: run_dir"""
import json, pickle, sys
from pathlib import Path
from planet.lineages import techtree as TT
d = Path(sys.argv[1])
WATCH = {"towns", "tokens", "proto_writing", "writing", "cities", "kingship", "law", "chiefdoms"}
LOG = {}
_adv = TT.Calendar.advance
def advance(self, to=None):
    # step one at a time to log the step when each front is fixed
    n = 0
    while self.grid is None or self.step < len(self.grid):
        before = set(self.arrive)
        km = {(a, b): k for a, b, fr, t, k in self.links} | {(b, a): k for a, b, fr, t, k in self.links}
        frs = {(a, b): fr for a, b, fr, t, k in self.links} | {(b, a): fr for a, b, fr, t, k in self.links}
        st = self.step
        if self.grid is None:
            r = _adv(self, 1e12)  # (fix the grid, run nothing past the first step)
        g = self.grid[self.step] if self.step < len(self.grid) else None
        if g is None:
            break
        r = _adv(self, g)
        n += r
        for k3 in set(self.arrive) - before:
            if k3[2] in WATCH:
                x, y, t = k3
                LOG[k3] = {"step": st, "ago": g, "km": km.get((x, y)), "fr": frs.get((x, y)), "area": TT._area_at(self.series[y], g),
                           "giver_at": (self.known[x].get(t) or [None])[0], "arrive": self.arrive[k3], "unit": self.unit.get((x, y))}
    return n
TT.Calendar.advance = advance
after = TT.rebuild(d)
live = pickle.loads((d / "l195_log.pkl").read_bytes())["fronts"]
pickle.dump(LOG, open(sys.argv[2], "wb"))
r = lambda v: {k: (round(float(x), 3) if isinstance(x, (float, int)) and x is not None and not isinstance(x, bool) else x) for k, x in v.items()}
for k3 in sorted(set(live) | set(LOG), key=lambda k: -max((v.get(k) or {}).get("giver_at") or 0 for v in (live, LOG))):
    if k3[1] not in ("gnome", "fire_giant", "human", "tortle") and k3[0] not in ("gnome",):
        continue
    print(k3, "\n  live ", r(live[k3]) if k3 in live else None, "\n  after", r(LOG[k3]) if k3 in LOG else None)
