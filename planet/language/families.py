"""Families: the true lect tree, the scholars' tree by an automatic comparative method, languages, and the horizon (PW-986,
architecture section 9).

- `cognate_share(a, b, concepts, blind=True)`: the share of concepts whose forms are recognisably alike. Blind: a normalized
  edit distance over percept vectors (substitution cost from how many axes differ and by how much, insertion/deletion 1),
  below COGNATE_DIST. Truth: the two words share an etymology root (the first step of their etymologies).
- The true tree: lect parent links (bud and shift; shift edges marked). Divergence of two lects = the time their lines parted.
- The scholars' tree: UPGMA over blind distances (1 - share) among the living lects; a link is reconstructable when its share is
  above the chance floor measured by shuffling concepts between unrelated pairs.
- The horizon: the oldest true split the scholars' tree still recovers. Two measures: `horizon_kyr` (pairs: the oldest 1-kyr bin
  of true divergence where at least half the pairs of living lects are still above the chance floor) and `clade_horizon_kyr`
  (the oldest true clade, two or more living lects, that the scholars' UPGMA reproduces exactly, with its link above chance).
- `horizon(result_or_doc)`: the split measure (calibration.md, "The horizon by splits"): splits of the true tree recovered as
  clades of the scholars' UPGMA under a strict cognate test (close forms whose segment correspondences recur elsewhere in the
  vocabulary), 2-kyr windows; with sisters / cross-family shares loose, strict and true. `analyse` keeps the pair measure.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from numba import njit

LANG_SHARE = 0.7  # blind core-list share above which lects count as one language
COGNATE_DIST = 0.45  # normalized edit distance below which two forms look cognate
SHUFFLE_PAIRS = 400  # random lect pairs for the chance floor
CHANCE_SD = 2.0  # floor = mean + this many sd of the shuffled shares
BIN_KYR = 1.0
HALF = 0.5

SUB_SCALE = 3.0  # percepts.distance at which a substitution costs as much as an insertion


def _seg_distance(segs: list) -> np.ndarray:
    """Substitution costs between distinct segments: min(1, percepts.distance / SUB_SCALE) (a kind mismatch is 1)."""
    from . import percepts as PC
    n = len(segs)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            M[i, j] = M[j, i] = min(1.0, PC.distance(segs[i], segs[j]) / SUB_SCALE)
    return M


@njit(cache=True)
def _pair_dist(segs, M, starts, lens, pa, pb):
    """Normalized edit distance per pair of words (indices into starts/lens): substitution M[x, y], indel 1, divided by the
    longer length."""
    out = np.empty(len(pa))
    for p in range(len(pa)):
        a, b = pa[p], pb[p]
        la, lb = lens[a], lens[b]
        if la == 0 or lb == 0:
            out[p] = 1.0
            continue
        sa, sb = starts[a], starts[b]
        prev = np.empty(lb + 1)
        cur = np.empty(lb + 1)
        for j in range(lb + 1):
            prev[j] = j
        for i in range(1, la + 1):
            cur[0] = i
            x = segs[sa + i - 1]
            for j in range(1, lb + 1):
                c = prev[j - 1] + M[x, segs[sb + j - 1]]
                if prev[j] + 1.0 < c:
                    c = prev[j] + 1.0
                if cur[j - 1] + 1.0 < c:
                    c = cur[j - 1] + 1.0
                cur[j] = c
            for j in range(lb + 1):
                prev[j] = cur[j]
        out[p] = prev[lb] / max(la, lb)
    return out


class WordTable:
    """Every (lect, concept) form flattened for fast pairwise distances."""

    def __init__(self, lects: list, concepts: list[str], form_of, root_of=None):
        self.lects = lects
        self.concepts = list(concepts)
        self.lidx = {getattr(l, "id", i): i for i, l in enumerate(lects)}
        nl, nc = len(lects), len(self.concepts)
        flat, starts, lens = [], np.zeros(nl * nc, np.int64), np.zeros(nl * nc, np.int64)
        seg_id: dict = {}
        self.roots = np.full(nl * nc, -1, np.int64)
        root_ids: dict = {}
        at = 0
        for i, l in enumerate(lects):
            for j, c in enumerate(self.concepts):
                f = form_of(l, c)
                k = i * nc + j
                starts[k] = at
                if f:
                    flat.extend(seg_id.setdefault(x, len(seg_id)) for x in f)
                    lens[k] = len(f)
                    at += len(f)
                if root_of is not None:
                    r = root_of(l, c)
                    if r is not None:
                        self.roots[k] = root_ids.setdefault(r, len(root_ids))
        self.segs = np.asarray(flat or [0], np.int64)
        self.seglist = list(seg_id)
        self.M = _seg_distance(self.seglist) if seg_id else np.zeros((1, 1))
        self.starts, self.lens = starts, lens
        self.has = lens > 0

    def share_matrix(self, idx: list[int] | None = None, blind: bool = True) -> np.ndarray:
        """Pairwise cognate shares among lects (indices into self.lects): over concepts both have."""
        idx = list(range(len(self.lects))) if idx is None else idx
        n, nc = len(idx), len(self.concepts)
        ia, ib = np.triu_indices(n, 1)
        out = np.eye(n)
        if not len(ia):
            return out
        A = np.asarray(idx)[ia][:, None] * nc + np.arange(nc)[None, :]
        B = np.asarray(idx)[ib][:, None] * nc + np.arange(nc)[None, :]
        both = self.has[A] & self.has[B]
        if blind:
            d = _pair_dist(self.segs, self.M, self.starts, self.lens, A.ravel(), B.ravel()).reshape(A.shape)
            hit = (d < COGNATE_DIST) & both
        else:
            hit = (self.roots[A] == self.roots[B]) & (self.roots[A] >= 0) & both
        s = hit.sum(1) / np.maximum(both.sum(1), 1)
        out[ia, ib] = s
        out[ib, ia] = s
        return out

    def chance_share(self, rng: np.random.Generator, idx: list[int], pairs: int = SHUFFLE_PAIRS) -> tuple[float, float, float]:
        """Shares when each concept of one lect is compared with a different concept of another (random pairs of lects): (mean, sd,
        floor = mean + CHANCE_SD sd)."""
        nc = len(self.concepts)
        if len(idx) < 2 or nc < 2:
            return 0.0, 0.0, 0.0
        a = rng.choice(idx, pairs)
        b = rng.choice(idx, pairs)
        keep = a != b
        a, b = a[keep], b[keep]
        perm = np.array([rng.permutation(nc) for _ in range(len(a))])
        A = a[:, None] * nc + np.arange(nc)[None, :]
        B = b[:, None] * nc + perm
        both = self.has[A] & self.has[B]
        d = _pair_dist(self.segs, self.M, self.starts, self.lens, A.ravel(), B.ravel()).reshape(A.shape)
        s = ((d < COGNATE_DIST) & both).sum(1) / np.maximum(both.sum(1), 1)
        m, sd = float(s.mean()), float(s.std())
        return m, sd, m + CHANCE_SD * sd


def cognate_share(a, b, concepts: list[str], blind: bool = True, form_of=None, root_of=None) -> float:
    """Share of concepts whose forms are recognisably cognate (blind) or share an etymology root (truth)."""
    from .lect import word_form, word_root
    t = WordTable([a, b], concepts, form_of or word_form, root_of or word_root)
    return float(t.share_matrix(blind=blind)[0, 1])


# ---------------------------------------------------------------------------- intelligibility
GRAMMAR_PENALTY = {"order": 0.15, "adp": 0.05, "case": 0.05, "number": 0.05}
INTEL_DIST_WEIGHT = 0.5  # how much the mean distance of the cognate pairs (relative to COGNATE_DIST) lowers intelligibility
INTEL_ADJ, INTEL_ENDS = 0.5, 0.5  # a continuum: neighbours above, ends below


def grammar_penalty(ta: dict | None, tb: dict | None) -> float:
    """Different basic word order, adposition side, case or number marking (typology summary values) cost a listener."""
    if not ta or not tb:
        return 0.0
    return float(min(0.3, sum(w for k, w in GRAMMAR_PENALTY.items() if ta.get(k) != tb.get(k))))


def _intel(d: np.ndarray, both: np.ndarray, gp: np.ndarray) -> np.ndarray:
    cog = (d < COGNATE_DIST) & both
    nb = np.maximum(both.sum(1), 1)
    share = cog.sum(1) / nb
    md = np.where(cog, d, 0.0).sum(1) / np.maximum(cog.sum(1), 1)
    base = share * (1.0 - INTEL_DIST_WEIGHT * md / COGNATE_DIST)
    return np.clip(base * (1.0 - gp), 0.0, 1.0)


def pair_intelligibility(tab: "WordTable", ia, ib, typ_a: list, typ_b: list) -> np.ndarray:
    """Intelligibility for pairs of lects of a WordTable (indices ia, ib): blind cognate share on its concepts x (1 - half the
    mean normalized distance of the cognate pairs over COGNATE_DIST) x (1 - grammar penalty)."""
    ia, ib = np.asarray(ia, np.int64), np.asarray(ib, np.int64)
    nc = len(tab.concepts)
    A = ia[:, None] * nc + np.arange(nc)[None, :]
    B = ib[:, None] * nc + np.arange(nc)[None, :]
    both = tab.has[A] & tab.has[B]
    d = _pair_dist(tab.segs, tab.M, tab.starts, tab.lens, A.ravel(), B.ravel()).reshape(A.shape)
    gp = np.array([grammar_penalty(x, y) for x, y in zip(typ_a, typ_b)])
    return _intel(d, both, gp)


class _Snap:
    def __init__(self, core):
        from .percepts import from_ipa
        self.forms = [tuple(from_ipa(x)) if x else None for x in core]


def intelligibility(a_snapshot: dict, b_snapshot: dict) -> float:
    """Intelligibility in [0, 1] between two lect snapshots (history.snapshot: core-100 IPA in a shared order, typology
    summary): the same measure the pass stores."""
    sa, sb = _Snap(a_snapshot["core"]), _Snap(b_snapshot["core"])
    concepts = list(range(len(sa.forms)))
    tab = WordTable([sa, sb], concepts, lambda s, c: s.forms[c])
    return float(pair_intelligibility(tab, [0], [1], [a_snapshot.get("typ")], [b_snapshot.get("typ")])[0])


def continua(lects: list, now: dict, in_contact, family_of) -> list[dict]:
    """Dialect continua among living lects: per family, the graph of lects in contact with intelligibility above INTEL_ADJ;
    in each connected piece, the pair of lects that cannot understand each other (below INTEL_ENDS) joined by the longest
    shortest path; the chain, its adjacent values and the ends' value."""
    from collections import deque
    fams: dict = {}
    for l in lects:
        fams.setdefault(family_of(l), []).append(l.id)
    out = []
    for fam, ids in sorted(fams.items()):
        if len(ids) < 3:
            continue
        adj = {x: [] for x in ids}
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                a, b = ids[x], ids[y]
                if now.get((min(a, b), max(a, b)), 0.0) > INTEL_ADJ and in_contact(a, b):
                    adj[a].append(b)
                    adj[b].append(a)
        best = None
        for src in sorted(ids):
            prev = {src: None}
            q = deque([src])
            while q:
                u = q.popleft()
                for v in sorted(adj[u]):
                    if v not in prev:
                        prev[v] = u
                        q.append(v)
            for dst in prev:
                if dst <= src or now.get((src, dst), 0.0) >= INTEL_ENDS:
                    continue
                path = [dst]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                if best is None or len(path) > len(best):
                    best = path[::-1]
        if best and len(best) >= 3:
            av = [now.get((min(a, b), max(a, b)), 0.0) for a, b in zip(best, best[1:])]
            out.append({"family": fam, "chain": best, "adjacent": [round(x, 3) for x in av],
                        "ends": round(now.get((min(best[0], best[-1]), max(best[0], best[-1])), 0.0), 3)})
    return sorted(out, key=lambda c: -len(c["chain"]))


# ---------------------------------------------------------------------------- trees
def upgma(dist: np.ndarray, ids: list) -> dict:
    """UPGMA over a symmetric distance matrix; returns {"nodes": [{id, children, height, leaves}], "root": ...}. Infinite
    distances stay separate roots (a forest); the result has one root per connected group."""
    n = len(ids)
    nodes = [{"id": i, "leaf": ids[i], "height": 0.0, "size": 1, "children": []} for i in range(n)]
    if n == 0:
        return {"nodes": [], "roots": []}
    D = dist.astype(float).copy()
    np.fill_diagonal(D, np.inf)
    active = list(range(n))
    cid = list(range(n))  # cluster index in D -> node id
    size = [1] * n
    alive = np.ones(n, bool)
    while alive.sum() > 1:
        sub = np.where(alive[:, None] & alive[None, :], D, np.inf)
        k = int(np.argmin(sub))
        i, j = divmod(k, n)
        if not math.isfinite(sub[i, j]):
            break
        node = {"id": len(nodes), "leaf": None, "height": float(D[i, j]) / 2.0, "size": size[i] + size[j],
                "children": [cid[i], cid[j]]}
        nodes.append(node)
        new = (D[i] * size[i] + D[j] * size[j]) / (size[i] + size[j])
        D[i, :] = new
        D[:, i] = new
        D[i, i] = np.inf
        alive[j] = False
        D[j, :] = np.inf
        D[:, j] = np.inf
        size[i] += size[j]
        cid[i] = node["id"]
    roots = [cid[i] for i in range(n) if alive[i]]
    for nd in nodes:
        if nd["leaf"] is not None:
            nd["leaves"] = frozenset([nd["leaf"]])
        else:
            nd["leaves"] = frozenset().union(*(nodes[c]["leaves"] for c in nd["children"]))
    return {"nodes": nodes, "roots": roots}


def tree_json(t: dict, height_name: str = "height", scale: float = 1.0) -> list[dict]:
    """A tree as nested JSON: [{"lect"} | {"children": [...], height_name}] per root."""
    nodes = t["nodes"]

    def rec(i):
        nd = nodes[i]
        if nd["leaf"] is not None:
            return {"lect": nd["leaf"]}
        return {height_name: round(nd["height"] * scale, 3), "children": [rec(c) for c in nd["children"]]}
    return [rec(r) for r in t["roots"]]


def cut(t: dict, max_height: float) -> list[frozenset]:
    """Clusters of leaves joined below max_height."""
    nodes = t["nodes"]
    out = []

    def rec(i):
        nd = nodes[i]
        if nd["height"] <= max_height:
            out.append(nd["leaves"])
        else:
            for c in nd["children"]:
                rec(c)
    for r in t["roots"]:
        rec(r)
    return out


def _bins(t, s, st, fin, floor) -> list[dict]:
    bins = []
    for b0 in np.arange(0.0, 20.0 + BIN_KYR, BIN_KYR):
        m = fin & (t >= b0) & (t < b0 + BIN_KYR)
        if m.sum() >= 3:
            bins.append({"from_kyr": float(b0), "pairs": int(m.sum()), "above_chance": round(float((s[m] > floor).mean()), 3),
                         "mean_share": round(float(s[m].mean()), 3), "mean_true_share": round(float(st[m].mean()), 3)})
    return bins


PERM = 19  # concept shuffles per pair for its own chance level (Kessler-style permutation test)
MIN_EXCESS = 0.05  # a pair must also beat its own chance level by 5 of the 100 core words (judgement: a handful of cognate sets, not one lookalike)


def pair_chance(tab: "WordTable", ia, ib, rng, k: int = PERM) -> tuple[np.ndarray, np.ndarray]:
    """Each pair's own chance level: its blind share with one lect's concepts shuffled, k times (the same k permutations for
    every pair): (mean, sd) per pair. Related lects share sounds and shapes, so their chance resemblance is higher than that
    of random lect pairs; this measures it pair by pair."""
    ia, ib = np.asarray(ia, np.int64), np.asarray(ib, np.int64)
    nc = len(tab.concepts)
    A = ia[:, None] * nc + np.arange(nc)[None, :]
    sh = np.zeros((k, len(ia)))
    for r in range(k):
        perm = rng.permutation(nc)
        B = ib[:, None] * nc + perm[None, :]
        both = tab.has[A] & tab.has[B]
        d = _pair_dist(tab.segs, tab.M, tab.starts, tab.lens, A.ravel(), B.ravel()).reshape(A.shape)
        sh[r] = ((d < COGNATE_DIST) & both).sum(1) / np.maximum(both.sum(1), 1)
    return sh.mean(0), sh.std(0)


def reconstructable(share: np.ndarray, cm: np.ndarray, csd: np.ndarray) -> np.ndarray:
    """A pair's relationship is visible to the scholars when its share beats its own chance level by 2 sd and MIN_EXCESS."""
    return share >= cm + np.maximum(2.0 * csd, MIN_EXCESS)


def _bins_ok(t, s, st, ok) -> list[dict]:
    bins = []
    for b0 in np.arange(0.0, 20.0 + BIN_KYR, BIN_KYR):
        m = (t >= b0) & (t < b0 + BIN_KYR)
        if m.sum() >= 3:
            bins.append({"from_kyr": float(b0), "pairs": int(m.sum()), "above_chance": round(float(ok[m].mean()), 3),
                         "mean_share": round(float(s[m].mean()), 3), "mean_true_share": round(float(st[m].mean()), 3)})
    return bins


def horizon_pairs(tab: "WordTable", T: np.ndarray, S_blind: np.ndarray, S_true: np.ndarray, sel_pairs, rng) -> dict:
    """The horizon over the related pairs (finite true divergence) among sel_pairs (i, j arrays): bins by divergence, the share
    of pairs each bin still reconstructs (per-pair permutation test), the horizon."""
    i, j = sel_pairs
    t = T[i, j]
    fin = np.isfinite(t)
    i, j, t = i[fin], j[fin], t[fin]
    if not len(i):
        return {"horizon_kyr": None, "bins": [], "pairs": 0}
    cm, csd = pair_chance(tab, i, j, rng)
    s = S_blind[i, j]
    ok = reconstructable(s, cm, csd)
    bins = _bins_ok(t, s, S_true[i, j], ok)
    return {"horizon_kyr": _horizon(bins), "bins": bins, "pairs": int(len(i)), "chance_mean": round(float(cm.mean()), 4),
            "chance_sd": round(float(csd.mean()), 4)}


MIN_BIN = 5  # a bin with fewer pairs cannot end the horizon (too few to tell), though it can extend it


def _horizon(bins: list[dict]) -> float | None:
    """How deep the scholars see: from the youngest bin of true divergence on, the end of the last bin where at least half
    the pairs still beat their chance level, stopping at the first bin of MIN_BIN or more pairs where fewer than half do.
    (Contiguous from the present: one lucky old bin of a few pairs does not set the horizon; calibration.md, t7.)"""
    hz = None
    for b in bins:
        if b["above_chance"] >= HALF:
            hz = b["from_kyr"] + BIN_KYR
        elif b["pairs"] >= MIN_BIN:
            break
    return hz


# ---------------------------------------------------------------------------- true history
def lineage(lect, by_id: dict) -> list[tuple[str, float]]:
    """[(lect id, time this path left it)] from the lect up to its proto: the lect itself at 0 (or its death) then each parent
    at the birth of the child on the path."""
    out = [(lect.id, float(lect.died_kyr or 0.0))]
    cur = lect
    while cur.parent is not None and cur.parent in by_id:
        out.append((cur.parent, float(cur.born_kyr)))
        cur = by_id[cur.parent]
    return out


def divergence(a, b, by_id: dict) -> float:
    """When two lects' lines parted (kyr ago), inf when they share no ancestor."""
    la = dict(lineage(a, by_id)[::-1])  # (the oldest first so the dict keeps... any order is fine: ids are unique)
    for lid, tb in lineage(b, by_id):
        if lid in la:
            return max(la[lid], tb)
    return math.inf


def divergence_matrix(lects: list, by_id: dict) -> np.ndarray:
    n = len(lects)
    lin = [dict(lineage(l, by_id)) for l in lects]
    order = [lineage(l, by_id) for l in lects]
    T = np.full((n, n), np.inf)
    np.fill_diagonal(T, 0.0)
    for i in range(n):
        for j in range(i + 1, n):
            for lid, tb in order[j]:
                ta = lin[i].get(lid)
                if ta is not None:
                    T[i, j] = T[j, i] = max(ta, tb)
                    break
    return T


def root_of_lect(l, by_id: dict) -> str:
    cur = l
    while cur.parent is not None and cur.parent in by_id:
        cur = by_id[cur.parent]
    return cur.id


def analyse(lects: list, concepts: list[str], seed: int, form_of=None, root_of=None, people_sets: dict | None = None) -> dict:
    """The families block: true tree, scholars' tree, languages, the chance floor, the horizon, and the share matrices summary.
    Sets `language`, `family_true`, `family_scholars` on each living lect (dead lects keep family_true only)."""
    from .lect import word_form, word_root
    form_of = form_of or word_form
    root_of = root_of or word_root
    by_id = {l.id: l for l in lects}
    living = [l for l in lects if l.died_kyr is None and l.deme is not None]
    for l in lects:
        l.family_true = root_of_lect(l, by_id)
    out = {"living": len(living), "lang_share": LANG_SHARE, "cognate_dist": COGNATE_DIST}
    if len(living) < 2:
        out.update({"true": [], "scholars": [], "horizon_kyr": None, "clade_horizon_kyr": None, "languages": []})
        return out
    tab = WordTable(living, concepts, form_of, root_of)
    idx = list(range(len(living)))
    S_blind = tab.share_matrix(idx, blind=True)
    S_true = tab.share_matrix(idx, blind=False)
    T = divergence_matrix(living, by_id)
    rng = np.random.default_rng((seed, 986, 9))
    mean, sd, floor = tab.chance_share(rng, idx)
    out["chance"] = {"mean": round(mean, 4), "sd": round(sd, 4), "floor": round(floor, 4), "pairs": SHUFFLE_PAIRS}
    ids = [l.id for l in living]
    true_t = upgma(np.where(np.isfinite(T), 2 * T, np.inf), ids)  # (UPGMA heights are half the distance)
    sch_t = upgma(1.0 - S_blind, ids)
    out["true"] = tree_json(true_t, "split_kyr")
    out["scholars"] = tree_json(sch_t, "distance", 2.0)
    # languages: scholars' clusters with share above LANG_SHARE; families: above the chance floor
    langs = cut(sch_t, (1.0 - LANG_SHARE) / 2.0)
    fams = cut(sch_t, (1.0 - floor) / 2.0)
    lang_rows = []
    for k, cl in enumerate(sorted(langs, key=lambda c: (-len(c), min(c)))):
        members = [by_id[x] for x in cl]
        big = max(members, key=lambda l: (l.population, l.id))
        lid = f"lang{k}"
        for m in members:
            m.language = lid
        lang_rows.append({"id": lid, "name": f"speech of {big.deme_name or big.id}", "largest_lect": big.id,
                          "lects": sorted(cl), "peoples": sorted({m.people for m in members})})
    for k, cl in enumerate(sorted(fams, key=lambda c: (-len(c), min(c)))):
        for x in cl:
            by_id[x].family_scholars = f"fam{k}"
    out["languages"] = lang_rows
    out["scholars_families"] = len(fams)
    out["true_families"] = len({l.family_true for l in living})
    # horizon by pairs
    iu = np.triu_indices(len(living), 1)
    t, s = T[iu], S_blind[iu]
    fin = np.isfinite(t)
    hz = horizon_pairs(tab, T, S_blind, S_true, iu, np.random.default_rng((seed, 986, 10)))
    out["by_divergence"] = hz["bins"]
    out["horizon_kyr"] = hz["horizon_kyr"]
    out["horizon_method"] = {"perm": PERM, "min_excess": MIN_EXCESS, "chance_mean": hz.get("chance_mean"),
                             "chance_sd": hz.get("chance_sd"), "related_pairs": hz["pairs"]}
    out["horizon_by"] = {}
    for name, peoples in (people_sets or {}).items():
        sel = np.array([living[i].people in peoples and living[j].people in peoples for i, j in zip(*iu)], bool)
        if sel.any():
            h2 = horizon_pairs(tab, T, S_blind, S_true, (iu[0][sel], iu[1][sel]), np.random.default_rng((seed, 986, 11)))
            out["horizon_by"][name] = {**h2, "lects": int(sum(l.people in peoples for l in living))}
    # clade horizon
    sch_sets = {nd["leaves"]: nd["height"] for nd in sch_t["nodes"] if nd["leaf"] is None}
    rec_h = []
    for nd in true_t["nodes"]:
        if nd["leaf"] is not None:
            continue
        h = nd["height"] / 1.0
        sh = sch_sets.get(nd["leaves"])
        if sh is not None and (1.0 - 2.0 * sh) > floor:
            rec_h.append(h)
    out["clade_horizon_kyr"] = round(max(rec_h), 2) if rec_h else None
    out["clades_recovered"] = len(rec_h)
    out["clades_true"] = sum(1 for nd in true_t["nodes"] if nd["leaf"] is None)
    # shares by relation (for checks)
    sib = fin & (t <= 2.0)
    fam = np.array([living[i].family_true != living[j].family_true for i, j in zip(*iu)])
    out["shares"] = {"siblings_le2kyr": round(float(s[sib].mean()), 3) if sib.any() else None,
                     "siblings_pairs": int(sib.sum()),
                     "cross_family": round(float(s[fam].mean()), 3) if fam.any() else None,
                     "cross_family_pairs": int(fam.sum()),
                     "siblings_true": round(float(S_true[iu][sib].mean()), 3) if sib.any() else None}
    out["_matrices"] = {"ids": ids, "blind": S_blind, "true": S_true, "divergence": T}
    return out


# ---------------------------------------------------------------------------- the horizon, by splits and regular correspondences
# (review-output.md section 8: the pair measure rests on one or two old splits, and an edit-distance lookalike test is looser
# than the comparative method.) Two changes:
# - a stricter cognate test: two forms count as cognate only when they are close (normalized aligned distance under
#   COGNATE_DIST) *and* every segment correspondence of their alignment (x:y, x:-, -:y) recurs in at least REC_MIN other
#   candidate pairs of the same two lects' vocabulary (the comparative method's recurrence criterion, simplified; one pass:
#   the counts are over all candidates, REC_ITERATE recounts after dropping the failures);
# - scoring splits, not pairs: a true split (a node of the lect tree, its living descendants in two or more groups) is
#   recovered when the scholars' UPGMA over strict blind distances holds a clade matching the split's lects (Jaccard >=
#   SPLIT_JACCARD), and the share across the split's groups beats the pairs' own shuffled chance level by SPLIT_EXCESS. The
#   horizon is where the share of recovered splits, in 2-kyr windows stepped by 1 kyr from the present, first falls below half
#   (linear between window centres); windows with fewer than MIN_SPLITS splits are widened (SPLIT_WIDEN), else skipped.
REC_MIN = 2  # each correspondence of a cognate pair must recur in this many other candidate pairs
REC_ITERATE = False  # True: drop failing candidates and recount until stable (collapses small cognate sets; see calibration.md)
SPLIT_JACCARD = 0.8  # a scholars' clade matches a true split's lects at this overlap (one stray lect in five)
SPLIT_EXCESS = 0.03  # the share across a split must beat chance by three regular cognate sets in a hundred
SPLIT_WINDOW, SPLIT_STEP = 2.0, 1.0
MIN_SPLITS = 3
# A window with fewer than MIN_SPLITS splits widens by SPLIT_WIDEN_STEP at each end, up to SPLIT_WIDEN per side, before it
# is skipped (measures round, run F: human splits are thin at 9-12 kyr, and skipping those windows let the crossing be
# interpolated across a 4-kyr gap with no evidence in it); its from/to stay the nominal window, "widened_kyr" the span used.
SPLIT_WIDEN, SPLIT_WIDEN_STEP = 1.0, 0.5
BIG_SIDE = 3  # "where possible", only splits with two groups of at least this many living lects are scored


@njit(cache=True)
def _align_cols(segs, M, sa, la, sb, lb, ca, cb):
    """Edit-distance alignment of two words (substitution M, indel 1), traced back into columns ca/cb (segment ids, -1 a gap,
    in reverse order); returns (number of columns, normalized distance)."""
    D = np.empty((la + 1, lb + 1))
    for i in range(la + 1):
        D[i, 0] = i
    for j in range(lb + 1):
        D[0, j] = j
    for i in range(1, la + 1):
        x = segs[sa + i - 1]
        for j in range(1, lb + 1):
            c = D[i - 1, j - 1] + M[x, segs[sb + j - 1]]
            if D[i - 1, j] + 1.0 < c:
                c = D[i - 1, j] + 1.0
            if D[i, j - 1] + 1.0 < c:
                c = D[i, j - 1] + 1.0
            D[i, j] = c
    i, j, n = la, lb, 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and abs(D[i, j] - (D[i - 1, j - 1] + M[segs[sa + i - 1], segs[sb + j - 1]])) < 1e-9:
            ca[n] = segs[sa + i - 1]
            cb[n] = segs[sb + j - 1]
            i -= 1
            j -= 1
        elif i > 0 and abs(D[i, j] - (D[i - 1, j] + 1.0)) < 1e-9:
            ca[n] = segs[sa + i - 1]
            cb[n] = -1
            i -= 1
        else:
            ca[n] = -1
            cb[n] = segs[sb + j - 1]
            j -= 1
        n += 1
    return n, D[la, lb] / max(la, lb)


@njit(cache=True)
def _strict_pairs(segs, M, starts, lens, has, A, B, K, cdist, rec_min, scored, cls, iterate):
    """For each pair of lects (rows of A, B: word indices per concept): (loose share, strict share) over the `scored` concepts
    both have. Loose: aligned distance < cdist. Strict: loose and every correspondence of the word recurs in >= rec_min other
    candidates (close pairs, distance < cdist) among all the concepts, scored or not."""
    P, nc = A.shape
    loose = np.zeros(P)
    strict = np.zeros(P)
    maxl = 1
    for k in range(len(lens)):
        if lens[k] > maxl:
            maxl = lens[k]
    W = 2 * maxl + 1
    ca = np.empty(W, np.int64)
    cb = np.empty(W, np.int64)
    codes = np.empty((nc, W), np.int64)
    ncode = np.zeros(nc, np.int64)
    for p in range(P):
        nb = 0
        cand = np.zeros(nc, np.bool_)
        for c in range(nc):
            a, b = A[p, c], B[p, c]
            if not (has[a] and has[b]):
                continue
            if scored[c]:
                nb += 1
            n, d = _align_cols(segs, M, starts[a], lens[a], starts[b], lens[b], ca, cb)
            if d < cdist:
                cand[c] = True
                # distinct correspondences of this word, by correspondence class (tone apart); tone-letter columns skipped
                m = 0
                for q in range(n):
                    x = cls[ca[q]] if ca[q] >= 0 else -1
                    y = cls[cb[q]] if cb[q] >= 0 else -1
                    if x == -2 or y == -2 or (x == -1 and y == -1):
                        continue
                    ca[m] = (x + 1) * (K + 1) + (y + 1)
                    m += 1
                u = np.unique(ca[:m])
                ncode[c] = len(u)
                codes[c, :len(u)] = u
        if nb == 0:
            continue
        loose[p] = (cand & scored).sum() / nb
        alive = cand.copy()
        while True:
            # how many live candidates hold each code
            tot = 0
            for c in range(nc):
                if alive[c]:
                    tot += ncode[c]
            if tot == 0:
                break
            allc = np.empty(tot, np.int64)
            at = 0
            for c in range(nc):
                if alive[c]:
                    allc[at:at + ncode[c]] = codes[c, :ncode[c]]
                    at += ncode[c]
            allc.sort()
            changed = False
            for c in range(nc):
                if not alive[c]:
                    continue
                for q in range(ncode[c]):
                    x = codes[c, q]
                    cnt = np.searchsorted(allc, x, side="right") - np.searchsorted(allc, x, side="left")
                    if cnt - 1 < rec_min:
                        alive[c] = False
                        changed = True
                        break
            if not changed or not iterate:
                break
        strict[p] = (alive & scored).sum() / nb
    return loose, strict


CHUNK = 4000


def _corr_classes(tab: "WordTable") -> np.ndarray:
    """Segment id -> correspondence class: the segment without its tone (tone is its own tier for a comparativist, and tone
    letters are not segments: -2, skipped)."""
    c = getattr(tab, "_cls", None)
    if c is not None:
        return c
    from dataclasses import replace
    key: dict = {}
    out = np.zeros(max(1, len(tab.seglist)), np.int64)
    for i, sg in enumerate(tab.seglist):
        if getattr(sg, "kind", None) == "T":
            out[i] = -2
            continue
        try:
            k = replace(sg, tone=0)
        except TypeError:
            k = sg
        out[i] = key.setdefault(k, len(key))
    tab._cls = out
    return out


def strict_shares(tab: "WordTable", ia, ib, perm=None, scored=None) -> tuple[np.ndarray, np.ndarray]:
    """(loose, strict) blind shares for pairs of lects (indices into tab.lects) on the `scored` concepts (a bool mask over
    tab.concepts, default all; correspondences are counted over all of tab's concepts); perm shuffles the second lect's
    concepts (the chance level)."""
    ia, ib = np.asarray(ia, np.int64), np.asarray(ib, np.int64)
    nc = len(tab.concepts)
    cols = np.arange(nc) if perm is None else np.asarray(perm)
    sc = np.ones(nc, np.bool_) if scored is None else np.asarray(scored, np.bool_)
    K = int(tab.M.shape[0])
    lo, st = np.zeros(len(ia)), np.zeros(len(ia))
    for k in range(0, len(ia), CHUNK):  # (chunks keep the index arrays small)
        A = ia[k:k + CHUNK, None] * nc + np.arange(nc)[None, :]
        B = ib[k:k + CHUNK, None] * nc + cols[None, :]
        lo[k:k + CHUNK], st[k:k + CHUNK] = _strict_pairs(tab.segs, tab.M, tab.starts, tab.lens, tab.has, A, B, K, COGNATE_DIST,
                                                         REC_MIN, sc, _corr_classes(tab), REC_ITERATE)
    return lo, st


def strict_matrix(tab: "WordTable", scored=None) -> tuple[np.ndarray, np.ndarray]:
    """Loose and strict blind share matrices over all lects of a WordTable (scored: as strict_shares)."""
    n = len(tab.lects)
    ia, ib = np.triu_indices(n, 1)
    Lo, St = np.eye(n), np.eye(n)
    if len(ia):
        lo, st = strict_shares(tab, ia, ib, scored=scored)
        Lo[ia, ib] = Lo[ib, ia] = lo
        St[ia, ib] = St[ib, ia] = st
    return Lo, St


def true_splits(T: np.ndarray, ids: list) -> list[dict]:
    """The true tree's splits among living lects from their divergence matrix: UPGMA on an ultrametric is exact; nodes at the
    same height as their parent are folded into it (several lines parting in one frame are one split, not an arbitrary
    binary order). [{"kyr", "leaves" (indices), "groups" [index sets]}]."""
    t = upgma(np.where(np.isfinite(T), 2 * T, np.inf), list(range(len(ids))))
    nodes = t["nodes"]

    def groups(i, h):
        nd = nodes[i]
        if nd["leaf"] is None and abs(nd["height"] - h) < 1e-9:
            return [g for c in nd["children"] for g in groups(c, h)]
        return [nd["leaves"]]
    out = []
    for nd in nodes:
        if nd["leaf"] is not None:
            continue
        # skip nodes folded into a parent of the same height
        out.append({"kyr": nd["height"], "leaves": nd["leaves"], "groups": [g for c in nd["children"] for g in groups(c, nd["height"])],
                    "_id": nd["id"]})
    folded = set()
    for nd in nodes:
        if nd["leaf"] is None:
            for c in nd["children"]:
                if nodes[c]["leaf"] is None and abs(nodes[c]["height"] - nd["height"]) < 1e-9:
                    folded.add(c)
    return [s for s in out if s["_id"] not in folded]


def _clade_match(sch_clades: list[frozenset], leaves: frozenset) -> bool:
    for c in sch_clades:
        inter = len(c & leaves)
        if inter and inter / len(c | leaves) >= SPLIT_JACCARD:
            return True
    return False


def split_horizon(tab: "WordTable", T: np.ndarray, S_strict: np.ndarray, sel: list[int], rng, perm: int = PERM,
                  extra: dict | None = None, scored=None) -> dict:
    """The split measure among the lects `sel` (indices into tab.lects): the scholars' UPGMA over 1 - strict share among them
    (lects in a random order, so ties do not follow storage order), each true split scored, the recovery curve, the horizon.
    extra: {name: share matrix} also averaged across each split (e.g. the loose and true shares) for the record."""
    sel = list(sel)
    n = len(sel)
    if n < 3:
        return {"horizon_kyr": None, "censored": False, "single_window_kyr": None, "smoothed_kyr": None, "smoothed": [],
                "recovery_by_bin": [], "splits": 0}
    order = rng.permutation(n)
    sub = np.asarray(sel)[order]
    D = 1.0 - S_strict[np.ix_(sub, sub)]
    sch = upgma(D, list(range(n)))
    clades = [frozenset(int(order[x]) for x in nd["leaves"]) for nd in sch["nodes"] if nd["leaf"] is None]
    splits = true_splits(T[np.ix_(sel, sel)], sel)
    # chance level per related pair (one set of concept shuffles shared by all pairs)
    pa, pb, owner = [], [], []
    for k, s in enumerate(splits):
        gs = [sorted(g) for g in s["groups"]]
        for x in range(len(gs)):
            for y in range(x + 1, len(gs)):
                for i in gs[x]:
                    for j in gs[y]:
                        pa.append(sel[i])
                        pb.append(sel[j])
                        owner.append(k)
    pa, pb, owner = np.asarray(pa, np.int64), np.asarray(pb, np.int64), np.asarray(owner, np.int64)
    nc = len(tab.concepts)
    ch = np.zeros(len(pa))
    if len(pa):
        for _ in range(perm):
            ch += strict_shares(tab, pa, pb, rng.permutation(nc), scored)[1]
        ch /= perm
    obs = S_strict[pa, pb] if len(pa) else np.zeros(0)
    rows = []
    for k, s in enumerate(splits):
        m = owner == k
        exc = float(obs[m].mean() - ch[m].mean()) if m.any() else 0.0
        sizes = sorted((len(g) for g in s["groups"]), reverse=True)
        clade = _clade_match(clades, s["leaves"])
        rec = clade and exc >= SPLIT_EXCESS
        rows.append({"kyr": float(s["kyr"]), "lects": len(s["leaves"]), "sides": sizes, "big": len(sizes) > 1 and sizes[1] >= BIG_SIDE,
                     "clade": bool(clade), "excess": round(exc, 4),
                     "share": round(float(obs[m].mean()), 4) if m.any() else None, "chance": round(float(ch[m].mean()), 4) if m.any() else None,
                     "recovered": bool(rec), "ids": [getattr(tab.lects[sel[i]], "id", None) for i in sorted(s["leaves"])]})
        for name, X in (extra or {}).items():
            rows[-1][name] = round(float(X[pa[m], pb[m]].mean()), 4) if m.any() and X is not None else None
    curve = recovery_curve(rows)
    rd = horizon_read(curve)
    return {"horizon_kyr": rd["horizon_kyr"], "censored": rd["censored"], "single_window_kyr": rd["single_window_kyr"],
            "smoothed_kyr": rd["smoothed_kyr"], "smoothed": rd["smoothed"], "recovery_by_bin": curve, "splits": len(rows),
            "split_rows": rows}


def recovery_curve(rows: list[dict]) -> list[dict]:
    """Split rows ({kyr, big, recovered, share}) into 2-kyr windows stepped by 1 kyr from the present: {from_kyr, to_kyr,
    splits, big_splits, widened_kyr (only when widened), scored ("big" when MIN_SPLITS big splits, else "all"), recovered,
    recovered_all, mean_share}. A window under MIN_SPLITS splits widens about its centre (SPLIT_WIDEN)."""
    curve = []
    top = max((r["kyr"] for r in rows), default=0.0)
    b0 = 0.0
    while b0 <= top:
        lo, hi = b0, b0 + SPLIT_WINDOW
        inw = [r for r in rows if lo <= r["kyr"] < hi]
        while len(inw) < MIN_SPLITS and b0 - lo < SPLIT_WIDEN - 1e-9:  # a sparse window widens about its centre
            lo, hi = lo - SPLIT_WIDEN_STEP, hi + SPLIT_WIDEN_STEP
            inw = [r for r in rows if lo <= r["kyr"] < hi]
        big = [r for r in inw if r["big"]]
        use = big if len(big) >= MIN_SPLITS else inw
        if inw:
            curve.append({"from_kyr": b0, "to_kyr": b0 + SPLIT_WINDOW, "splits": len(inw), "big_splits": len(big),
                          **({"widened_kyr": [max(lo, 0.0), hi]} if lo < b0 else {}),
                          "scored": "big" if use is big else "all",
                          "recovered": round(float(np.mean([r["recovered"] for r in use])), 3),
                          "recovered_all": round(float(np.mean([r["recovered"] for r in inw])), 3),
                          "mean_share": round(float(np.mean([r["share"] for r in use if r["share"] is not None] or [0.0])), 4)})
        b0 += SPLIT_STEP
    return curve


RUN_WINDOWS = 2  # the horizon needs this many consecutive scored windows under half (one unlucky window of 2-14 splits is noise)
SMOOTH_WINDOWS = 3  # the smoothed read: split-count-weighted moving average over this many scored windows


def _scored(curve: list[dict]) -> list[dict]:
    return [w for w in curve if w["splits"] >= MIN_SPLITS]


def _weight(w: dict) -> int:
    return w["big_splits"] if w.get("scored") == "big" else w["splits"]


def _crossing(prev, w, r_w) -> float:
    """The age where recovery crosses one half, linear between the previous (passing) scored window's centre and this one's
    (this window's start when it is the first)."""
    if prev is None:
        return w["from_kyr"]
    pc, pr = prev
    c = (w["from_kyr"] + w["to_kyr"]) / 2.0
    return round(pc + (pr - HALF) / max(pr - r_w, 1e-9) * (c - pc), 2)


def _split_horizon(curve: list[dict], run: int = RUN_WINDOWS) -> float | None:
    """From the present: the start of the first run of `run` consecutive scored windows (MIN_SPLITS or more splits) where fewer
    than half are recovered; the horizon is the crossing of one half into the run's first window, linear between its centre
    and the previous scored window's (its start when it is the first). A run cut short by the end of the curve counts.
    Never failing: the end of the last scored window (a lower bound; see horizon_read)."""
    return horizon_read(curve, run)["horizon_kyr"]


def horizon_read(curve: list[dict], run: int = RUN_WINDOWS) -> dict:
    """The horizon of a recovery curve three ways: {"horizon_kyr" (two windows in a row under half), "censored" (True: never
    under half for `run` windows, horizon_kyr is the end of the last scored window, a lower bound), "single_window_kyr" (the
    first window under half, the former rule), "smoothed_kyr" (the first crossing of the split-count-weighted moving average
    over SMOOTH_WINDOWS scored windows), "smoothed" (that average per scored window: [[from_kyr, value]])}."""
    sc = _scored(curve)
    out = {"horizon_kyr": None, "censored": False, "single_window_kyr": None, "smoothed_kyr": None, "smoothed": []}
    if not sc:
        return out
    rec = [w["recovered"] for w in sc]
    cen = [(w["from_kyr"] + w["to_kyr"]) / 2.0 for w in sc]

    def first(vals, need):
        prev = None
        for k, w in enumerate(sc):
            if vals[k] < HALF and all(vals[j] < HALF for j in range(k, min(k + need, len(sc)))):
                return _crossing(prev, w, vals[k])
            if vals[k] >= HALF:
                prev = (cen[k], vals[k])
        return None
    h = first(rec, run)
    if h is None:
        out["horizon_kyr"], out["censored"] = sc[-1]["to_kyr"], True
    else:
        out["horizon_kyr"] = h
    out["single_window_kyr"] = first(rec, 1) if first(rec, 1) is not None else sc[-1]["to_kyr"]
    half = SMOOTH_WINDOWS // 2
    sm = []
    for k in range(len(sc)):
        js = range(max(0, k - half), min(len(sc), k + half + 1))
        wt = [_weight(sc[j]) for j in js]
        sm.append(sum(wt[i] * rec[j] for i, j in enumerate(js)) / max(sum(wt), 1))
    out["smoothed"] = [[w["from_kyr"], round(v, 3)] for w, v in zip(sc, sm)]
    hs = first(sm, 1)
    out["smoothed_kyr"] = hs if hs is not None else sc[-1]["to_kyr"]
    return out


def _doc_lects(doc: dict, concepts) -> tuple[list, dict]:
    """Lightweight lects from a stored languages.json: id/parent/born/died/deme/people, core forms and true roots (the last
    word-formation step of each etymology chain)."""
    from .lect import FORMATION_SKIP
    from .percepts import from_ipa
    nodes = doc.get("etym_nodes") or []
    memo: dict = {}

    def root(nid):
        if nid in memo:
            return memo[nid]
        cur, last = nid, nid
        while cur is not None and cur >= 0:
            nd = nodes[cur]
            if nd[3].split(":", 1)[0] not in FORMATION_SKIP:
                last = cur
                break
            last, cur = cur, nd[0]
        memo[nid] = last
        return last
    cs = set(concepts)

    class _L:
        pass
    by = {}
    for x in doc["lects"]:
        l = _L()
        l.id, l.parent, l.born_kyr, l.died_kyr, l.deme, l.people = x["id"], x["parent"], x["born_kyr"], x["died_kyr"], x["deme"], x["people"]
        l.gen_yr = float(x.get("gen_yr") or 25.0)
        l.forms, l.roots = {}, {}
        if l.died_kyr is None and l.deme is not None:
            for c, w in (x.get("lexicon") or {}).items():
                if c in cs and w.get("ipa"):
                    l.forms[c] = tuple(from_ipa(w["ipa"]))
                    if w.get("etym") is not None and nodes:
                        l.roots[c] = root(int(w["etym"]))
        by[l.id] = l
    return list(by.values()), by


POOL_SHARE = 0.5  # correspondences are counted over every concept that at least this share of the living lects have a word for


def _pool(lexicons: list, core: list) -> list:
    from collections import Counter
    n = Counter(c for lx in lexicons for c in lx)
    return [c for c, k in sorted(n.items()) if k >= POOL_SHARE * len(lexicons) and c not in set(core)]


def horizon(result_or_doc: dict, people: str | None = "human", seed: int = 12, groups: dict | None = None) -> dict:
    """The scholars' horizon by splits under the strict cognate test, from the pass result (lects as objects) or a stored
    languages.json (lects as dicts): {"horizon_kyr" (lects of `people`, None = all), "method", "recovery_by_bin",
    "sisters", "cross_family", "by": {"human"|..., "all": the split measure among all living lects}}. Shares are scored on
    the core 100; correspondences are counted over the whole stored vocabulary the lects have in common (the comparativist
    works from every word, the lexicostatistician from the list). Sisters and cross-family shares are reported loose (the
    old edit-distance test), strict and true. groups: {name: predicate over a lect (people, gen_yr)}: the split measure is
    also run among each group's living lects (by[name]), e.g. the long-lived peoples."""
    from . import lexicon as LX
    from .lect import word_form, word_root
    concepts = sorted(LX.CORE100)
    lects = result_or_doc["lects"]
    if lects and isinstance(lects[0], dict):
        liv = [x for x in lects if x["died_kyr"] is None and x["deme"] is not None]
        pool = _pool([x.get("lexicon") or {} for x in liv], concepts)
        allx, by = _doc_lects(result_or_doc, concepts + pool)
        form_of, root_of = (lambda l, c: l.forms.get(c)), (lambda l, c: l.roots.get(c))
    else:
        allx, by = lects, {l.id: l for l in lects}
        form_of, root_of = word_form, word_root
        liv = [l for l in allx if l.died_kyr is None and l.deme is not None]
        pool = _pool([getattr(l.lexicon, "words", l.lexicon) or {} for l in liv], concepts)
    living = [l for l in allx if l.died_kyr is None and l.deme is not None]
    return horizon_from(living, by, concepts, form_of, root_of, people, seed, pool=pool, groups=groups)


def horizon_from(living: list, by_id: dict, concepts, form_of, root_of=None, people: str | None = "human", seed: int = 12,
                 pool=None, groups: dict | None = None) -> dict:
    """horizon() on lect objects (id, parent, born_kyr, died_kyr, people) with form_of/root_of accessors; shares scored on
    `concepts`, correspondences counted over concepts + pool."""
    concepts = list(concepts)
    allc = concepts + [c for c in (pool or []) if c not in set(concepts)]
    scored = np.arange(len(allc)) < len(concepts)
    tab = WordTable(living, allc, form_of, root_of)
    T = divergence_matrix(living, by_id)
    Lo, St = strict_matrix(tab, scored)
    Tr = None
    if root_of is not None:
        core_tab = WordTable(living, concepts, form_of, root_of)
        Tr = core_tab.share_matrix(blind=False)
    fam = {l.id: root_of_lect(l, by_id) for l in living}
    iu = np.triu_indices(len(living), 1)
    t = T[iu]
    sib = np.isfinite(t) & (t <= 2.0)
    cross = np.array([fam[living[i].id] != fam[living[j].id] for i, j in zip(*iu)], bool)

    def shares(m):
        if not m.any():
            return {"pairs": 0}
        return {"pairs": int(m.sum()), "loose": round(float(Lo[iu][m].mean()), 4), "strict": round(float(St[iu][m].mean()), 4),
                "true": round(float(Tr[iu][m].mean()), 4) if Tr is not None else None}
    by = {}
    extra = {"loose": Lo, "true": Tr}
    by["all"] = split_horizon(tab, T, St, range(len(living)), np.random.default_rng((seed, 986, 12)), extra=extra, scored=scored)
    by["all"]["lects"] = len(living)
    if people is not None:
        sel = [k for k, l in enumerate(living) if l.people == people]
        by[people] = split_horizon(tab, T, St, sel, np.random.default_rng((seed, 986, 13)), extra=extra, scored=scored)
        by[people]["lects"] = len(sel)
    for name, pred in (groups or {}).items():
        if name in by:
            continue
        sel = [k for k, l in enumerate(living) if pred(l)]
        by[name] = split_horizon(tab, T, St, sel, np.random.default_rng((seed, 986, zlib.crc32(name.encode()))), extra=extra,
                                 scored=scored)
        by[name]["lects"] = len(sel)
    main = by[people] if people is not None else by["all"]
    return {"horizon_kyr": main["horizon_kyr"],
            "method": {"test": "strict: aligned distance < cognate_dist and every correspondence recurs in >= rec_min other close "
                               "pairs over the pooled vocabulary; splits recovered by UPGMA clade match and excess over chance",
                       "cognate_dist": COGNATE_DIST, "rec_min": REC_MIN, "jaccard": SPLIT_JACCARD, "split_excess": SPLIT_EXCESS,
                       "window_kyr": SPLIT_WINDOW, "step_kyr": SPLIT_STEP, "min_splits": MIN_SPLITS, "widen_kyr": SPLIT_WIDEN, "big_side": BIG_SIDE,
                       "perm": PERM, "people": people, "lects": len(living), "scored_concepts": len(concepts),
                       "pool_concepts": len(allc)},
            "recovery_by_bin": main["recovery_by_bin"],
            "sisters": shares(sib), "cross_family": shares(cross),
            "censored": main.get("censored"), "single_window_kyr": main.get("single_window_kyr"),
            "smoothed_kyr": main.get("smoothed_kyr"), "smoothed": main.get("smoothed"),
            "by": {k: {"horizon_kyr": v["horizon_kyr"], "censored": v.get("censored"), "single_window_kyr": v.get("single_window_kyr"),
                       "smoothed_kyr": v.get("smoothed_kyr"), "smoothed": v.get("smoothed"), "splits": v["splits"],
                       "lects": v.get("lects"),
                       "recovery_by_bin": v["recovery_by_bin"], "split_rows": v.get("split_rows", [])} for k, v in by.items()}}
