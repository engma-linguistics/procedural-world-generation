"""Attitudes v0 (PW-904): each culture's general temperament on two axes, followed through its history. Read-out only, like gods.py.

In plain words: every culture has a **tolerance** (0..1: how it bears outsiders and other faiths; high: Cyrus letting the exiles go
home and rebuild their temples, low: forced conversion, expulsion) and an **aggression** (0..1: how far it seeks to expand by war;
high: a conqueror's horde, low: a people that keeps to its own land). Daniel's framing (D54, 2026-11-04): history has everything
from Genghis Khan razing cities to Cyrus the Great's tolerance, in any era, so the axes vary by culture and over time, never by era.

Where the numbers come from (every number here is a JUDGEMENT, a first guess; the point is the ordering and that each follows from
the tree or the culture's own history):
- Its people's temperament from the tree: tolerance falls with the people's insularity (spec.DEMOGRAPHY; the same number that sets
  how readily peoples live beside each other, compose.py) and rises for `cosmopolitan` peoples; aggression rises with `aggressive`
  (the spread's push), the contest strength of `martial` peoples (dwarves, hobgoblins: demography contest 1.5) and a mobile herding
  life (`nomadic`, or the pastoral_nomad way). A trade axis is not separate: openness to trade is the insularity the tree already has.
- Each culture differs: a seeded offset per culture (OFFSET_SD), kept for its life, and a daughter starts from its parent's values.
- Its history moves the point it drifts toward (each a memory that fades with TAU_MEM):
  * conquest: a culture whose state took land by war grows more aggressive (WIN_AGG: success feeds expansion);
  * rule over many: a ruling culture with several subject cultures grows a little more tolerant (EMPIRE_TOL: the pragmatic tolerance
    of the many-peopled empires, the Achaemenids', the Mongols');
  * subjection: a culture under a foreign ruler grows a little less aggressive (SUBJECT_AGG);
  * contact: a culture in touch with many others grows more tolerant, an isolated one less (CONTACT_TOL over CONTACT_FULL);
  * faith: a culture whose faith seeks converts (missionary, gods.py) is a little less tolerant of other faiths (MISSION_TOL).
- Drift: around that point each axis wanders (an Ornstein-Uhlenbeck walk: e-folding TAU_ATT, spread DRIFT_SD), so a culture can
  turn from tolerant to harsh within centuries and back, as any history does.

Grudges between named peoples, xenophobia by species, forgiveness and stubbornness (the rest of PW-904) are not in v0.
"""

from __future__ import annotations

import math

import numpy as np

AXES = ("tolerance", "aggression")
TOL_BASE, TOL_INSULAR, TOL_COSMO = 0.8, 0.6, 0.1  # JUDGEMENT: tolerance 0.8 - 0.6 x insularity (+0.1 cosmopolitan): humans (0.3) 0.72, elves (0.7) 0.38, dragons (0.85) 0.29
AGG_BASE, AGG_AGGRESSIVE, AGG_CONTEST, AGG_NOMAD = 0.3, 0.2, 0.4, 0.1  # JUDGEMENT: aggression 0.3 (+0.2 aggressive, +0.4 x (contest - 1): martial 1.5 -> +0.2, +0.1 nomadic herders)
OFFSET_SD = 0.1  # JUDGEMENT: each culture's own lasting offset from its people's temperament
TAU_ATT, DRIFT_SD = 0.5, 0.1  # kyr, JUDGEMENT: the axes wander about their point with this e-folding and spread (centuries, not eras)
TAU_MEM = 0.5  # kyr, JUDGEMENT: a conquest or a subjection is felt for centuries, then fades
WIN_AGG = 0.15  # JUDGEMENT: a culture whose state took land by war, at full memory
EMPIRE_TOL, EMPIRE_FULL = 0.05, 5  # JUDGEMENT: a ruling culture with this many subject cultures, at full
SUBJECT_AGG = 0.05  # JUDGEMENT: a culture under a foreign ruler, at full memory
CONTACT_TOL, CONTACT_FULL = 0.1, 6  # JUDGEMENT: tolerance -0.05 alone .. +0.05 with this many cultures in touch
MISSION_TOL = 0.05  # JUDGEMENT: a culture of a missionary faith
TRACK_KYR = 0.5  # (a sample of each culture's axes at most this often, for the read-out)


def _c(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def temperament(line: dict | None) -> tuple[float, float]:
    """A people's starting (tolerance, aggression) from its tree entry (run meta lineages: traits, demography, way)."""
    line = line or {}
    tr = set(line.get("traits") or ())
    demo = line.get("demography") or {}
    ins = float(demo.get("insularity", 0.85 if "insular" in tr else 0.3 if "cosmopolitan" in tr else 0.5))
    contest = float(demo.get("contest", 1.5 if "martial" in tr else 1.0))
    way = line.get("way") or ""
    tol = TOL_BASE - TOL_INSULAR * ins + (TOL_COSMO if "cosmopolitan" in tr else 0.0)
    agg = (AGG_BASE + (AGG_AGGRESSIVE if "aggressive" in tr else 0.0) + AGG_CONTEST * max(0.0, contest - 1.0)
           + (AGG_NOMAD if ("nomadic" in tr or "pastoral_nomad" in str(way)) else 0.0))
    return _c(tol), _c(agg)


class Attitudes:
    """The two axes of every culture, stepped frame by frame (oldest first). No I/O."""

    def __init__(self, lines: dict | None = None, seed: int = 0):
        self.lines = lines or {}
        self.rng = np.random.default_rng((int(seed), 904))
        self.x: dict[int, np.ndarray] = {}  # culture -> [tolerance, aggression] now
        self.off: dict[int, np.ndarray] = {}  # culture -> its lasting offset
        self.people: dict[int, str] = {}
        self.mem: dict[int, dict] = {}  # culture -> {"win", "sub", "rule_n"} memories 0..1
        self.track: dict[int, list] = {}
        self.base: dict[str, tuple] = {}

    def _base(self, people: str) -> np.ndarray:
        if people not in self.base:
            self.base[people] = temperament(self.lines.get(people))
        return np.array(self.base[people], float)

    def ensure(self, c: int, people: str, parent: int | None = None):
        if c in self.x:
            return
        self.people[c] = people
        self.off[c] = self.rng.normal(0.0, OFFSET_SD, 2)
        if parent is not None and parent in self.x:
            self.x[c] = self.x[parent].copy()
        else:
            self.x[c] = np.clip(self._base(people) + self.off[c], 0.0, 1.0)
        self.mem[c] = {"win": 0.0, "sub": 0.0, "rule_n": 0}

    def get(self, c: int) -> tuple[float, float]:
        v = self.x.get(c)
        return (0.5, 0.3) if v is None else (float(v[0]), float(v[1]))

    def tolerance(self, c: int) -> float:
        return self.get(c)[0]

    def won(self, c: int):
        if c in self.mem:
            self.mem[c]["win"] = 1.0

    def ruled(self, c: int, n_subjects: int):
        if c in self.mem:
            self.mem[c]["rule_n"] = max(self.mem[c]["rule_n"], int(n_subjects))

    def subject(self, c: int):
        if c in self.mem:
            self.mem[c]["sub"] = 1.0

    def target(self, c: int, n_contacts: int, missionary: bool) -> np.ndarray:
        m = self.mem[c]
        t = self._base(self.people[c]) + self.off[c]
        t[0] += CONTACT_TOL * (min(1.0, n_contacts / CONTACT_FULL) - 0.5) + EMPIRE_TOL * min(1.0, m["rule_n"] / EMPIRE_FULL)
        t[0] -= MISSION_TOL if missionary else 0.0
        t[1] += WIN_AGG * m["win"] - SUBJECT_AGG * m["sub"]
        return t

    def step(self, ago: float, dt: float, present: dict, n_contacts: dict, missionary: set):
        """present: culture -> people for the cultures on the map now; n_contacts: culture -> cultures in touch; missionary: the
        cultures whose faith seeks converts."""
        for c, people in present.items():
            self.ensure(c, people)
            if dt > 0:
                k = math.exp(-dt / TAU_ATT)
                t = self.target(c, n_contacts.get(c, 0), c in missionary)
                noise = self.rng.normal(0.0, DRIFT_SD * math.sqrt(1.0 - k * k), 2)
                self.x[c] = np.clip(t + (self.x[c] - t) * k + noise, 0.0, 1.0)
                f = math.exp(-dt / TAU_MEM)
                m = self.mem[c]
                m["win"] *= f
                m["sub"] *= f
                m["rule_n"] = 0
            tr = self.track.setdefault(c, [])
            if not tr or abs(tr[-1][0] - ago) >= TRACK_KYR - 1e-9:
                tr.append([round(float(ago), 3), round(float(self.x[c][0]), 3), round(float(self.x[c][1]), 3)])

    def doc(self) -> dict:
        """The read-out: per culture its people's temperament and its track [[kyr ago, tolerance, aggression], ...]."""
        cs = {str(c): {"people": self.people[c], "now": [round(float(v), 3) for v in self.x[c]], "track": self.track.get(c, [])}
              for c in sorted(self.x)}
        tol = np.array([v[0] for v in self.x.values()]) if self.x else np.zeros(0)
        agg = np.array([v[1] for v in self.x.values()]) if self.x else np.zeros(0)
        q = lambda a: [round(float(x), 3) for x in np.quantile(a, (0.1, 0.5, 0.9))] if len(a) else []  # noqa: E731
        return {"axes": list(AXES), "rule": RULE, "peoples": {p: [round(a, 3), round(b, 3)] for p, (a, b) in sorted(self.base.items())},
                "cultures": cs, "summary": {"cultures": len(cs), "tolerance_q10_50_90": q(tol), "aggression_q10_50_90": q(agg)},
                "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))}}


RULE = ("Each culture has a tolerance (of outsiders and other faiths) and an aggression (the drive to expand by war), 0 to 1. They start "
        "from its people's temperament in the tree (insular peoples less tolerant, cosmopolitan ones more; aggressive, martial and "
        "herding peoples more aggressive) plus the culture's own lasting offset, and wander over centuries about a point its history "
        "moves: taking land by war raises aggression, ruling many peoples raises tolerance a little, living under a foreign ruler lowers "
        "aggression, wide contact raises tolerance and isolation lowers it, a missionary faith lowers tolerance a little. A ruler's "
        "tolerance sets how hard it pushes its faith on its subjects.")
