"""Round 24 (lane 281, PW-1596): where the first state comes from, with polities in the history on and off. Read-only.

argv: run_dir [--readout] [--held] [--calendar OTHER_RUN]
- the first state of the run's polities doc (derive: the live map when the run has polities_live.json), its seat, people, place and
  the seat people's gate techs (kingship, law, writing, cities) in the run's calendar;
- --readout: derive's own read-out even on a switch-on run (the live map hidden): the after-run seat test on that history;
- --held: _site_tables reads each site's kept series at the point at or before each step, not by straight lines between them;
- --calendar OTHER_RUN: that run's tech calendar (meta.techtree) in place of this run's.
For the first three states (by date) it also prints the site's kept series around the date, so a need crossed between two kept
points shows."""
import json
import sys
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO

GATE = ("chiefdoms", "kingship", "law", "writing", "cities", "towns")


def held_tables(R, agos):
    sites = R.S["sites"]
    tm_default = R.S["tiers"]["town_min_by_stage"][-1]
    A = np.asarray(agos, float)
    pop = np.zeros((len(sites), len(A)))
    for i, s in enumerate(sites):
        sr = s.get("series") or []
        if not sr:
            continue
        a = np.asarray([x for x, _ in sr], float)  # (oldest first: kyr ago falling)
        y = np.asarray([p for _, p in sr], float)
        j = np.searchsorted(-a, -A + 1e-9, side="right") - 1  # (the last kept point at or before each step)
        v = np.where(j >= 0, y[np.clip(j, 0, len(y) - 1)], y[0])
        v[A > s["founded_kyr"] + 1e-6] = 0
        if s.get("abandoned_kyr") is not None:
            v[A <= s["abandoned_kyr"] + 1e-6] = 0
        pop[i] = v
    _, holder, town_min = _orig(R, agos)
    return pop, holder, town_min


_orig = PO._site_tables


def main(argv):
    d = Path(argv[0])
    readout, held = "--readout" in argv, "--held" in argv
    cal = argv[argv.index("--calendar") + 1] if "--calendar" in argv else None
    if held:
        PO._site_tables = held_tables
    if readout:
        PO._from_live = None
        _ex = Path.exists
        Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    if cal:
        known = json.loads((Path(cal) / "run.json").read_text())["meta"]["techtree"]["known"]
        _init = PO._Run.__init__

        def init(self, rd):
            _init(self, rd)
            self.known = known
        PO._Run.__init__ = init
    D = PO.derive(d)
    R = PO._Run(d)
    if cal:
        R.known = known
    firsts = []
    for r in D["polities"]:
        st = [a for a, t in r.get("tiers") or [] if t in ("state", "empire")]
        if st:
            firsts.append((max(st), r))
    firsts.sort(key=lambda x: -x[0])
    print(f"== {d.name} readout={readout} held={held} calendar={cal and Path(cal).name}")
    for a, r in firsts[:3]:
        ppl = (r.get("peoples") or [[None, r.get("people")]])
        ppl = PO._at([[x[0], x[1]] for x in ppl], a)[1] if r.get("peoples") else r.get("people")
        cap = r["capital"]
        gate = {t: ((R.known.get(ppl) or {}).get(t) or [None])[0] for t in GATE}
        print(f"  state {a * 1000:,.0f} ya: {ppl} seat cell {cap['cell']} site {cap.get('site')} | gate techs (kyr ago) "
              + ", ".join(f"{t} {v if v is None else round(float(v), 3)}" for t, v in gate.items()))
        if cap.get("site") is not None:
            s = next(x for x in R.S["sites"] if x["id"] == cap["site"])
            ser = [(round(x, 3), round(p)) for x, p in s.get("series") or [] if a - 1.0 <= x <= a + 1.0]
            print(f"    site {s['id']} kind {s['kind']} founded {s['founded_kyr']} holder now {s.get('holder')}; kept series within 1 kyr: {ser}")


if __name__ == "__main__":
    main(sys.argv[1:])
