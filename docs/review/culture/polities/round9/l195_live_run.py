"""A peoples run with polities in the history on (scratch data root via PLANET_DATA), instrumented: for each front of the watched
techs, the inputs the live calendar used when it fixed it (border km, taker's area, the giver's date). Pickled beside the run.
argv: tree seed [arms] [out tag]"""
import math, os, pickle, sys, time
import numpy as np
from planet.lineages.history import params as HP
from planet.lineages import techtree as TT
from planet.lineages import run as LR

HP.POLITIES_LIVE = True
tree_name, seed = sys.argv[1], int(sys.argv[2])
arms = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
tag = sys.argv[4] if len(sys.argv) > 4 else f"{tree_name}{seed}"
WATCH = {"towns", "tokens", "proto_writing", "writing", "cities", "kingship", "law", "chiefdoms"}
LOG = {"fronts": {}, "feeds": [], "steps": 0}
if arms:  # (a test override: the tree's default arms)
    _load = TT.load
    def load(path=None):
        T = _load(path)
        T["defaults"]["contact_arms"] = arms
        return T
    TT.load = load

_adv = TT.Calendar.advance
def advance(self, to=None):
    if not getattr(self, "_live", False):
        return _adv(self, to)
    before = set(self.arrive)
    km = {(a, b): k for a, b, fr, t, k in self.links} | {(b, a): k for a, b, fr, t, k in self.links}
    frs = {(a, b): fr for a, b, fr, t, k in self.links} | {(b, a): fr for a, b, fr, t, k in self.links}
    st = self.step
    n = _adv(self, to)
    ago = self.grid[min(self.step, len(self.grid)) - 1] if n else None
    for k3 in set(self.arrive) - before:
        if k3[2] in WATCH:
            x, y, t = k3
            LOG["fronts"][k3] = {"step": st, "ago": ago, "km": km.get((x, y)), "fr": frs.get((x, y)),
                                 "area": TT._area_at(self.series[y], ago if ago is not None else 0.0),
                                 "giver_at": (self.known[x].get(t) or [None])[0], "arrive": self.arrive[k3], "unit": self.unit.get((x, y))}
    return n
TT.Calendar.advance = advance
_init = TT.Calendar.__init__

from planet.lineages.history import tech_live as TL
_step = TL.LiveTech.step
def step(self, s):
    _step(self, s)
    if self.cal is not None and not getattr(self.cal, "_live", False):
        self.cal._live = True
TL.LiveTech.step = step
_feed = TT.Calendar.feed
def feed(self, lines=None, links=None, forced=None, have=None, pops=None):
    if getattr(self, "_live", False) and have is not None:
        LOG["feeds"].append({"step": self.step, "have": {k: (sorted(v) if v is not None else None) for k, v in have.items()},
                             "n_links": len(links or [])})
    return _feed(self, lines, links, forced, have, pops)
TT.Calendar.feed = feed

tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run("899985", tree, 1, None, 30.0, f"l195-{tag}", progress=lambda f, msg: None)
print("run", out.name, round(time.time() - t0, 1), "s", flush=True)
(out / "l195_log.pkl").write_bytes(pickle.dumps(LOG))
