"""The parallel kernels of the speed pass (PW-256/257) give the same bits as
the serial loops they replaced, at any numba thread count (PW-215): no
reductions whose summation order follows the thread split. Level 5, fast."""

import numba
import numpy as np
import pytest
from numba import njit

from planet import climate as C, timezoom as Z, timezoom_kernels as K
from planet.grid import build_grid

THREADS = sorted({1, 2, numba.config.NUMBA_NUM_THREADS})


@pytest.fixture(scope="module")
def g5():
    return build_grid(5)


def _at_threads(fn):
    """fn() at each thread count, the outputs as bytes."""
    old = numba.get_num_threads()
    try:
        out = []
        for t in THREADS:
            numba.set_num_threads(t)
            out.append(fn())
        return out
    finally:
        numba.set_num_threads(old)


def _same(outs, ref):
    for o in outs:
        assert len(o) == len(ref)
        for a, b in zip(o, ref):
            assert np.asarray(a).tobytes() == np.asarray(b).tobytes()


# --- the serial versions as they were before PW-257 (the references) ---

@njit
def _coarse_smooth_serial(f, cidx, nc, off, idx, sk, iters, cand, w):
    tot = np.zeros(nc)
    cnt = np.zeros(nc)
    for i in range(f.shape[0]):
        for k in range(cand.shape[1]):
            tot[cand[i, k]] += w[i, k] * f[i]
            cnt[cand[i, k]] += w[i, k]
    c = tot / np.maximum(cnt, 1e-12)
    g = np.empty(nc)
    for _ in range(iters):
        for j in range(nc):
            t = 0.0
            for e in range(off[j], off[j + 1]):
                t += sk[e] * (c[idx[e]] - c[j])
            g[j] = c[j] + t
        c[:] = g
    out = np.zeros(f.shape[0])
    for i in range(f.shape[0]):
        for k in range(cand.shape[1]):
            out[i] += w[i, k] * c[cand[i, k]]
    return out


@njit
def _sia_flow_serial(H, bed, sl, active, off, idx, dist, elen, ux, uy, uz, area, gamma, d_cap, dt_total, cfl,
                     flt, d2min, hold):
    na = active.shape[0]
    n = H.shape[0]
    D = np.zeros(n)
    out = np.zeros(n)
    dV = np.zeros(n)
    t = 0.0
    nsub = 0
    while t < dt_total - 1e-9:
        dmax = 0.0
        for a in range(na):
            i = active[a]
            if H[i] <= 0.0:
                D[i] = 0.0
                continue
            si = K._surf(bed, H, sl, flt, i)
            gx, gy, gz = 0.0, 0.0, 0.0
            down2 = 0.0
            for e in range(off[i], off[i + 1]):
                sj = K._surf(bed, H, sl, flt, idx[e])
                w = 0.5 * elen[e] * (sj - si)
                gx += w * ux[e]
                gy += w * uy[e]
                gz += w * uz[e]
                if sj < si:
                    down2 = max(down2, ((si - sj) / dist[e]) ** 2)
            g2 = max((gx * gx + gy * gy + gz * gz) / (area[i] * area[i]), down2)
            h2 = H[i] * H[i]
            d = min(gamma * h2 * h2 * H[i] * g2, d_cap)
            D[i] = d
            dmax = max(dmax, d)
        if dmax <= 0.0:
            break
        dt = min(dt_total - t, cfl * d2min / dmax)
        for a in range(na):
            i = active[a]
            out[i] = 0.0
            if H[i] <= 0.0:
                continue
            si = K._surf(bed, H, sl, flt, i)
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - K._surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    out[i] += q * K._held(bed, H, sl, flt, hold, i, j)
        for a in range(na):
            i = active[a]
            if out[i] <= 0.0:
                continue
            need = dt * out[i]
            held = H[i] * area[i]
            scale = 1.0 if need <= held else held / need
            si = K._surf(bed, H, sl, flt, i)
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - K._surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    v = q * K._held(bed, H, sl, flt, hold, i, j) * scale * dt
                    dV[i] -= v
                    dV[j] += v
        for a in range(na):
            i = active[a]
            if dV[i] != 0.0:
                H[i] = max(0.0, H[i] + dV[i] / area[i])
                dV[i] = 0.0
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                if dV[j] != 0.0:
                    H[j] = max(0.0, H[j] + dV[j] / area[j])
                    dV[j] = 0.0
        t += dt
        nsub += 1
    return nsub


def test_coarse_smooth(g5):
    rng = np.random.default_rng(1)
    f = rng.normal(size=g5.n) + np.sin(3 * g5.lat / 57.3)
    for lev in (2, 3):
        M = C._coarse(g5, lev)
        args = (f, M["cidx"], M["n"], M["off"], M["idx"], M["sk"], 7, M["cand"], M["w"])
        ref = _coarse_smooth_serial(*args)
        _same(_at_threads(lambda: [C._coarse_smooth(*args, M["inv_off"], M["inv"])]), [ref])


def test_climate_step(g5):
    """Bit-identical to the same loop compiled serially."""
    rng = np.random.default_rng(2)
    n = g5.n
    lat = g5.lat
    land = rng.random(n) < 0.4
    t_warm = 25 - 0.5 * np.abs(lat) + rng.normal(0, 3, n)
    t_cold = t_warm - 5 - 0.4 * np.abs(lat)
    band = np.clip(((lat + 90) / Z.BAND_DEG).astype(np.int64), 0, len(Z.BAND_LAT) - 1)
    dq = rng.normal(0, 20, (len(Z.BAND_LAT), 12))
    h = np.where(land & (np.abs(lat) > 55), rng.random(n) * 2000, 0.0)
    ins = (land, lat >= 0, 0.5 * (t_warm + t_cold), 0.5 * (t_warm - t_cold), rng.random(n) * 1500,
           rng.random(n) * 1500, -0.0065 * h, rng.normal(0, 1, n), rng.random(n) * 0.04, band, dq,
           np.clip(h / 500, 0, 1), np.clip(h / 50, 0, 1), 5.0, rng.random(n) * 0.5, 0.3, 0.4, 300.0,
           4.5, 3.0, 8.0, 0.4, 0.07)

    def run(fn):
        outs = [np.zeros(n) for _ in range(6)]
        fn(*ins, *outs)
        return outs
    ref = run(njit(K.climate_step.py_func))
    assert (ref[0] != 0).any() and (ref[5] > 0).any()
    _same(_at_threads(lambda: run(K.climate_step)), ref)


def test_sia_flow(g5):
    """A few ice caps on rough ground flowing for 20 kyr: the parallel
    gather moves the same ice as the serial scatter did, to the bit."""
    G = Z.geometry(g5)
    rng = np.random.default_rng(3)
    n = g5.n
    bed = 600 * np.sin(5 * g5.centers[:, 0]) * np.cos(4 * g5.centers[:, 1]) + rng.normal(0, 150, n)
    H = np.zeros(n)
    for c in rng.choice(n, 6, replace=False):
        d = np.arccos(np.clip(g5.centers @ g5.centers[c], -1, 1))
        H += np.maximum(0, 2500 * (1 - (d / 0.25) ** 2))
    H[rng.random(n) < 0.02] += 30  # (and some lone films, cells next to nothing)
    flt = 1 - Z.RHO_I / Z.RHO_W
    p = Z.TZParams()
    gamma = 2 * p.flow_a * p.enhancement * (Z.RHO_I * 9.81) ** 3 / 5
    active = np.flatnonzero(K.dilate(H > 0, g5.nbr_off, g5.nbr_idx, 2))
    hold = np.where(rng.random(n) < 0.3, 0.8, 0.0)  # (some grounding lines buttressed, PW-367)

    def run(fn, H0):
        h = H0.copy()
        ns = fn(h, bed, -40.0, active, g5.nbr_off, g5.nbr_idx, G["dist"], G["elen"], G["ux"], G["uy"], G["uz"],
                G["area"], gamma, p.d_cap, 20000.0, p.cfl, flt, G["d2min"], hold)
        return [h, np.array([ns])]
    ref = run(_sia_flow_serial, H)
    assert ref[1][0] > 3 and not np.array_equal(ref[0], H)
    assert abs((ref[0] * G["area"]).sum() / (H * G["area"]).sum() - 1) < 1e-12  # (ice conserved)
    _same(_at_threads(lambda: run(K.sia_flow, H)), ref)
