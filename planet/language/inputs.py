"""The language engine's view of a stored peoples run (PW-986): one `Run` opens a run directory once and answers every question
the driver asks (history.py), at the 41 frames of the last 20 kyr (0.5 kyr apart, kyr ago, larger = older).

Nothing at deme level is stored about who ruled, spoke or traded with whom, so this module derives it (docs/review/language/
inputs.md, "GAPs"): deme cells and populations per frame from the presence table and `layers/demes_all.bin`; contacts per frame
from co-presence (cells both demes live in) and borders (land edges between cells whose leading demes differ), computed afresh at
full resolution rather than interpolated from the thinned `pairs` series (which keeps only the top 3000 pairs); shift triggers
from incursions (located through demes_all), settlement changes of hands, mixed cities, swamping (a deme living mostly inside a
more numerous other people's deme) and long trade contact; crop and animal arrivals per deme from the `crop_known` and
`animal_known` bits; rivers and lakes from the world's `downstream`, `flow` and `lake` layers.

Read-only: nothing here writes to the run."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import numpy as np

from .. import store as S
from ..grid import shared_grid

START_KYR = 20.0
STEP_KYR = 0.5
NONE = 65535
R_KM = 6371.0

RIVER_FLOW = 50.0  # world `flow` floor for a river cell (m^3/s as stored; ~2,200 cells on dba204)
RIVER_MIN_CELLS = 3  # river cells (above the floor) a basin needs to count as a river
INCURSION_TAIL_KYR = 1.0  # elite rule outlasts the incursion's own span by this much
INCURSION_RADIUS_KM = 150.0  # added to the incursion's own radius when locating the demes involved
TAKEOVER_SITES = 2  # settlement takeovers per (ruler, ruled) frame that count as rule (or one town/city)
TOWN_POP, CITY_POP = 1000, 10000
SWAMP_INSIDE = 0.6  # share of a deme's cells inside another people's deme for swamping
SWAMP_RATIO = 2.0  # ... where that deme holds this many times more of the habitat, and this many times the people
TRADE_SHIFT_KYR = 3.0  # continuous contact before trade raises a shift pressure
TRADE_SHARED = 0.25  # shared-cell share (of the smaller deme) for a trade link
L2_SHARED = 0.6  # adult-L2 proxy: weight of other peoples' presence on a deme's cells
L2_MAX = 0.7  # ... and its ceiling (the share of heads in mixed cities is added before the clip)
PRESTIGE_TECHS = ("cities", "writing", "law")


@dataclass
class Trigger:
    """A reason for a deme (ruled) to take up another deme's (ruler) speech, active from start_kyr to end_kyr (kyr ago)."""
    kind: str  # elite | swamp | takeover | city | trade
    ruler_deme: int
    ruled_deme: int
    start_kyr: float
    end_kyr: float
    strength: float  # 0..1, multiplies the shift rate
    source: str  # plain words: where this came from in the stored history

    def to_json(self) -> dict:
        return {"kind": self.kind, "ruler_deme": self.ruler_deme, "ruled_deme": self.ruled_deme, "start_kyr": self.start_kyr,
                "end_kyr": self.end_kyr, "strength": round(self.strength, 3), "source": self.source}


@dataclass
class Frame:
    """One frame's deme cells, shares and contacts."""
    kyr: float
    run_index: int
    cells: dict = field(default_factory=dict)  # deme -> cell ids (int64)
    shares: dict = field(default_factory=dict)  # deme -> % of habitat (float)
    pairs: dict = field(default_factory=dict)  # (a, b) a < b -> [shared cells, border edges, share sum a, share sum b]


GEN_TOL = 0.05  # yr: a current-spec generation length this close to the stored one is not an override


def current_spec(meta: dict):
    """The current preset spec (lineages.spec.Tree) of a run: the file of the stored tree_file's name in this checkout's
    planet/lineages/samples, or None (a run built from a tree file that is not a preset keeps its stored lengths)."""
    tf = meta.get("tree_file")
    if not tf:
        return None
    from ..lineages import spec as SP
    p = Path(__file__).resolve().parents[1] / "lineages" / "samples" / Path(tf).name
    if not p.exists():
        return None
    try:
        return SP.load(p, meta.get("mode"))
    except Exception:  # noqa: BLE001 - a preset that no longer parses: keep the stored lengths
        return None


def line_generation_yr(tree, l) -> float:
    """A line's generation length, yr, as lineages.history.peoples.PeoplesMixin.gen_yr computes it."""
    if l.megafauna and "flies" in l.traits:
        from ..lineages import dragon_ages as DA
        return float(DA.generation_yr(tree.dragon_ages, tree.dragon_generation, l.generation_yr))
    from ..lineages import life_history as LH
    return float(LH.generation_yr(l))


def generation_overrides(meta: dict, lines: dict, tree=None) -> dict:
    """See Run.generation_overrides; `tree` (a spec.Tree) instead of the current preset, for tests."""
    tree = tree if tree is not None else current_spec(meta)
    if tree is None:
        return {}
    out = {}
    for lid, ln in lines.items():
        sl = tree.lines.get(lid)
        stored = ln.get("generation_yr")
        if sl is None or stored is None:
            continue
        cur = line_generation_yr(tree, sl)
        if abs(cur - float(stored)) > GEN_TOL:
            out[lid] = {"stored_yr": round(float(stored), 2), "current_yr": round(cur, 2), "spec": tree.source}
    return out


def _people_of_line(lines_by_id: dict, lid: str) -> str | None:
    """A group's or overlay's people for deme lookups (groups map to their people; overlays have no demes)."""
    l = lines_by_id.get(lid)
    if l is None:
        return None
    if l.get("group_of"):
        return l["group_of"]
    return lid


class Run:
    """A peoples run opened once for the language pass."""

    def __init__(self, run_dir, world_layers: dict | None = None, settlements: dict | None = None, load_world: bool = True):
        self.dir = Path(run_dir)
        self.run = json.loads((self.dir / "run.json").read_text())
        self.meta = self.run["meta"]
        self.id = self.run.get("id") or self.dir.name
        self.seed = int(self.meta.get("seed") or 0)
        self.demes_doc = json.loads((self.dir / "demes.json").read_text())
        self.demes = self.demes_doc["demes"]
        cp = self.dir / "cultures.json"
        self.cultures_doc = json.loads(cp.read_text()) if cp.exists() else None
        self._settlements = settlements
        self.lines = {l["id"]: l for l in self.meta["lineages"]}
        self.line_index = {l["id"]: l["index"] for l in self.meta["lineages"]}
        self.index_line = {l["index"]: l["id"] for l in self.meta["lineages"]}
        self.level = int(self.meta.get("level", 7))
        self.n = int(self.meta.get("cells") or 0)
        self.g = shared_grid(self.level)
        self.n = self.g.n
        self.cell_km2 = 4 * math.pi * R_KM ** 2 / self.n
        ts = [f["t"] for f in self.run["frames"]]
        ago_to_run = {}
        for i, t in enumerate(ts):
            ago_to_run[round(-t, 3)] = i  # (the later index on a repeat)
        nf = int(round(START_KYR / STEP_KYR)) + 1
        self.frames_kyr = [round(START_KYR - STEP_KYR * i, 3) for i in range(nf)]
        missing = [k for k in self.frames_kyr if k not in ago_to_run]
        if missing:
            raise ValueError(f"run {self.id} lacks frames at {missing[:5]} kyr ago")
        self.run_frame = [ago_to_run[k] for k in self.frames_kyr]
        self._world_layers = world_layers
        self._load_world = load_world
        self._frames: list[Frame | None] = [None] * nf
        self._lead = S.read_layers(self.dir, self.run["layers"], ["demes", "crop_known", "animal_known"])
        self._open_presence()

    # ------------------------------------------------------------------ basics
    def culture_rules(self, deme: int | None) -> frozenset | None:
        """The taboo rule ids (kinship, speech, ...; not food) of the deme's culture now (cultures.json deme_culture,
        taboos.json). A taboos.json from before the non-food rules (format procgen-taboos/1) is re-derived in memory,
        read-only (planet.lineages.taboos.derive). None when the run has no cultures."""
        if not hasattr(self, "_culture_rules"):
            self._culture_rules = {}
            dc = (getattr(self, "cultures_doc", None) or {}).get("deme_culture") or []
            doc = None
            if dc and getattr(self, "dir", None) is not None:
                tp = Path(self.dir) / "taboos.json"
                try:
                    doc = json.loads(tp.read_text()) if tp.exists() else None
                    if doc is None or not any(t.get("kind") for c in doc.get("cultures", {}).values() for t in c.get("taboos") or []):
                        from planet.lineages import taboos as TB
                        gp = Path(self.dir) / "gods.json"
                        doc = TB.derive(Path(self.dir), json.loads(gp.read_text()) if gp.exists() else None)
                except Exception:   # noqa: BLE001 - no culture steering then
                    doc = None
            cu = (doc or {}).get("cultures") or {}
            self._culture_rules = {"dc": dc, "by": {k: frozenset(t["target"] for t in v.get("taboos") or [] if t.get("kind") not in (None, "food"))
                                                    for k, v in cu.items()}}
        cr = self._culture_rules
        if deme is None or not cr["by"] or deme >= len(cr["dc"]) or cr["dc"][deme] is None:
            return None
        return cr["by"].get(str(cr["dc"][deme]))

    def gods_doc(self) -> dict | None:
        """The run's gods.json (gods, faiths, cultures' faiths). One from before the faith records (no "faiths": format
        procgen-gods/1) is re-derived in memory, read-only (planet.lineages.gods.derive: about 2 minutes on a24559).
        None without one (no cultures, or a run held in memory: tests set `_gods_doc`)."""
        if "_gods_doc" not in self.__dict__:
            doc = None
            d = getattr(self, "dir", None)
            if d is not None and getattr(self, "cultures_doc", None):
                gp = Path(d) / "gods.json"
                try:
                    doc = json.loads(gp.read_text()) if gp.exists() else None
                    if doc is None or not (doc.get("faiths") or {}).get("list"):
                        from planet.lineages import gods as GD
                        doc = GD.derive(Path(d))
                except Exception:   # noqa: BLE001 - no faiths then
                    doc = None
            self.__dict__["_gods_doc"] = doc
        return self.__dict__["_gods_doc"]

    def kyr(self, i: int) -> float:
        return self.frames_kyr[i]

    def frame_of(self, kyr: float) -> int:
        """The local frame index nearest a time (kyr ago), clamped to the window."""
        return int(min(max(round((START_KYR - kyr) / STEP_KYR), 0), len(self.frames_kyr) - 1))

    def people_of(self, deme: int) -> str:
        return self.demes[deme]["people"]

    def line(self, people: str) -> dict:
        return self.lines[people]

    def generation_yr(self, people: str) -> float:
        """The people's generation length, yr: the current preset's (generation_overrides) where it differs from the one the run
        stored, else the stored one."""
        ov = self.generation_overrides.get(people)
        if ov is not None:
            return float(ov["current_yr"])
        return float(self.lines[people].get("generation_yr") or 25.0)

    @cached_property
    def generation_overrides(self) -> dict:
        """{people: {"stored_yr", "current_yr", "spec"}} for the peoples whose generation length under the current preset spec
        differs from the run's stored one (by more than GEN_TOL): a preset change made after the peoples run (aarakocra adult 12,
        lifespan 60, owner 11-04) reaches the language pass without rebuilding the run. Computed as the lineages code does
        (history.peoples.PeoplesMixin.gen_yr): a flying megafauna line's from the dragons' age schedule, else the canon-age
        life table's T under the forager schedule, else the line's own generation_yr. The spec is the preset of the same file
        name in this checkout's planet/lineages/samples (the stored tree_file path may point at another checkout), else none."""
        return generation_overrides(self.meta, self.lines)

    def density(self, people: str) -> float:
        """Heads per km2: the people's present population over its present area (meta.present.lines). The stored
        `demography.density` is the density ladder's factor, not heads per km2 (red dragons 0.6 there, 0.0003 in fact), so it
        is the fallback only, for a people with no present record."""
        if not hasattr(self, "_dens"):
            self._dens = {}
        if people not in self._dens:
            pl = ((self.meta.get("present") or {}).get("lines") or {}).get(people) or {}
            pop, a = pl.get("population"), pl.get("area_mkm2")
            if pop and a:
                self._dens[people] = float(pop) / (float(a) * 1e6)
            else:
                self._dens[people] = float((self.lines[people].get("demography") or {}).get("density") or 1.0)
        return self._dens[people]

    def is_arrival(self, people: str) -> bool:
        return self.lines[people].get("origin") == "arrival"

    def parent_deme(self, deme: int) -> int | None:
        """The deme a deme's speech descends from: its deme parent, except an arrival people's first demes (whose stored parent is
        merely the deme that led those cells before) and a new people's first deme whose parent people is not its tree parent."""
        d = self.demes[deme]
        p = d.get("parent")
        if p is None:
            return None
        if d.get("parent_people") and d["parent_people"] != d["people"]:
            if self.is_arrival(d["people"]):
                return None
            if d["parent_people"] not in (self.lines[d["people"]].get("parents") or []):
                return None
        return int(p)

    def profile(self, people: str):
        """The people's voice profile (profiles.resolve_profile along its first-parent chain, a group following its people; a
        line's own spec `voice` table when the stored tree has one); the human default for an unknown people."""
        from . import profiles as PR

        def parents(l: str) -> list[str]:
            ln = self.lines.get(l)
            if ln is None:
                return []
            if ln.get("group_of"):
                return [ln["group_of"]]
            return list(ln.get("parents") or [])
        given = {r.get("id"): r.get("voice") for r in ((self.meta.get("tree") or {}).get("lineage") or []) if r.get("voice")}
        if people not in self.lines:
            return PR.HUMAN
        return PR.resolve_profile(people, parents, lambda l: given.get(l))

    def alive_at(self, deme: int, kyr: float) -> bool:
        d = self.demes[deme]
        e = d.get("ended_kyr")
        return d["born_kyr"] >= kyr - 1e-9 and (e is None or e < kyr - 1e-9)

    def demes_alive(self, i: int) -> list[int]:
        """Demes alive at local frame i (born at or before it, not yet ended) that hold cells there."""
        fr = self.frame(i)
        k = self.kyr(i)
        return sorted(d for d in fr.cells if self.alive_at(d, k))

    def events_in(self, i: int) -> dict:
        """Buds, fusions and extinctions in the interval (kyr(i-1), kyr(i)] (i >= 1): {"buds": [(child, parent)], "fusions":
        [(absorbed, host)], "extinct": [deme], "births": [deme with no speech parent]}."""
        t0, t1 = self.kyr(i - 1), self.kyr(i)
        out = {"buds": [], "fusions": [], "extinct": [], "births": []}
        for d in self.demes:
            if t1 - 1e-9 <= d["born_kyr"] < t0 - 1e-9:
                p = self.parent_deme(d["id"])
                (out["buds"].append((d["id"], p)) if p is not None else out["births"].append(d["id"]))
            e = d.get("ended_kyr")
            if e is not None and t1 - 1e-9 <= e < t0 - 1e-9:
                if d.get("end") == "fused" and d.get("into") is not None:
                    out["fusions"].append((d["id"], int(d["into"])))
                else:
                    out["extinct"].append(d["id"])
        return out

    # ------------------------------------------------------------------ presence
    def _open_presence(self):
        pm = self.meta.get("presence")
        dm = (self.meta.get("demes") or {}).get("all")
        if not pm or not dm:
            raise ValueError(f"run {self.id} has no presence table or demes_all (made before PW-1259)")
        self._p_off = np.fromfile(self.dir / pm["files"]["offsets"], dtype=np.dtype(pm["dtypes"]["offsets"])).reshape(pm["frames"], pm["lines"] + 1)
        self._p_cells = np.memmap(self.dir / pm["files"]["cells"], dtype=np.dtype(pm["dtypes"]["cells"]), mode="r")
        self._p_share = np.memmap(self.dir / pm["files"]["share"], dtype=np.uint8, mode="r")
        self._p_deme = np.memmap(self.dir / dm["file"], dtype=np.dtype(dm.get("dtype", "<u2")), mode="r")
        self.nlines = pm["lines"]

    def entries(self, i: int, people: str | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Presence entries at local frame i: (cells, share %, deme, line index), optionally for one people only."""
        rf = self.run_frame[i]
        row = self._p_off[rf]
        if people is None:
            a, b = int(row[0]), int(row[-1])
            lines = np.repeat(np.arange(self.nlines), np.diff(row).astype(np.int64))
        else:
            k = self.line_index[people]
            a, b = int(row[k]), int(row[k + 1])
            lines = np.full(b - a, k)
        return (np.asarray(self._p_cells[a:b], np.int64), np.asarray(self._p_share[a:b], np.float64),
                np.asarray(self._p_deme[a:b], np.int64), lines)

    def frame(self, i: int) -> Frame:
        """Local frame i's deme cells, shares and contact pairs (computed once)."""
        fr = self._frames[i]
        if fr is not None:
            return fr
        cells, share, deme, _ = self.entries(i)
        keep = deme != NONE
        cells, share, deme = cells[keep], share[keep], deme[keep]
        fr = Frame(self.kyr(i), self.run_frame[i])
        o = np.argsort(deme, kind="stable")
        ds, starts = np.unique(deme[o], return_index=True)
        ends = np.append(starts[1:], len(o))
        for d, s, e in zip(ds.tolist(), starts.tolist(), ends.tolist()):
            fr.cells[d] = cells[o[s:e]]
            fr.shares[d] = share[o[s:e]]
        # co-presence: every pair of demes on the same cell
        oc = np.lexsort((deme, cells))
        c2, d2, s2 = cells[oc], deme[oc], share[oc]
        pairs: dict = {}
        for k in range(1, 12):
            if k >= len(c2):
                break
            same = (c2[k:] == c2[:-k]) & (d2[k:] != d2[:-k])
            if not same.any():
                break
            ia = np.flatnonzero(same)
            a, b = d2[ia], d2[ia + k]
            sa, sb = s2[ia], s2[ia + k]
            lo, hi = np.minimum(a, b), np.maximum(a, b)
            slo = np.where(a < b, sa, sb)
            shi = np.where(a < b, sb, sa)
            key = lo * 100000 + hi
            uk, inv = np.unique(key, return_inverse=True)
            cnt = np.bincount(inv)
            ssl = np.bincount(inv, weights=slo)
            ssh = np.bincount(inv, weights=shi)
            for kk, c, x, y in zip(uk.tolist(), cnt.tolist(), ssl.tolist(), ssh.tolist()):
                p = pairs.setdefault((kk // 100000, kk % 100000), [0, 0, 0.0, 0.0])
                p[0] += c
                p[2] += x
                p[3] += y
        # borders between leading demes
        lead = np.asarray(self._lead["demes"][fr.run_index]).astype(np.int64)
        e = self.g.edges
        la, lb = lead[e[:, 0]], lead[e[:, 1]]
        ok = (la != NONE) & (lb != NONE) & (la != lb)
        lo, hi = np.minimum(la[ok], lb[ok]), np.maximum(la[ok], lb[ok])
        uk, cnt = np.unique(lo * 100000 + hi, return_counts=True)
        for kk, c in zip(uk.tolist(), cnt.tolist()):
            pairs.setdefault((kk // 100000, kk % 100000), [0, 0, 0.0, 0.0])[1] += c
        fr.pairs = pairs
        self._frames[i] = fr
        return fr

    def deme_cells(self, deme: int, i: int) -> tuple[np.ndarray, np.ndarray]:
        """(cells, shares in %) of a deme at local frame i (empty when it holds none there)."""
        fr = self.frame(i)
        if deme not in fr.cells:
            return np.zeros(0, np.int64), np.zeros(0)
        return fr.cells[deme], fr.shares[deme]

    def deme_population(self, deme: int, i: int) -> float:
        """Heads: cells x presence share x cell area x the people's density (present mean; good enough for prestige and swamping)."""
        _, sh = self.deme_cells(deme, i)
        return float(sh.sum() / 100.0 * self.cell_km2 * self.density(self.people_of(deme)))

    def contact(self, a: int, b: int, i: int) -> float:
        """Contact strength 0..1 between two demes at local frame i: (shared cells + half the border edges) / the smaller deme's
        cells."""
        if a == b:
            return 1.0
        fr = self.frame(i)
        p = fr.pairs.get((min(a, b), max(a, b)))
        if not p:
            return 0.0
        na, nb = len(fr.cells.get(a, ())), len(fr.cells.get(b, ()))
        m = max(min(na, nb), 1)
        return float(min(1.0, (p[0] + 0.5 * p[1]) / m))

    def contacts_of(self, deme: int, i: int, floor: float = 0.0) -> dict[int, float]:
        """Every deme in contact with `deme` at local frame i, with its strength above `floor`."""
        fr = self.frame(i)
        idx = self._pair_index(i)
        out = {}
        for o in idx.get(deme, ()):
            c = self.contact(deme, o, i)
            if c > floor:
                out[o] = c
        return out

    def _pair_index(self, i: int) -> dict:
        key = ("_pidx", i)
        if not hasattr(self, "_pidx"):
            self._pidx = {}
        if i not in self._pidx:
            idx: dict = {}
            for a, b in self.frame(i).pairs:
                idx.setdefault(a, []).append(b)
                idx.setdefault(b, []).append(a)
            self._pidx[i] = idx
        return self._pidx[i]

    def l2_share(self, deme: int, i: int) -> float:
        """Adult second-language share proxy (PW-985): clip(L2_SHARED x the other peoples' presence on the deme's cells (each
        co-held cell weighted by the other people's presence share there) / the deme's cells + the share of the deme's heads
        living in mixed cities it holds, 0, L2_MAX)."""
        cells, _ = self.deme_cells(deme, i)
        if not len(cells):
            return 0.0
        people = self.people_of(deme)
        fr = self.frame(i)
        sh = 0.0
        for o in self._pair_index(i).get(deme, ()):
            if self.people_of(o) != people:
                p = fr.pairs[(min(deme, o), max(deme, o))]
                sh += (p[3] if deme < o else p[2]) / 100.0  # (the other deme's summed presence % on the shared cells)
        city = sum(c["pop"] for c in self._mixed_cities_cached(i) if c["holder_deme"] == deme)
        bonus = min(1.0, city / max(self.deme_population(deme, i), 1.0)) if city else 0.0
        return float(min(max(L2_SHARED * sh / len(cells) + bonus, 0.0), L2_MAX))

    def _mixed_cities_cached(self, i: int) -> list[dict]:
        if not hasattr(self, "_mc"):
            self._mc = {}
        if i not in self._mc:
            self._mc[i] = self.mixed_cities(i)
        return self._mc[i]

    def isolation(self, deme: int, i: int) -> float:
        """1 when a deme touches no other deme at all, falling with its total contact."""
        c = sum(self.contacts_of(deme, i).values())
        return float(1.0 / (1.0 + c))

    # ------------------------------------------------------------------ prestige
    def knows(self, people: str, tech: str, kyr: float) -> bool:
        k = ((self.meta.get("techtree") or {}).get("known") or {}).get(people) or {}
        v = k.get(tech)
        return bool(v) and float(v[0]) >= kyr - 1e-9

    def prestige(self, deme: int, i: int) -> float:
        """Population, raised by the cities, writing and law the people knows at that time and by the towns and cities on its cells."""
        pop = self.deme_population(deme, i)
        people = self.people_of(deme)
        k = self.kyr(i)
        tech = sum(self.knows(people, t, k) for t in PRESTIGE_TECHS)
        towns, cities = self.places_of(deme, i)
        return pop * (1 + 0.5 * tech) * (1 + 0.05 * towns + 0.5 * cities)

    # ------------------------------------------------------------------ settlements
    @property
    def settlements(self) -> dict:
        if self._settlements is None:
            p = self.dir / "settlements.json"
            if p.exists():
                doc = json.loads(p.read_text())
                keep = ("id", "kind", "cell", "tier_peak", "tier_now", "holders", "who", "series", "founded_kyr", "abandoned_kyr", "holder")
                self._settlements = {"sites": [{k: s.get(k) for k in keep} for s in doc["sites"]], "tiers": doc.get("tiers", {})}
            else:
                self._settlements = {"sites": [], "tiers": {}}
        return self._settlements

    @cached_property
    def _site_tiers(self) -> list[dict]:
        """Per local frame, {cell: (tier, holder people, site)} of towns and cities (pop at the frame from the site's series)."""
        out = [dict() for _ in self.frames_kyr]
        for s in self.settlements["sites"]:
            ser = s.get("series") or []
            if not ser:
                continue
            ags = np.array([a for a, _ in ser], float)
            pops = np.array([p for _, p in ser], float)
            if pops.max() < TOWN_POP:
                continue
            for i, k in enumerate(self.frames_kyr):
                if k > ags.max() + 1e-9 or k < ags.min() - 0.2:
                    continue
                j = int(np.argmin(np.abs(ags - k)))
                p = pops[j]
                if p >= TOWN_POP:
                    tier = "city" if p >= CITY_POP else "town"
                    out[i][int(s["cell"])] = (tier, self.holder_at(s, k), s, float(p))
        return out

    def holder_at(self, site: dict, kyr: float) -> str | None:
        h = None
        for frm, who in site.get("holders") or []:
            if frm >= kyr - 1e-9:
                h = who
        return _people_of_line(self.lines, h) if h else None

    def places_of(self, deme: int, i: int) -> tuple[int, int]:
        """(towns, cities) on a deme's cells held by its people at local frame i."""
        cells, _ = self.deme_cells(deme, i)
        tiers = self._site_tiers[i]
        if not tiers or not len(cells):
            return 0, 0
        people = self.people_of(deme)
        t = c = 0
        for cell in set(cells.tolist()) & tiers.keys():
            tier, holder, _s, _p = tiers[cell]
            if holder == people:
                if tier == "city":
                    c += 1
                else:
                    t += 1
        return t, c

    def deme_at_cell(self, people: str, cell: int, i: int) -> int | None:
        """The deme of a people on a cell at local frame i, or None."""
        p = _people_of_line(self.lines, people)
        if p is None or p not in self.line_index:
            return None
        cells, _, dem, _ = self.entries(i, p)
        j = np.searchsorted(cells, cell)
        if j < len(cells) and cells[j] == cell and dem[j] != NONE:
            return int(dem[j])
        return None

    def mixed_city_demes(self, i: int) -> set[int]:
        if not hasattr(self, "_mcd"):
            self._mcd = {}
        if i not in self._mcd:
            out = set()
            for cell, (tier, holder, s, _p) in self._site_tiers[i].items():
                if tier == "city" and len(s.get("who") or {}) >= 2 and holder:
                    d = self.deme_at_cell(holder, cell, i)
                    if d is not None:
                        out.add(d)
            self._mcd[i] = out
        return self._mcd[i]

    def mixed_cities(self, i: int, min_pct: float = 10.0) -> list[dict]:
        """Cities at local frame i whose heads (`who`) hold two or more peoples at min_pct or more: {site, cell, pop, holder,
        holder_deme, who {people: share 0..1 over the kept peoples}} (koine pressure)."""
        out = []
        for cell, (tier, holder, s, pop) in sorted(self._site_tiers[i].items()):
            if tier != "city" or not holder:
                continue
            who = {}
            for p, pct in (s.get("who") or {}).items():
                pp = _people_of_line(self.lines, p)
                if pp and pct >= min_pct:
                    who[pp] = who.get(pp, 0.0) + float(pct)
            if len(who) < 2:
                continue
            hd = self.deme_at_cell(holder, cell, i)
            if hd is None:
                continue
            tot = sum(who.values())
            out.append({"site": s["id"], "cell": cell, "pop": pop, "holder": holder, "holder_deme": hd,
                        "who": {p: v / tot for p, v in sorted(who.items())}})
        return out

    # ------------------------------------------------------------------ triggers
    @cached_property
    def triggers(self) -> list[Trigger]:
        """Every shift trigger in the window, derived once (architecture section 8)."""
        out: list[Trigger] = []
        out += self._incursion_triggers()
        out += self._takeover_triggers()
        out += self._city_triggers()
        out += self._swamp_triggers()
        out += self._trade_triggers()
        return out

    def shift_triggers(self, i: int) -> list[Trigger]:
        """The triggers active at local frame i."""
        k = self.kyr(i)
        return [t for t in self.triggers if t.start_kyr >= k - 1e-9 and t.end_kyr <= k + 1e-9]

    def _disk(self, lat: float, lon: float, r_km: float) -> np.ndarray:
        la, lo = math.radians(lat), math.radians(lon)
        v = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
        return np.flatnonzero(self.g.centers @ v >= math.cos(r_km / R_KM))

    def _demes_in(self, people: str, cells: np.ndarray, i: int) -> dict[int, int]:
        p = _people_of_line(self.lines, people)
        if p is None or p not in self.line_index:
            return {}
        c, _, d, _ = self.entries(i, p)
        m = np.isin(c, cells) & (d != NONE)
        u, n = np.unique(d[m], return_counts=True)
        return dict(zip(u.tolist(), n.tolist()))

    def _incursion_triggers(self) -> list[Trigger]:
        out = []
        for inc in (self.meta.get("contacts") or {}).get("incursions") or []:
            ago = float(inc["ago_kyr"])
            if ago > START_KYR:
                continue
            i = self.frame_of(ago)
            r = 60.0 * math.sqrt(max(inc.get("cells", 1), 1) / math.pi) + INCURSION_RADIUS_KM
            disk = self._disk(inc["lat"], inc["lon"], r)
            by = self._demes_in(inc["by"], disk, i)
            over = self._demes_in(inc["over"], disk, i)
            if not by or not over:
                continue
            b = max(by, key=by.get)
            o = max(over, key=over.get)
            if b == o or self.people_of(b) == self.people_of(o):
                continue
            pb, po = self.prestige(b, i), self.prestige(o, i)
            end = max(ago - float(inc.get("span_kyr") or 0.5) - INCURSION_TAIL_KYR, 0.0)
            src = (f"incursion: {inc['by']} {inc['kind'].replace('_', ' ')} {inc['over']} on {inc.get('cells')} cells "
                   f"{ago:.2f} kyr ago (run.json meta.contacts.incursions)")
            if pb > po:
                out.append(Trigger("elite", b, o, ago, end, float(min(1.0, 0.3 + inc.get("local_share", 0.3))), src))
            else:
                out.append(Trigger("swamp", o, b, ago, end, float(min(1.0, 0.3 + inc.get("gain", 0.3))), src + "; the newcomers are fewer"))
        return out

    def _takeover_triggers(self) -> list[Trigger]:
        agg: dict = {}
        for s in self.settlements["sites"]:
            hs = s.get("holders") or []
            if len(hs) < 2:
                continue
            for j in range(1, len(hs)):
                t, new = float(hs[j][0]), _people_of_line(self.lines, hs[j][1])
                old = _people_of_line(self.lines, hs[j - 1][1])
                if not new or not old or new == old or t > START_KYR:
                    continue
                i = self.frame_of(t)
                rd = self.deme_at_cell(new, int(s["cell"]), i)
                od = self.deme_at_cell(old, int(s["cell"]), i) or self.deme_at_cell(old, int(s["cell"]), max(i - 1, 0))
                if rd is None or od is None:
                    continue
                nxt = float(hs[j + 1][0]) if j + 1 < len(hs) else 0.0
                end = max(nxt, float(s.get("abandoned_kyr") or 0.0))
                a = agg.setdefault((rd, od, i), {"n": 0, "city": 0, "end": end, "start": t})
                a["n"] += 1
                a["city"] += s.get("tier_peak") in ("city", "town")
                a["end"] = min(a["end"], end)
                a["start"] = max(a["start"], t)
        out = []
        for (rd, od, i), a in agg.items():
            if a["n"] >= TAKEOVER_SITES or a["city"]:
                src = (f"settlements: {a['n']} site(s) of the {self.people_of(od)} taken by the {self.people_of(rd)} about "
                       f"{self.kyr(i):.1f} kyr ago{' (a town or city among them)' if a['city'] else ''} (settlements.json holders)")
                out.append(Trigger("takeover", rd, od, a["start"], a["end"], float(min(1.0, 0.2 + 0.1 * a["n"] + 0.3 * bool(a["city"]))), src))
        return out

    def _city_triggers(self) -> list[Trigger]:
        """Mixed cities: the minority peoples' demes on a mixed city's cell lean to the holder's speech, with a strength scaled by
        the city's minority heads against the minority deme's population (one city cannot shift a large deme)."""
        best: dict = {}
        for i in range(len(self.frames_kyr)):
            for cell, (tier, holder, s, _p) in self._site_tiers[i].items():
                who = s.get("who") or {}
                if tier != "city" or len(who) < 2 or not holder:
                    continue
                hd = self.deme_at_cell(holder, cell, i)
                if hd is None:
                    continue
                pop = float(s.get("series")[-1][1]) if s.get("series") else CITY_POP
                for p, pct in who.items():
                    pp = _people_of_line(self.lines, p)
                    if pp == holder:
                        continue
                    od = self.deme_at_cell(pp, cell, i) if pp else None
                    if od is None or od == hd:
                        continue
                    st = float(min(1.0, 20.0 * pop * pct / 100.0 / max(self.deme_population(od, i), 1.0)))
                    k = (hd, od)
                    if k not in best:
                        best[k] = [self.kyr(i), self.kyr(i), st, s["id"]]
                    else:
                        best[k][1] = self.kyr(i)
                        best[k][2] = max(best[k][2], st)
        return [Trigger("city", hd, od, a, b, st, f"mixed city (site {sid}): the {self.people_of(od)} there live under the "
                        f"{self.people_of(hd)} (settlements.json who)") for (hd, od), (a, b, st, sid) in best.items() if st > 0.01]

    def _swamp_triggers(self) -> list[Trigger]:
        """A deme living mostly inside another people's deme that holds far more of the habitat and has far more people."""
        runs: dict = {}
        for i in range(len(self.frames_kyr)):
            fr = self.frame(i)
            for (a, b), (sh, _, sa, sb) in fr.pairs.items():
                if sh == 0 or self.people_of(a) == self.people_of(b):
                    continue
                for x, y, sx, sy in ((a, b, sa, sb), (b, a, sb, sa)):
                    nx = len(fr.cells.get(x, ()))
                    if nx and sh / nx >= SWAMP_INSIDE and sy >= SWAMP_RATIO * sx and self.deme_population(y, i) >= SWAMP_RATIO * self.deme_population(x, i):
                        r = runs.setdefault((y, x), [])
                        r.append(i)
        out = []
        for (y, x), idx in runs.items():
            # contiguous stretches of frames
            start = idx[0]
            prev = idx[0]
            for j in idx[1:] + [None]:
                if j is None or j != prev + 1:
                    if prev - start >= 1:
                        out.append(Trigger("swamp", y, x, self.kyr(start), self.kyr(prev), 0.6,
                                           f"swamping: the {self.people_of(x)} live inside the far more numerous {self.people_of(y)} "
                                           f"from {self.kyr(start):.1f} to {self.kyr(prev):.1f} kyr ago (presence table)"))
                    if j is not None:
                        start = j
                prev = j if j is not None else prev
        return out

    def _trade_triggers(self) -> list[Trigger]:
        """Long contact between peoples with many shared cells: the larger deme's speech becomes the smaller's trade language, and a
        shift pressure starts after TRADE_SHIFT_KYR of it."""
        runs: dict = {}
        need = int(round(TRADE_SHIFT_KYR / STEP_KYR))
        for i in range(len(self.frames_kyr)):
            fr = self.frame(i)
            for (a, b), (sh, *_r) in fr.pairs.items():
                if self.people_of(a) == self.people_of(b):
                    continue
                na, nb = len(fr.cells.get(a, ())), len(fr.cells.get(b, ()))
                if not na or not nb or sh / min(na, nb) < TRADE_SHARED:
                    continue
                big, small = (a, b) if self.deme_population(a, i) >= self.deme_population(b, i) else (b, a)
                runs.setdefault((big, small), []).append(i)
        out = []
        for (big, small), idx in runs.items():
            start = idx[0]
            prev = idx[0]
            for j in idx[1:] + [None]:
                if j is None or j != prev + 1:
                    if prev - start >= need:
                        s0 = self.kyr(start + need)
                        out.append(Trigger("trade", big, small, s0, self.kyr(prev), 0.25,
                                           f"trade: the {self.people_of(small)} and {self.people_of(big)} shared land from "
                                           f"{self.kyr(start):.1f} to {self.kyr(prev):.1f} kyr ago (presence table)"))
                    if j is not None:
                        start = j
                prev = j if j is not None else prev
        return out

    # ------------------------------------------------------------------ crops and animals
    @cached_property
    def stocks(self) -> dict:
        """{concept: {"bit", "layer", "label", "tamed": [...]}} for every crop and animal stock of the run."""
        out = {}
        for kind, layer in (("crops", "crop_known"), ("animals", "animal_known")):
            for sid, st in ((self.meta.get(kind) or {}).get("stocks") or {}).items():
                out[f"{'crop' if kind == 'crops' else 'animal'}:{sid}"] = {"bit": int(st["bit"]), "layer": layer, "label": st.get("label", sid),
                                                                          "tamed": st.get("tamed") or []}
        return out

    def _known_bits(self, i: int, layer: str) -> np.ndarray:
        return np.asarray(self._lead[layer][self.run_frame[i]]).astype(np.uint64)

    @cached_property
    def _arrivals(self) -> list[list]:
        """Per local frame, the (deme, concept, donor, origin, how) arrivals (frame 0 holds what the start demes already know).
        how: "tamed" (the deme holding a `stocks[id].tamed[]` cell at its taming frame: the route's origin), "land" (from the
        co-present or bordering deme that knew it in the previous frame with the most shared and border cells; ties by
        population), "sea" (no such neighbour: from the nearest deme that knew it), or "none" (nobody knew it: first known)."""
        out: list[list] = [[] for _ in self.frames_kyr]
        cum: dict = {}
        layers = ("crop_known", "animal_known")
        by_layer = {l: [(c, s["bit"]) for c, s in self.stocks.items() if s["layer"] == l] for l in layers}
        origins = self._taming_origins()
        prev_alive: set = set()
        for i in range(len(self.frames_kyr)):
            bits_now = {l: self._known_bits(i, l) for l in layers}
            alive = self.demes_alive(i)
            alive_set = set(alive)
            prev_cum = {d: dict(v) for d, v in cum.items() if d in prev_alive}
            known: dict = {}
            for d in alive:
                cells, _ = self.deme_cells(d, i)
                known[d] = {l: int(np.bitwise_or.reduce(bits_now[l][cells])) if len(cells) else 0 for l in layers}
            tamed_now = {}  # concept -> origin demes at this frame
            for (concept, fi), ds in origins.items():
                if fi == i:
                    for d in ds:
                        if d in alive_set:
                            tamed_now.setdefault(concept, []).append(d)
                            known[d][self.stocks[concept]["layer"]] |= 1 << self.stocks[concept]["bit"]
            for d in alive:
                if d not in cum:
                    p = self.parent_deme(d)
                    cum[d] = dict(cum[p]) if (p is not None and p in cum) else {l: 0 for l in layers}
                    if i == 0:
                        cum[d] = dict(known[d])
                        continue
                for l in layers:
                    new = known[d][l] & ~cum[d][l]
                    if not new:
                        continue
                    for concept, bit in by_layer[l]:
                        if not new >> bit & 1:
                            continue
                        if d in tamed_now.get(concept, ()):
                            out[i].append((d, concept, None, True, "tamed"))
                            continue
                        donor, how = self._donor(d, l, bit, i, prev_cum, alive_set, tamed_now.get(concept, ()))
                        out[i].append((d, concept, donor, False, how))
                    cum[d][l] |= known[d][l]
            prev_alive = alive_set
        return out

    def _taming_origins(self) -> dict:
        """{(concept, local frame): [deme, ...]}: for each `tamed` entry of a stock (the first=True one first), the deme holding
        its lat/lon cell at its taming frame (the tamer's people there, else the cell's leading deme, else that people's
        nearest deme). Tamings before the window are known at the start, not origins."""
        out: dict = {}
        for concept, st in sorted(self.stocks.items()):
            for t in sorted(st["tamed"], key=lambda t: (not t.get("first"), -float(t["ago_kyr"]))):
                if t.get("lat") is None or float(t["ago_kyr"]) > self.frames_kyr[0] + 1e-9:
                    continue
                k = float(t["ago_kyr"])
                i = max(1, min(range(len(self.frames_kyr)), key=lambda j: (abs(self.frames_kyr[j] - k), j)))
                la, lo = math.radians(float(t["lat"])), math.radians(float(t["lon"]))
                v = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
                cell = int(np.argmax(self.g.centers @ v))
                people = _people_of_line(self.lines, t.get("line"))
                d = self.deme_at_cell(people, cell, i) if people else None
                if d is None:
                    lead = int(np.asarray(self._lead["demes"][self.run_frame[i]])[cell])
                    d = lead if lead != NONE and self.alive_at(lead, self.kyr(i)) else None
                if d is None and people:
                    cand = [x for x in self.demes_alive(i) if self.people_of(x) == people]
                    if cand:
                        d = max(cand, key=lambda x: (float(self._centroid(x, i) @ v), -x))
                if d is not None:
                    ds = out.setdefault((concept, i), [])
                    if d not in ds:
                        ds.append(d)
        return out

    def _centroid(self, d: int, i: int) -> np.ndarray:
        key = (d, i)
        if not hasattr(self, "_cent"):
            self._cent = {}
        c = self._cent.get(key)
        if c is None:
            cells, _ = self.deme_cells(d, i)
            if not len(cells):
                cells, _ = self.deme_cells(d, max(i - 1, 0))
            m = self.g.centers[cells].sum(0) if len(cells) else np.zeros(3)
            c = self._cent[key] = m / (np.linalg.norm(m) or 1.0)
        return c

    def _donor(self, d: int, layer: str, bit: int, i: int, prev_cum: dict, alive: set, tamed: tuple = ()) -> tuple:
        """(donor deme, how) for deme d's arrival at frame i: the co-present or bordering deme that knew it in the previous
        frame (or tamed it this frame) with the most shared + border cells (ties by population, then id), at frame i, else at
        frame i - 1; else ("sea") the nearest deme that knew it; else (None, "none")."""
        knew = {o for o, c in prev_cum.items() if c[layer] >> bit & 1 and o in alive and o != d} | {o for o in tamed if o != d}
        if not knew:
            return None, "none"
        for j in (i, i - 1):
            fr = self.frame(j)
            best, bk = None, None
            for o in self._pair_index(j).get(d, ()):
                if o not in knew:
                    continue
                p = fr.pairs[(min(d, o), max(d, o))]
                k = (p[0] + p[1], self.deme_population(o, j), -o)
                if bk is None or k > bk:
                    best, bk = o, k
            if best is not None:
                return best, "land"
        v = self._centroid(d, i)
        best = max(sorted(knew), key=lambda o: (float(self._centroid(o, i) @ v), -o))
        return best, "sea"

    def crop_arrivals(self, i: int) -> list[tuple[int, str, int | None, bool, str]]:
        """(deme, concept, donor deme or None, origin, how) for every crop or animal a deme first knows at local frame i (i >= 1);
        how: tamed | land | sea | none (see _arrivals)."""
        return list(self._arrivals[i]) if i > 0 else []

    def known_at_start(self) -> list[tuple[int, str]]:
        """(deme, concept) for the crops and animals the start demes know already (coined at their proto time)."""
        return [(d, c) for d, c, *_ in self._arrivals[0]]

    # ------------------------------------------------------------------ landscape
    @property
    def world(self) -> dict | None:
        if self._world_layers is None and self._load_world and self.meta.get("world"):
            p = S.find_world(self.meta["world"])
            doc = json.loads(Path(p).read_text())
            keep = ("downstream", "flow", "lake", "coast_type", "elevation")
            self._world_layers = {k: np.asarray(doc["layers"][k]) for k in keep if k in doc["layers"]}
            self.world_summary = doc.get("summary", {})
            del doc
        return self._world_layers

    @cached_property
    def _river_data(self) -> dict:
        L = self.world
        if not L or "downstream" not in L or "flow" not in L:
            return {"id": np.full(self.n, -1), "rivers": {}}
        down = L["downstream"].astype(np.int64)
        flow = L["flow"].astype(float)
        nxt = np.where(down >= 0, down, np.arange(self.n))
        out = nxt.copy()
        for _ in range(40):
            o2 = out[out]
            if np.array_equal(o2, out):
                break
            out = o2
        riv = flow >= RIVER_FLOW
        rid = np.where(riv, out, -1)
        u, c = np.unique(rid[riv], return_counts=True)
        keep = {int(m) for m, k in zip(u.tolist(), c.tolist()) if k >= RIVER_MIN_CELLS}
        rid = np.where(np.isin(rid, list(keep)), rid, -1)
        rivers = {}
        for m in keep:
            cells = np.flatnonzero(rid == m)
            rivers[m] = {"id": m, "cells": int(len(cells)), "flow": float(flow[cells].max()), "mouth_cell": int(cells[np.argmax(flow[cells])])}
        return {"id": rid, "rivers": rivers}

    def rivers(self) -> dict:
        """{river id (its outlet cell): {id, cells, flow (largest discharge on it), mouth_cell}} and the per-cell id via river_id."""
        return self._river_data["rivers"]

    def river_id(self) -> np.ndarray:
        return self._river_data["id"]

    @cached_property
    def _lake_data(self) -> dict:
        L = self.world
        if not L or "lake" not in L:
            return {"id": np.full(self.n, -1), "lakes": {}}
        lk = np.asarray(L["lake"]) > 0
        parent = {int(c): int(c) for c in np.flatnonzero(lk)}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        e = self.g.edges
        m = lk[e[:, 0]] & lk[e[:, 1]]
        for a, b in e[m].tolist():
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
        lid = np.full(self.n, -1)
        for c in parent:
            lid[c] = find(c)
        u, cnt = np.unique(lid[lk], return_counts=True)
        return {"id": lid, "lakes": {int(a): {"id": int(a), "cells": int(k)} for a, k in zip(u.tolist(), cnt.tolist())}}

    def lakes(self) -> dict:
        """{lake id (its lowest cell index): {id, cells}}; connected `lake` cells of the world."""
        return self._lake_data["lakes"]

    def lake_id(self) -> np.ndarray:
        return self._lake_data["id"]

    def deme_landscape(self, deme: int, i: int) -> dict:
        """What a deme lives by, for naming: its largest river (and size), lake, coast share, mountain, landmass part."""
        cells, _ = self.deme_cells(deme, i)
        out = {"river": None, "river_flow": 0.0, "river_cells_here": 0, "rivers": [], "lake": None, "lake_cells": 0,
               "coast_share": 0.0, "mountain_m": 0.0, "mountain_share": 0.0, "part": self.demes[deme].get("place")}
        if not len(cells) or self.world is None:
            return out
        rid = self.river_id()[cells]
        rs = [int(r) for r in np.unique(rid[rid >= 0]).tolist()]
        if rs:
            R = self.rivers()
            rs.sort(key=lambda r: -R[r]["flow"])
            out["river"] = rs[0]
            out["river_flow"] = R[rs[0]]["flow"]
            out["river_cells_here"] = int((rid == rs[0]).sum())
            out["rivers"] = rs[:5]
        lid = self.lake_id()[cells]
        ls = lid[lid >= 0]
        if len(ls):
            u, c = np.unique(ls, return_counts=True)
            out["lake"] = int(u[np.argmax(c)])
            out["lake_cells"] = int(c.max())
        L = self.world
        if "coast_type" in L:
            out["coast_share"] = float((np.asarray(L["coast_type"])[cells] > 0).mean())
        if "elevation" in L:
            el = np.asarray(L["elevation"], float)[cells]
            out["mountain_m"] = float(el.max())
            out["mountain_share"] = float((el > 2000).mean())
        return out

    def niche_weights(self, deme: int, i: int) -> dict:
        """Herd, fish, crop, hunt and forage emphasis (sum 1) from the people's way and traits, the crops and animals known on its
        cells and its coast share; drives lexical elaboration."""
        people = self.people_of(deme)
        l = self.lines[people]
        w = {"herd": 0.1, "fish": 0.1, "crop": 0.1, "hunt": 0.2, "forage": 0.3}
        way = l.get("way") or ""
        if way in ("farmer", "agro_pastoral", "horticulturalist"):
            w["crop"] += 0.8
        if way in ("pastoral_nomad", "transhumant", "agro_pastoral"):
            w["herd"] += 0.8
        if way in ("fisher_forager", "sea_nomad"):
            w["fish"] += 0.8
        tr = set(l.get("traits") or [])
        if tr & {"seafaring", "coastal", "sea_hunter", "swims"}:
            w["fish"] += 0.4
        if "agricultural" in tr:
            w["crop"] += 0.4
        if "nomadic" in tr:
            w["herd"] += 0.2
        if "hunter" in tr:
            w["hunt"] += 0.4
        cells, _ = self.deme_cells(deme, i)
        if len(cells):
            ck = int(np.bitwise_or.reduce(self._known_bits(i, "crop_known")[cells]))
            ak = int(np.bitwise_or.reduce(self._known_bits(i, "animal_known")[cells]))
            w["crop"] += 0.1 * bin(ck).count("1")
            w["herd"] += 0.15 * bin(ak).count("1")
            if self.world is not None and "coast_type" in self.world:
                w["fish"] += float((np.asarray(self.world["coast_type"])[cells] > 0).mean())
        s = sum(w.values())
        return {k: round(v / s, 4) for k, v in w.items()}

    # ------------------------------------------------------------------ start
    def start_components(self, link: float) -> list[list[int]]:
        """Connected components of same-people demes alive at the start frame, linked by contact above `link` (each gets one
        proto-language)."""
        alive = self.demes_alive(0)
        parent = {d: d for d in alive}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in self.frame(0).pairs:
            if a in parent and b in parent and self.people_of(a) == self.people_of(b) and self.contact(a, b, 0) > link:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
        comps: dict = {}
        for d in alive:
            comps.setdefault(find(d), []).append(d)
        return sorted(comps.values(), key=lambda c: c[0])
