"""Lane 254: one peoples run in the lane's scratch data root, polities in the history on or off, languages skipped (round18's runner).
argv: tree seed live(on|off) tag kyr world [arm]. arm: base (the code as is), or feed=<run dir>: the diagnosis of PW-1597, the live
tech tree reads that (switch-off) run's ledger footprint (techspread.town_footprint) instead of the live seats' own town cells."""
import sys
import time

from planet.lineages.history import params as HP
from planet.lineages.history import tech_live as TL
from planet.lineages import run as LR
import planet.language.run as LANG


def _skip(out):
    raise RuntimeError("skipped by lane 254's runner")


LANG.write = _skip
tree_name, seed, live, tag, kyr, world = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6]
arm = sys.argv[7] if len(sys.argv) > 7 else "base"
HP.POLITIES_LIVE = live == "on"
if arm.startswith("feed="):
    from planet.lineages.techspread import town_footprint
    fp = town_footprint(arm[5:])
    fp = {k: (v if k == "_cell_km2" else (list(v[0]), list(v[1]))) for k, v in fp.items()}
    _init = TL.LiveTech.__init__

    def _init_feed(self, h):
        _init(self, h)
        if self.towns is not None:
            self.towns.clear()
            self.towns.update(fp)
    TL.LiveTech.__init__ = _init_feed
    TL.LiveTech.note_towns = lambda self, ago, cells: None
    print("ARM feed", arm[5:], len(fp) - 1, "peoples", flush=True)
if arm.startswith("feedlinks="):  # (diagnosis: the live tree reads that finished run's contacts as the after-run tree does, links_of)
    import json as _j
    from planet.lineages import techtree as TT
    _con = _j.loads((__import__("pathlib").Path(arm[10:]) / "run.json").read_text())["meta"]["contacts"]
    TL.LiveTech._links = lambda self: TT.links_of(_con, self.cal.kind)
    print("ARM feedlinks", arm[10:], flush=True)
if arm.startswith("feedtracks="):  # (diagnosis: the live tree reads that finished run's whole tracks, as the after-run tree does)
    import json as _j
    _tr = {l["id"]: l.get("track") for l in _j.loads((__import__("pathlib").Path(arm[11:]) / "run.json").read_text())["meta"]["lineages"]}
    _lines = TL.LiveTech.lines

    def _lines_feed(self):
        out = _lines(self)
        for l in out:
            if _tr.get(l["id"]):
                l["track"] = _tr[l["id"]]
        return out
    TL.LiveTech.lines = _lines_feed
    print("ARM feedtracks", arm[11:], flush=True)
if live == "on":  # (the footprint the live tree read, kept beside the logs: round19/footprint.py compares it with the ledger's)
    import json
    import os
    _result = TL.LiveTech.result

    def _result_dump(self, *a, **k):
        d = os.environ.get("L254_FOOT")
        if d and self.towns is not None:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{tag}.json"), "w") as f:
                json.dump({lid: v if lid == "_cell_km2" else [list(map(float, v[0])), list(map(float, v[1]))] for lid, v in self.towns.items()}, f)
        return _result(self, *a, **k)
    TL.LiveTech.result = _result_dump
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(world, tree, 1, None, kyr, f"l254-{tag}", progress=lambda f, msg: None)
print("RUN", tag, out, round(time.time() - t0, 1), "s", flush=True)
