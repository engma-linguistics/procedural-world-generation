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
"""
from __future__ import annotations

import math

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
        self.M = _seg_distance(list(seg_id)) if seg_id else np.zeros((1, 1))
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
