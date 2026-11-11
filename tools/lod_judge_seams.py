"""Seams on the tiles a dive built (lod-plan-v2.md step 6, PW-1673): siblings, levels and cell edges, against
PW-1697's rule (within 10% of the same line with no seam).

    PLANET_DATA=<root> uv run --with pillow python tools/lod_judge_seams.py WORLD_ID OUT.json [--carve=N]

Reads the tile service's index (<root>/.tiles/<world>.json) and every built tile of levels 1-4 in it.
- siblings: every pair of built tiles of one cell and level that share an edge, `lod_build.edge_steps` across it
  (land off the imposed courses, the inside band 16-48 px on the same lines): the ratio across / inside, median and
  p90. For up to N pairs a level (--carve, default 3) away from cell edges, the reference is the same line with no
  seam: one block carved over both tiles (`carve_block`, as `test_edge_steps_like_the_inside`); the score is the
  pair's ratio over the reference's (1.0: as if there were no edge). The satellite image's colour steps (RGB
  distance) across the edge against the inside band, as a ratio of means (1.0: no colour seam).
- levels: at each built tile of levels 2-4, |child - parent| with the parent level's tiles read bilinearly on the
  cell's plane (as the viewer shows the parent stretched beside a child), at the child's outermost pixels against
  its pixels 16-48 px inside (no seam there): ratio median, p90.
- cells: every pair of built tiles of one level in two cells that meet at a cell edge, `line_seam` at the edge's
  points against the floor (`resampled`: the owner's tiles resampled onto the other's lattice), pooled per level.
"""
import json
import sys
from pathlib import Path

import numpy as np

from planet import store as S
from planet import world as W
from planet.zoom import lod as L
from planet.zoom import lod_build as LB
from planet.zoom import match as ZM
from planet.zoom import regional as Z


def tiles(wid: str) -> dict[L.Key, Path]:
    ix = json.loads((S.root() / ".tiles" / f"{wid}.json").read_text())
    out = {}
    for ks, e in ix.items():
        d = S.tile_zooms_dir(wid) / e["id"]
        if (d / "zoom.json").exists():
            out[L.Key.parse(ks)] = d
    return out


_cache: dict = {}


def load(d: Path) -> tuple[dict, dict]:
    if d not in _cache:
        if len(_cache) > 40:
            _cache.pop(next(iter(_cache)))
        _cache[d] = Z.load(d, decode=True)
    return _cache[d]


def plane_bilinear(built: dict, cell: str, level: int, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """The level's elevation (its built tiles of the cell, stitched on the shared lattice) at plane km (x, y),
    bilinear; nan where a needed pixel isn't built."""
    r, n = L.res_km(level), L.tile_px(level)
    gi, gj = (x + L.HALF) / r - 0.5, (L.HALF - y) / r - 0.5  # (column, row on the level's lattice)
    i0, j0 = np.floor(gi).astype(int), np.floor(gj).astype(int)
    fi, fj = gi - i0, gj - j0
    out = np.zeros(len(x))
    for di, dj, w in ((0, 0, (1 - fi) * (1 - fj)), (1, 0, fi * (1 - fj)), (0, 1, (1 - fi) * fj), (1, 1, fi * fj)):
        I, J = i0 + di, j0 + dj
        v = np.full(len(x), np.nan)
        tx, ty = I // n, J // n
        for a, b in set(zip(tx.tolist(), ty.tolist())):
            if level == 1:
                k = L.Key(cell, 1, 0, 0)
            else:
                try:
                    k = L.Key(cell, level, a, b)
                except ValueError:
                    continue
            if k not in built:
                continue
            h = load(built[k])[1]["elevation"]
            m = (tx == a) & (ty == b)
            if level == 1:  # (the section: 1,000 px on the same lattice)
                v[m] = h[np.clip(J[m], 0, h.shape[0] - 1), np.clip(I[m], 0, h.shape[1] - 1)]
            else:
                v[m] = h[J[m] - b * n, I[m] - a * n]
        out += w * v
    return out


def level_seams(built: dict) -> list[dict]:
    out = []
    for k in sorted(built, key=str):
        if k.level < 2 or L.parent(k) not in built:
            continue
        m, lay = load(built[k])
        h, land = lay["elevation"].astype(float), lay["water"] != 1
        n = h.shape[0]
        x, y = L.lattice(k)
        hp = plane_bilinear(built, k.cell, k.level - 1, x, y).reshape(h.shape)
        d = np.abs(h - hp)
        ii, jj = np.meshgrid(np.arange(n), np.arange(n))
        e = np.minimum(np.minimum(ii, n - 1 - ii), np.minimum(jj, n - 1 - jj))
        ok = land & np.isfinite(d)
        edge, inside = d[ok & (e == 0)], d[ok & (e >= 16) & (e <= 48)]
        if len(edge) < 50 or len(inside) < 50:
            continue
        out.append({"tile": str(k), "n_edge": int(len(edge)), "edge_med": float(np.median(edge)),
                    "edge_p90": float(np.percentile(edge, 90)), "inside_med": float(np.median(inside)),
                    "inside_p90": float(np.percentile(inside, 90)),
                    "ratio_med": float(np.median(edge) / np.median(inside)),
                    "ratio_p90": float(np.percentile(edge, 90) / np.percentile(inside, 90))})
    return out


def sibling_seams(built: dict, world: dict | None, wid: str, carve: int) -> list[dict]:
    out, carved = [], {}
    for a in sorted(built, key=str):
        if a.level < 2:
            continue
        for axis, b in ((1, (a.tx + 1, a.ty)), (0, (a.tx, a.ty + 1))):
            try:
                kb = L.Key(a.cell, a.level, *b)
            except ValueError:
                continue
            if kb not in built:
                continue
            za, zb = load(built[a])[1], load(built[kb])[1]
            ha, hb = za["elevation"].astype(float), zb["elevation"].astype(float)
            pa, pb = za["river_phase"], zb["river_phase"]
            la, lb = za["water"] != 1, zb["water"] != 1
            if axis == 1:
                off = ~(np.isfinite(pa[:, -1]) | np.isfinite(pb[:, 0])) & la[:, -1] & lb[:, 0]
            else:
                off = ~(np.isfinite(pa[-1, :]) | np.isfinite(pb[0, :])) & la[-1, :] & lb[0, :]
            across, inside = LB.edge_steps(ha, hb, axis, band=(16, 48))
            across = across[off]
            if len(across) < 30:
                continue
            r = {"a": str(a), "b": str(kb), "axis": axis, "n": int(len(across)), "near_cell_edge": bool(LB.near_lines(a) or LB.near_lines(kb)),
                 "ratio_med": float(np.median(across) / np.median(inside)),
                 "ratio_p90": float(np.percentile(across, 90) / np.percentile(inside, 90)),
                 "across_med_m": float(np.median(across)), "across_p90_m": float(np.percentile(across, 90)),
                 "across_max_m": float(across.max())}
            ca, cb = colour(built[a]), colour(built[kb])
            if ca is not None and cb is not None and ca.shape[:2] == ha.shape and cb.shape[:2] == hb.shape:
                cx, ci = [], []
                for ch in range(3):
                    x_, i_ = LB.edge_steps(ca[..., ch], cb[..., ch], axis, band=(16, 48))
                    cx.append(x_), ci.append(i_)
                cx, ci = np.sqrt(sum(v ** 2 for v in cx)), np.sqrt(sum(v ** 2 for v in ci))  # (RGB distance per step)
                r |= {"colour_across_mean": float(cx.mean()), "colour_inside_mean": float(ci.mean()),
                      "colour_ratio_mean": float(cx.mean() / max(ci.mean(), 1e-6)),
                      "colour_across_p99": float(np.percentile(cx, 99)), "colour_inside_p99": float(np.percentile(ci, 99))}
            if world is not None and not r["near_cell_edge"] and carved.get(a.level, 0) < carve:
                n, mpx = L.tile_px(a.level), 40
                src = {**LB.load_sources(wid, a), **LB.load_sources(wid, kb)}
                if axis == 1:
                    blk = (a.tx * n - mpx, (kb.tx + 1) * n + mpx, a.ty * n, (a.ty + 1) * n)
                else:
                    blk = (a.tx * n, (a.tx + 1) * n, a.ty * n - mpx, (kb.ty + 1) * n + mpx)
                hw = LB.carve_block(world, a, src, blk).astype(float)
                if axis == 0:
                    hw = hw.T
                ref, ref_in = LB.edge_steps(hw[:, :mpx + n], hw[:, mpx + n:], 1, band=(16, 48))
                ref = ref[off]
                rm = np.median(ref) / np.median(ref_in)
                r9 = np.percentile(ref, 90) / np.percentile(ref_in, 90)
                r |= {"ref_ratio_med": float(rm), "ref_ratio_p90": float(r9),
                      "score_med": float(r["ratio_med"] / rm), "score_p90": float(r["ratio_p90"] / r9)}
                carved[a.level] = carved.get(a.level, 0) + 1
            out.append(r)
            print("sibling", r, flush=True)
    return out


def colour(d: Path):
    """The tile's satellite image as float RGB (rows north first), or None."""
    try:
        from PIL import Image
        return np.asarray(Image.open(d / "satellite.png").convert("RGB"), float)
    except (ImportError, OSError):
        return None


def source(d: Path) -> dict:
    m, lay = load(d)
    return ZM.source_of({"layers": lay, "frame": Z.frame_of(m["center"]), "res": m["res_km"], "nx": m["nx"], "ny": m["ny"]})


def cell_seams(built: dict, wid: str) -> list[dict]:
    out = []
    by = {}
    for k in built:
        by.setdefault(k.level, []).append(k)
    for lv, ks in sorted(by.items()):
        cells = sorted({k.cell for k in ks})
        for i, a in enumerate(cells):
            for b in cells[i + 1:]:
                if b not in LB.cell_lines(a):
                    continue
                P = LB._line(a, b)
                own = LB.line_owner(wid, a, b)
                d, f = [], []
                for ka in [k for k in ks if k.cell == a]:
                    for kb in [k for k in ks if k.cell == b]:
                        if b not in LB.near_lines(ka) or a not in LB.near_lines(kb):
                            continue
                        sa, sb = source(built[ka]), source(built[kb])
                        s = LB.line_seam(sa, sb, P)
                        if not s["n"]:
                            continue
                        so, sx = (sa, sb) if own == a else (sb, sa)
                        d.append(s["d"])
                        f.append(LB.line_seam(so, LB.resampled(so, sx), P)["d"])
                if not d:
                    continue
                d, f = np.concatenate(d), np.concatenate(f)
                r = {"level": lv, "cells": [a, b], "owner": own, "n": int(len(d)), "med": float(np.median(d)),
                     "p90": float(np.percentile(d, 90)), "max": float(d.max()), "floor_med": float(np.median(f)),
                     "floor_p90": float(np.percentile(f, 90)),
                     "score_med": float(np.median(d) / max(np.median(f), 1e-6)),
                     "score_p90": float(np.percentile(d, 90) / max(np.percentile(f, 90), 1e-6))}
                out.append(r)
                print("cell", r, flush=True)
    return out


def main():
    wid, outp = sys.argv[1], Path(sys.argv[2])
    opt = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--") and "=" in a)
    carve = int(opt.get("carve", "3"))
    with S.tile_store(wid):
        built = tiles(wid)
        print({lv: sum(k.level == lv for k in built) for lv in (1, 2, 3, 4)}, flush=True)
        world = W.load(Z.find_world(wid)) if carve else None
        rep = {"tiles": {lv: sum(k.level == lv for k in built) for lv in (1, 2, 3, 4)},
               "levels": level_seams(built), "cells": cell_seams(built, wid)}
        rep["siblings"] = sibling_seams(built, world, wid, carve)
    outp.write_text(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
