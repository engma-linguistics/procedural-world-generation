"""Rivers and lakes at the owner line of a matched pair (PW-1302; notes in rivers-round1.md).

    PLANET_DATA=... uv run python docs/review/land-zoom/rivers.py A B [--q 50] [--tol 12] [--json out.json]

A built first, B matched to it (`planet zoom --match A`). The mosaic shows each place from its owner (zoom/match.py's
rule: the tiling's cell when both are sections, else the nearer centre). A river crossing the owner line is found in
the *upstream* owner's own network (its `receiver` layer): a pixel it owns whose receiver the other one owns, carrying
at least q m3/s. Its counterpart is the downstream owner's river on its own ground within `tol` km of the crossing,
flowing away from the line: its nearest pixel carrying at least half the crossing's discharge (the course offset is
the distance to it), else the largest discharge there. Two directions:
  A->B: A's river flows into B's ground; does B carry A's water on from the line?
  B->A: B's river flows into A's ground; does B deliver what A carries on (A was built first, so A's discharge there is
        A's own estimate of B's catchment)?
Per direction: crossings, how many the other side continues (ratio within x2), median |log2 ratio|, share within 25%,
median offset (km) to the counterpart's peak pixel, and the total discharge across the line both ways. Lakes: B's first
own pixels at the line, A sampled there (nearest): pixels where one has a lake and the other land.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from planet import store as S  # noqa: E402
from planet.zoom import kernels as ZK  # noqa: E402
from planet.zoom import regional as RG  # noqa: E402
from planet.zoom import tiling as ZT  # noqa: E402


class N:
    """A zoom's drainage: discharge, receivers (pixel index, -1 none), water, its pixels on the sphere."""

    def __init__(self, ref: str):
        d = S.find_zoom(ref)
        meta = json.loads((d / "zoom.json").read_text())
        raw = S.read_layers(d, meta["layers"], ("water", "discharge", "receiver"))
        self.id, self.meta = meta["id"], meta
        self.res, self.nx, self.ny = float(meta["res_km"]), int(meta["nx"]), int(meta["ny"])
        self.frame = RG.frame_of(meta["center"])
        self.water = np.asarray(raw["water"]).ravel()
        self.q = S.decode(np.asarray(raw["discharge"]), meta["layers"]["discharge"]).astype(np.float32).ravel()
        s = np.asarray(raw["receiver"]).ravel().astype(int)
        i = np.arange(self.nx * self.ny)
        sl = s + (s >= 4)
        dr, dc = sl // 3 - 1, sl % 3 - 1
        self.rec = np.where(s == RG.D8_NONE, -1, i + dr * self.nx + dc)
        xs = (np.arange(self.nx) + 0.5 - self.nx / 2) * self.res
        ys = (self.ny / 2 - np.arange(self.ny) - 0.5) * self.res
        X, Y = np.meshgrid(xs, ys)
        self.P = self.frame.to_sphere(X.ravel(), Y.ravel())

    def rc(self, P):
        x, y = self.frame.to_plane(P)
        return self.ny / 2 - y / self.res - 0.5, x / self.res + self.nx / 2 - 0.5


def owner(P, A: N, B: N) -> np.ndarray:
    """0 A owns the point, 1 B, -1 a third section (tiling cells) -- zoom/match.py's rule for a pair."""
    sa, sb = A.meta.get("section"), B.meta.get("section")
    if sa and sb:
        n = ZT.choose_n(B.meta["size_km"], 190.0)
        f, i, j = ZT.locate(P, n)
        cell = np.char.add(np.char.add(np.char.add(np.array(list(ZT.FACES))[f], "."), i.astype(str)),
                           np.char.add(".", j.astype(str)))
        return np.where(cell == sb, 1, np.where(cell == sa, 0, -1))
    return (P @ B.frame.c >= P @ A.frame.c).astype(int)


def crossings(Z: N, own: np.ndarray, up: int, q0: float):
    """Pixels of Z owned by `up` whose receiver the other owner owns, discharge >= q0: (pixel, receiver)."""
    p = np.flatnonzero((own == up) & (Z.rec >= 0) & (Z.q >= q0) & (Z.water != 1))
    r = Z.rec[p]
    k = own[r] == 1 - up
    return p[k], r[k]


def leaving(Z: N, own: np.ndarray, side: int, steps: int) -> np.ndarray:
    """Pixels on `side`'s ground whose water reaches the other's ground within `steps` (flowing towards the line)."""
    cur = np.arange(len(Z.rec))
    hit = np.zeros(len(cur), bool)
    for _ in range(steps):
        nxt = np.where(cur >= 0, Z.rec[np.maximum(cur, 0)], -1)
        cur = np.where(nxt >= 0, nxt, -1)
        hit |= (cur >= 0) & (own[np.maximum(cur, 0)] == 1 - side)
    return hit & (own == side)


def counterpart(O: N, own_O: np.ndarray, side: int, pts: np.ndarray, tol_km: float, qref: np.ndarray):
    """The other zoom's largest discharge on `side`'s ground within tol of each point, flowing away from the line
    (not a river of its own running into the line there), and the course offset: km to its nearest such pixel
    carrying at least half the crossing's discharge (nan: none)."""
    bad = leaving(O, own_O, side, int(np.ceil(2 * tol_km / O.res)))
    r, c = O.rc(pts)
    w = int(np.ceil(tol_km / O.res))
    qs, offs, ok = np.zeros(len(pts)), np.full(len(pts), np.nan), np.zeros(len(pts), bool)
    for k in range(len(pts)):
        r0, c0 = int(round(r[k])), int(round(c[k]))
        if not (w + 3 <= r0 < O.ny - w - 3 and w + 3 <= c0 < O.nx - w - 3):
            continue
        ok[k] = True
        rr, cc = np.mgrid[r0 - w:r0 + w + 1, c0 - w:c0 + w + 1]
        d = np.hypot(rr - r[k], cc - c[k]) * O.res
        idx = (rr * O.nx + cc).ravel()
        m = (d.ravel() <= tol_km) & (own_O[idx] == side) & (O.water[idx] != 1) & ~bad[idx]
        if not m.any():
            continue
        j = np.argmax(np.where(m, O.q[idx], -1))
        qs[k] = O.q[idx][j]
        h = m & (O.q[idx] >= 0.5 * qref[k])
        if h.any():  # (the same river: its nearest pixel carrying at least half; not a bigger one joined below)
            j = np.flatnonzero(h)[np.argmin(d.ravel()[h])]
            qs[k], offs[k] = O.q[idx][j], d.ravel()[j]
    return qs, offs, ok


def direction(U: N, own_U, O: N, own_O, up: int, q0: float, tol: float) -> dict:
    p, r = crossings(U, own_U, up, q0)
    pts = U.P[p] + U.P[r]
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    qo, off, ok = counterpart(O, own_O, 1 - up, pts, tol, U.q[p])
    # (several pixels of one river may cross side by side: keep the largest within tol of each other)
    keep = np.zeros(len(p), bool)
    order = np.argsort(-U.q[p])
    taken = []
    for k in order:
        if not ok[k]:
            continue
        if any(np.arccos(np.clip(pts[k] @ pts[t], -1, 1)) * 6371.0 < tol for t in taken):
            continue
        taken.append(k)
        keep[k] = True
    qu = U.q[p][keep]
    qo, off = qo[keep], off[keep]
    lr = np.abs(np.log2(np.maximum(qo, 1e-3) / np.maximum(qu, 1e-3)))
    big = qu >= 500.0
    return dict(n=int(keep.sum()), continued=int((lr <= 1).sum()), within25=float((lr <= np.log2(1.25)).mean()) if len(lr) else None,
                log2_median=float(np.median(lr)) if len(lr) else None,
                offset_km_median=float(np.nanmedian(off[lr <= 1])) if np.isfinite(off[lr <= 1]).any() else None,
                n_big=int(big.sum()), big_within25=float((lr[big] <= np.log2(1.25)).mean()) if big.any() else None,
                q_up_total=float(qu.sum()), q_down_total=float(qo.sum()),
                worst=[dict(q_up=round(float(a), 1), q_down=round(float(b), 1)) for a, b in
                       sorted(zip(qu, qo), key=lambda t: -abs(np.log2(max(t[1], 1e-3) / max(t[0], 1e-3))) * t[0])[:5]])


def lakes_at_line(A: N, B: N, own_B) -> dict:
    mine = own_B == 1
    d = np.asarray(ZK.inside_distance(mine, B.nx, B.ny, False)).ravel()
    k = mine & (d <= 1.0)
    r, c = A.rc(B.P[k])
    okA = (r >= 2) & (r <= A.ny - 3) & (c >= 2) & (c <= A.nx - 3)
    wa = A.water[np.clip(np.rint(r).astype(int), 0, A.ny - 1) * A.nx + np.clip(np.rint(c).astype(int), 0, A.nx - 1)][okA]
    wb = B.water[k][okA]
    return dict(n=int(okA.sum()), lake_A=int((wa == 2).sum()), lake_B=int((wb == 2).sum()),
                A_lake_B_land=int(((wa == 2) & (wb == 0)).sum()), A_land_B_lake=int(((wa == 0) & (wb == 2)).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--q", type=float, default=50.0)
    ap.add_argument("--tol", type=float, default=12.0)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    A, B = N(a.a), N(a.b)
    own_A, own_B = owner(A.P, A, B), owner(B.P, A, B)
    out = dict(a=A.id, b=B.id, q=a.q, tol_km=a.tol,
               A_to_B=direction(A, own_A, B, own_B, 0, a.q, a.tol),
               B_to_A=direction(B, own_B, A, own_A, 1, a.q, a.tol),
               lakes=lakes_at_line(A, B, own_B))
    print(json.dumps(out, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
