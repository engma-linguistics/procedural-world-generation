"""Seam measurement between two regional zooms (PW-1300; re-run by PW-1301/1302 lanes).

    uv run python docs/review/land-zoom/seams.py ZOOM_A ZOOM_B [--name NAME] [--q 100] [--out docs/review/land-zoom]

Two zooms of the same world whose squares overlap by a small band (centres a little under one side apart) are
compared at the same points of the sphere. The seam line is the great circle halfway between the two centres
(the perpendicular bisector); `d` is the signed distance across it, + towards B. Zoom A's square ends at
d = +(overlap/2), zoom B's at d = -(overlap/2); we compare the two zooms' fields at three stations:
    d = -edge  (B's own edge, A well inside),  d = 0  (both inside),  d = +edge  (A's own edge, B well inside)
(edge = overlap/2 - 5 km). Reported per station along the line (valid where both zooms have data):
  - |dh| of elevation where both are land: median, p95, bias (A - B);
  - |d slope| (degrees, from each zoom's own 1-pixel gradient): median, p95;
  - coast breaks per 100 km: runs where one zoom says land and the other sea or lake (water layer);
  - river breaks per 100 km: river crossings of the line (discharge >= q m3/s) that the other zoom lacks within
    TOL_KM, both ways; for matched crossings the median offset in km and the median |log2 discharge ratio|;
  - landform / biome class mismatch share over points both call land.
Writes seam-<name>.json and seam-<name>.png (strips across the seam: A, B, A-B elevation, biomes, rivers).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from planet import climate as CL  # noqa: E402
from planet import store as S  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402
from planet.images import write_png  # noqa: E402
from planet.zoom import regional as RG  # noqa: E402

TOL_KM = 3.0
NEED = ("elevation", "water", "discharge", "biome", "landform")


class Z:
    """A loaded zoom: the needed layers, its frame, and sampling at sphere points."""

    def __init__(self, ref: str):
        d = S.find_zoom(ref)
        meta = json.loads((d / "zoom.json").read_text())
        raw = S.read_layers(d, meta["layers"], NEED)
        self.id = meta["id"]
        self.meta = meta
        self.res, self.nx, self.ny = meta["res_km"], meta["nx"], meta["ny"]
        self.c = meta["center"]
        self.frame = RG.frame_of(self.c)  # (a turned section keeps its orientation in center.up, PW-1338)
        self.h = S.decode(np.asarray(raw["elevation"]), meta["layers"]["elevation"]).astype(np.float32)
        self.water = np.asarray(raw["water"])
        self.q = S.decode(np.asarray(raw["discharge"]), meta["layers"]["discharge"]).astype(np.float32)
        self.biome = np.asarray(raw["biome"])
        self.landform = np.asarray(raw["landform"])
        gy, gx = np.gradient(self.h, self.res * 1000.0)
        self.slope = np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)
        del gy, gx

    def centre_vec(self):
        return xyz(np.radians(self.c["lat"]), np.radians(self.c["lon"]))

    def rc(self, pts: np.ndarray):
        x, y = self.frame.to_plane(pts)
        return self.ny / 2 - y / self.res - 0.5, x / self.res + self.nx / 2 - 0.5

    def sample(self, pts: np.ndarray, margin_px: float = 2.0) -> dict:
        """Fields at sphere points (n, 3); valid = inside the square (margin_px from its edge)."""
        r, c = self.rc(pts)
        ok = (r >= margin_px) & (r <= self.ny - 1 - margin_px) & (c >= margin_px) & (c <= self.nx - 1 - margin_px)
        ri = np.clip(np.rint(r).astype(int), 0, self.ny - 1)
        ci = np.clip(np.rint(c).astype(int), 0, self.nx - 1)
        r0 = np.clip(np.floor(r).astype(int), 0, self.ny - 2)
        c0 = np.clip(np.floor(c).astype(int), 0, self.nx - 2)
        fr, fc = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
        h = (self.h[r0, c0] * (1 - fr) * (1 - fc) + self.h[r0, c0 + 1] * (1 - fr) * fc
             + self.h[r0 + 1, c0] * fr * (1 - fc) + self.h[r0 + 1, c0 + 1] * fr * fc)
        return dict(ok=ok, h=h, slope=self.slope[ri, ci], water=self.water[ri, ci], q=self.q[ri, ci],
                    biome=self.biome[ri, ci], landform=self.landform[ri, ci])


def seam_points(a: np.ndarray, b: np.ndarray, half_km: float, step_km: float, dmax: float, dstep: float):
    """(n_along, n_across, 3) sphere points: along the bisector, across by d in [-dmax, dmax]."""
    m = (a + b) / np.linalg.norm(a + b)
    t = np.cross(a, b)
    t /= np.linalg.norm(t)
    s = np.arange(-half_km, half_km + 1e-6, step_km) / R_KM
    p = np.cos(s)[:, None] * m + np.sin(s)[:, None] * t  # (na, 3)
    u = (b - a)[None, :] - ((b - a)[None, :] * p).sum(1, keepdims=True) * p
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    d = np.arange(-dmax, dmax + 1e-6, dstep) / R_KM
    pts = np.cos(d)[None, :, None] * p[:, None, :] + np.sin(d)[None, :, None] * u[:, None, :]
    return pts, np.arange(-half_km, half_km + 1e-6, step_km), np.arange(-dmax, dmax + 1e-6, dstep)


def runs(mask: np.ndarray):
    """[(start, end_exclusive)] of True runs."""
    m = np.concatenate([[0], mask.astype(np.int8), [0]])
    dm = np.diff(m)
    return list(zip(np.nonzero(dm == 1)[0], np.nonzero(dm == -1)[0]))


def pct(x, p):
    return float(np.percentile(x, p)) if len(x) else None


def station(A: dict, B: dict, step_km: float, q: float) -> dict:
    ok = A["ok"] & B["ok"]
    km = float(ok.sum() * step_km)
    out = {"line_km": km}
    if km < 50:
        return out
    landA, landB = A["water"] == 0, B["water"] == 0
    both = ok & landA & landB
    dh = (A["h"] - B["h"])[both]
    ds = np.abs(A["slope"] - B["slope"])[both]
    out.update(n_land=int(both.sum()), dh_median_abs=pct(np.abs(dh), 50), dh_p95_abs=pct(np.abs(dh), 95),
               dh_bias=float(dh.mean()) if len(dh) else None, dslope_median_deg=pct(ds, 50), dslope_p95_deg=pct(ds, 95))
    # coast: land vs not-land
    mism = ok & (landA != landB)
    out["coast_mismatch_share"] = float(mism.sum() / ok.sum())
    out["coast_breaks_per_100km"] = float(len(runs(mism)) / km * 100)
    # rivers
    rA, rB = ok & (A["q"] >= q) & landA, ok & (B["q"] >= q) & landB
    tol = int(round(TOL_KM / step_km))
    k = np.ones(2 * tol + 1)
    nearA = np.convolve(rA.astype(float), k, "same") > 0
    nearB = np.convolve(rB.astype(float), k, "same") > 0
    cA, cB = runs(rA), runs(rB)
    unA = [r for r in cA if not nearB[r[0]:r[1]].any()]
    unB = [r for r in cB if not nearA[r[0]:r[1]].any()]
    offs, lrat = [], []
    cBc = np.array([(r[0] + r[1] - 1) / 2 for r in cB]) if cB else np.array([])
    for r in cA:
        if r in unA or not len(cBc):
            continue
        ca = (r[0] + r[1] - 1) / 2
        j = int(np.argmin(abs(cBc - ca)))
        offs.append(abs(cBc[j] - ca) * step_km)
        qa = A["q"][r[0]:r[1]].max()
        qb = B["q"][cB[j][0]:cB[j][1]].max()
        lrat.append(abs(np.log2(max(qa, 1e-3) / max(qb, 1e-3))))
    out.update(river_crossings_A=len(cA), river_crossings_B=len(cB), river_unmatched_A=len(unA),
               river_unmatched_B=len(unB), river_breaks_per_100km=float((len(unA) + len(unB)) / km * 100),
               river_matched=len(offs), river_offset_km_median=pct(offs, 50),
               river_offset_km_max=float(max(offs)) if offs else None, river_log2_q_ratio_median=pct(lrat, 50))
    out["landform_mismatch_share"] = float((A["landform"] != B["landform"])[both].mean()) if both.any() else None
    out["biome_mismatch_share"] = float((A["biome"] != B["biome"])[both].mean()) if both.any() else None
    return out


# ---- pictures --------------------------------------------------------------------------------------------------
def _hex(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


BIOME_RGB = np.array([_hex(b[3]) for b in CL.BIOMES], np.uint8)
HYPS = [(-4000, (20, 40, 100)), (-200, (60, 110, 170)), (0, (150, 200, 220)), (1, (60, 130, 60)), (300, (130, 170, 80)),
        (900, (190, 175, 110)), (1800, (150, 110, 80)), (3000, (200, 195, 190)), (5500, (255, 255, 255))]


def colour_elev(h):
    xs = np.array([p[0] for p in HYPS], float)
    out = np.stack([np.interp(h, xs, [p[1][i] for p in HYPS]) for i in range(3)], -1)
    return out.astype(np.uint8)


def shade(h, dstep_km, step_km):
    # light from the north-west across the strip (rows = d, cols = along), crude hillshade
    gy, gx = np.gradient(h, dstep_km * 1000.0, step_km * 1000.0)
    s = np.clip(0.75 + 0.9 * (gx - gy) / 1.4142 * 2.0, 0.35, 1.25)
    return s


def render(A: dict, B: dict, along_km, d_km, path: Path, step: int, q: float, title_ids):
    """Strips: rows = d (A's side at the top), columns = along the seam; panels stacked with white gaps."""
    na, nd = A["h"].shape
    T = lambda x: np.asarray(x).T  # noqa: E731  (-> (nd, na))
    hA, hB = T(A["h"]), T(B["h"])
    okA, okB = T(A["ok"]), T(B["ok"])
    dist = d_km[:, None]
    nodata = np.array([40, 40, 40], np.uint8)
    nodata2 = np.array([90, 20, 20], np.uint8)

    def elev_panel(h, ok, water):
        img = colour_elev(h)
        sh = shade(h, d_km[1] - d_km[0], along_km[1] - along_km[0])[..., None]
        img = np.clip(img * sh, 0, 255).astype(np.uint8)
        img[~ok] = nodata
        return img

    pA = elev_panel(hA, okA, T(A["water"]))
    pB = elev_panel(hB, okB, T(B["water"]))
    both = okA & okB
    diff = np.clip((hA - hB) / 400.0, -1, 1)
    pD = np.zeros(hA.shape + (3,), np.uint8)
    pD[...] = 255
    pD[..., 0] = np.where(diff > 0, 255, 255 * (1 + diff)).astype(np.uint8)
    pD[..., 2] = np.where(diff < 0, 255, 255 * (1 - diff)).astype(np.uint8)
    pD[..., 1] = (255 * (1 - np.abs(diff))).astype(np.uint8)
    pD[~both] = nodata
    bA, bB = BIOME_RGB[np.clip(T(A["biome"]), 0, 15)], BIOME_RGB[np.clip(T(B["biome"]), 0, 15)]
    bA = bA.copy(); bB = bB.copy()
    bA[~okA] = nodata; bB[~okB] = nodata
    # rivers: A red, B blue, both magenta/white, over a dimmed land/sea base
    base = np.where(T(A["water"] == 0)[..., None], np.array([170, 170, 150], np.uint8), np.array([40, 70, 110], np.uint8))
    rv = base.copy()
    rvA, rvB = (T(A["q"]) >= q) & okA & (T(A["water"]) == 0), (T(B["q"]) >= q) & okB & (T(B["water"]) == 0)
    rv[~(okA | okB)] = nodata
    rv[rvA] = (220, 30, 30)
    rv[rvB] = (30, 60, 230)
    rv[rvA & rvB] = (255, 255, 255)
    # widen the river lines a little so they show at this scale
    for name in ("A", "B"):
        pass
    panels = [pA, pB, pD, bA, bB, rv]
    gap = np.full((6, na, 3), 255, np.uint8)
    rows = []
    for p in panels:
        rows += [p, gap]
    img = np.concatenate(rows[:-1], 0)
    # tick marks: seam line d = 0 on each panel's left/right edges
    z0 = int(np.argmin(abs(d_km)))
    off = 0
    for p in panels:
        img[off + z0, :8] = 255
        img[off + z0, -8:] = 255
        off += p.shape[0] + 6
    img = img[:, ::step]
    write_png(path, np.ascontiguousarray(img))


OWNER_STATIONS = (("held -50", -50.0), ("held -10", -10.0), ("line", 0.0), ("ramp +20", 20.0), ("ramp +40", 40.0),
                  ("ramp +70", 70.0))
MOVED_BANDS = ((0, 80), (80, 160), (160, 300), (300, 600), (600, 1e9))


def owner_stations(ZA: Z, ZB: Z, alone: Z | None = None) -> dict:
    """A matched pair's numbers at the owner line (PW-1301): who owns each of B's pixels as zoom/match.py decides it
    (the tiling's cell when both are sections, else the nearer centre); sd = signed km from the owner line, + into
    B's own ground. Stations are B's pixels within half a pixel of sd = d (held ground at d < 0, the ramp 0..80);
    A is sampled at their centres. With `alone` (B built alone, the same frame): how far B moved, by band of sd."""
    from planet.zoom import kernels as ZK
    from planet.zoom import tiling as ZT
    nx, ny, res = ZB.nx, ZB.ny, ZB.res
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    P = ZB.frame.to_sphere(X.ravel(), Y.ravel())
    sa, sb = ZA.meta.get("section"), ZB.meta.get("section")
    if sa and sb:
        n = ZT.choose_n(ZB.meta["size_km"], 190.0)
        f, i, j = ZT.locate(P, n)
        cell = np.char.add(np.char.add(np.char.add(np.array(list(ZT.FACES))[f], "."), i.astype(str)),
                           np.char.add(".", j.astype(str)))
        mine, theirs = cell == sb, cell == sa
    else:
        a, b = ZA.centre_vec(), ZB.centre_vec()
        mine = (P @ b) >= (P @ a)
        theirs = ~mine
    # (pixel centres: the first pixel each side of the line is half a pixel from it; a third cell's pixels are left out)
    sd = (np.maximum(ZK.inside_distance(mine, nx, ny, False) - 0.5, 0)
          - np.maximum(ZK.inside_distance(theirs, nx, ny, False) - 0.5, 0)) * res
    sd = np.where(mine | theirs, sd, np.nan)
    SA = ZA.sample(P)
    SB = {k: v.ravel() for k, v in dict(h=ZB.h, slope=ZB.slope, water=ZB.water, q=ZB.q, biome=ZB.biome,
                                          landform=ZB.landform).items()}
    SB["ok"] = np.ones(len(P), bool)
    landA, landB = SA["water"] == 0, SB["water"] == 0
    out = {"owner": "tiling cells" if sa and sb else "nearer centre", "stations": {}}
    for name, d in OWNER_STATIONS:
        k = SA["ok"] & (np.abs(sd - d) <= 0.5 * res)
        both = k & landA & landB
        dh = np.abs(SA["h"] - SB["h"])[both]
        ds = np.abs(SA["slope"] - SB["slope"])[both]
        out["stations"][name] = dict(
            d_km=d, n=int(k.sum()), n_land=int(both.sum()), dh_median_abs=pct(dh, 50), dh_p95_abs=pct(dh, 95),
            dslope_median_deg=pct(ds, 50), dslope_p95_deg=pct(ds, 95),
            coast_mismatch_share=float((landA != landB)[k].mean()) if k.any() else None,
            # (which water each side has where they disagree, 'A/B': 0 land, 1 sea, 2 lake)
            coast_pairs={f"{wa}/{wb}": int(((SA["water"] == wa) & (SB["water"] == wb) & k).sum())
                         for wa in (0, 1, 2) for wb in (0, 1, 2) if wa != wb and (wa == 0 or wb == 0)},
            biome_mismatch_share=float((SA["biome"] != SB["biome"])[both].mean()) if both.any() else None,
            landform_mismatch_share=float((SA["landform"] != SB["landform"])[both].mean()) if both.any() else None)
    for lab, lo, hi in (("slope_p95_ramp_0_80", 0, 80), ("slope_p95_inside_120_400", 120, 400)):
        k = landB & (sd > lo) & (sd < hi)
        out[lab] = pct(SB["slope"][k], 95)
        if alone is not None:
            out[lab + "_alone"] = pct(alone.slope.ravel()[(alone.water.ravel() == 0) & (sd > lo) & (sd < hi)], 95)
    if alone is not None:
        assert (alone.nx, alone.ny) == (nx, ny), "the alone build must be the same square"
        both = landB & (alone.water.ravel() == 0)
        dh = np.abs(alone.h.ravel() - SB["h"])
        out["b_moved"] = {f"{lo}-{hi if hi < 1e8 else 'end'}": dict(
            n_land=int((both & (sd >= lo) & (sd < hi)).sum()),
            dh_median_abs=pct(dh[both & (sd >= lo) & (sd < hi)], 50), dh_p95_abs=pct(dh[both & (sd >= lo) & (sd < hi)], 95),
            coast_changed_share=float((landB != (alone.water.ravel() == 0))[(sd >= lo) & (sd < hi)].mean())
            if ((sd >= lo) & (sd < hi)).any() else None)
            for lo, hi in MOVED_BANDS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--name", default=None)
    ap.add_argument("--q", type=float, default=100.0, help="river threshold, m3/s")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--step", type=float, default=1.0, help="km between samples along the line")
    ap.add_argument("--strip-km", type=float, default=None, help="picture half-width across the seam (default overlap/2 + 40)")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--owner", action="store_true",
                    help="B is matched to A (planet zoom --match): add stations at the owner line and across the ramp")
    ap.add_argument("--alone", default=None, metavar="ZOOM",
                    help="with --owner: B's square built alone, to measure how far matching moved B")
    args = ap.parse_args()
    ZA, ZB = Z(args.a), Z(args.b)
    a, b = ZA.centre_vec(), ZB.centre_vec()
    gap = float(np.arccos(np.clip(a @ b, -1, 1)) * R_KM)
    side = ZA.meta["size_km"]
    half = min(side, ZB.meta["size_km"]) / 2 + 100.0
    dstep = 1.0
    # the band both squares cover, found from the data (turned or unequal sections: not side - gap, PW-1338):
    # across the bisector, the d range where at least half as much of the line as at best has both zooms
    probe, _, dp = seam_points(a, b, half, 10.0, max(side - gap, 0.0) / 2 + 400.0, dstep)
    pf = probe.reshape(-1, 3)
    both = np.mean((ZA.sample(pf)["ok"] & ZB.sample(pf)["ok"]).reshape(probe.shape[:2]), axis=0)
    cov = np.flatnonzero(both >= 0.5 * both.max())
    lo_d, hi_d = float(dp[cov[0]]), float(dp[cov[-1]])
    overlap, mid = hi_d - lo_d, 0.5 * (lo_d + hi_d)
    edge = overlap / 2 - 5.0
    pts, along, dd = seam_points(a, b, half, args.step, args.strip_km or (max(abs(lo_d), abs(hi_d)) + 40.0), dstep)
    na, nd = pts.shape[:2]
    flat = pts.reshape(-1, 3)
    SA, SB = ZA.sample(flat), ZB.sample(flat)
    SA = {k: v.reshape(na, nd) for k, v in SA.items()}
    SB = {k: v.reshape(na, nd) for k, v in SB.items()}
    res = {"a": ZA.id, "b": ZB.id, "centres_km_apart": round(gap, 1), "overlap_km": round(overlap, 1),
           "overlap_mid_km": round(mid, 1), "q_m3s": args.q, "stations": {}}
    for name, d in (("B_edge", mid - edge), ("middle", mid), ("A_edge", mid + edge)):
        i = int(np.argmin(abs(dd - d)))
        A = {k: v[:, i] for k, v in SA.items()}
        B = {k: v[:, i] for k, v in SB.items()}
        res["stations"][name] = {"d_km": float(dd[i]), **station(A, B, args.step, args.q)}
    if args.owner:
        res["owner_line"] = owner_stations(ZA, ZB, Z(args.alone) if args.alone else None)
    name = args.name or f"{ZA.id}-{ZB.id}"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"seam-{name}.json").write_text(json.dumps(res, indent=1))
    if not args.no_png:
        render(SA, SB, along, dd, out / f"seam-{name}.png", 2, args.q, (ZA.id, ZB.id))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
