"""GPU prototype of climate._rain (numba-cuda, fp64; data resident on the device for all
iterations, one host<->device round trip per call). Compares against the CPU kernel at 16
(and 48 if NUMBA_NUM_THREADS allows) threads. gpuvenv/bin/python gpu_rain.py rain_L7.pkl"""
import os, sys, pickle, time, json, math
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numpy as np
import numba
from numba import cuda, float64
from planet import climate

LQ = climate.LQ
d = pickle.load(open(sys.argv[1], "rb"))
a = d["args"]
(qs, src_q, ocean, ls_rate, cv_rate, mse_t, mse_thr, warm, move, diffusion, in_w,
 in_src, in_off, deg, nbr_off, nbr_idx, iterations, fex, rh_c, rh_pow, cv_scale, et, evap, mean_mm) = a
S, n = qs.shape
print("S", S, "n", n, "iterations", iterations, "edges", len(nbr_idx), "in-edges", len(in_src))
res = {"S": S, "n": n, "iterations": iterations, "load": os.getloadavg(), "cpu_capture_s": d["cpu_s"]}


def cpu_bench(reps=3):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); out = climate._rain(*a); ts.append(time.perf_counter() - t0)
    return min(ts), float(np.median(ts)), out


for th in (16, 48):
    if th > numba.config.NUMBA_NUM_THREADS:
        continue
    numba.set_num_threads(th)
    climate._rain(*a)
    mn, md, ref = cpu_bench()
    res[f"cpu_{th}"] = (mn, md)
ref = d["out"]

TPB = 256


@cuda.jit
def k_tcor(ema, ocean, tcor, scale_arr, evap, n, S):
    i = cuda.grid(1)
    if i >= n or ocean[i]:
        return
    scale = scale_arr[0]
    for k in range(S):
        lp = math.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))


@cuda.jit
def k_partial(ema, part, n, S):
    # deterministic block sums: fixed tree in shared memory
    sh = cuda.shared.array(TPB, float64)
    tid = cuda.threadIdx.x
    i = cuda.blockIdx.x * TPB + tid
    v = 0.0
    if i < n:
        for k in range(S):
            v += ema[k, i]
    sh[tid] = v
    cuda.syncthreads()
    s = TPB // 2
    while s > 0:
        if tid < s:
            sh[tid] += sh[tid + s]
        cuda.syncthreads()
        s //= 2
    if tid == 0:
        part[cuda.blockIdx.x] = sh[0]


@cuda.jit
def k_final(part, nb, scale_arr, mean_mm, S, n):
    if cuda.grid(1) == 0:
        tot = 0.0
        for b in range(nb):
            tot += part[b]
        scale_arr[0] = mean_mm * S * n / max(tot, 1e-12)


@cuda.jit
def k_rain(k, p, last, m, moved, src_q, ocean, ema, et, warm, qs, ls_rate, rh_c, rh_pow, mse_t, tcor, mse_thr,
           cv_scale, cv_rate, fex, diffusion, nbr_off, nbr_idx, deg, acc, acc_ls, acc_up, acc_q, S):
    i = cuda.grid(1)
    if i >= m.shape[1]:
        return
    if p >= 0:
        t = 0.0
        for e in range(nbr_off[i], nbr_off[i + 1]):
            t += moved[p, nbr_idx[e]]
        m[p, i] = (1 - diffusion[p, i]) * moved[p, i] + diffusion[p, i] * t / deg[i]
    if ocean[i]:
        if src_q[k, i] > m[k, i]:
            if last:
                acc_up[k, i] += src_q[k, i] - m[k, i]
            m[k, i] = src_q[k, i]
    else:
        year = 0.0
        for j in range(S):
            year += ema[j, i]
        m[k, i] += et[i] * warm[k, i] * year / S
    q = m[k, i]
    excess = max(q - qs[k, i], 0.0)
    rh = min(q / max(qs[k, i], 1e-12) / rh_c, 1.0)
    rate = ls_rate[k, i] * rh ** rh_pow
    r_ls = rate * (q - excess)
    inst = (mse_t[k, i] + tcor[k, i] + LQ * q - mse_thr[k, i]) / cv_scale
    if inst > 0:
        rate += cv_rate[k, i] * min(inst, 2.0)
    r = fex * excess + rate * (q - excess)
    m[k, i] = q - r
    ema[k, i] += 0.05 * (r - ema[k, i])
    if last:
        acc[k, i] += r
        acc_ls[k, i] += r_ls
        acc_q[k, i] += q - r


@cuda.jit
def k_move(k, m, moved, move, in_off, in_src, in_w):
    i = cuda.grid(1)
    if i >= m.shape[1]:
        return
    mo = (1 - move[k, i]) * m[k, i]
    for e in range(in_off[i], in_off[i + 1]):
        j = in_src[e]
        mo += move[k, j] * m[k, j] * in_w[k, e]
    moved[k, i] = mo


def gpu_rain(H):
    """H: host inputs. Returns host outputs and (upload, compute, download) seconds."""
    t0 = time.perf_counter()
    D = {k: cuda.to_device(np.ascontiguousarray(v)) for k, v in H.items()}
    cuda.synchronize()
    t1 = time.perf_counter()
    m = cuda.to_device(H["src_q"])
    z = lambda: cuda.to_device(np.zeros((S, n)))
    acc, acc_ls, ema, tcor, acc_up, acc_q = z(), z(), z(), z(), z(), z()
    moved = cuda.device_array((S, n))
    nb = (n + TPB - 1) // TPB
    part = cuda.device_array(nb)
    scale = cuda.device_array(1)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        if evap != 0 and it >= 20 and it % 10 == 0:
            k_partial[nb, TPB](ema, part, n, S)
            k_final[1, 1](part, nb, scale, mean_mm, S, n)
            k_tcor[nb, TPB](ema, D["ocean"], tcor, scale, evap, n, S)
        last = it >= iterations - tail
        for k in range(S):
            p = k - 1 if k > 0 else (S - 1 if it > 0 else -1)
            k_rain[nb, TPB](k, p, last, m, moved, D["src_q"], D["ocean"], ema, D["et"], D["warm"], D["qs"],
                            D["ls_rate"], rh_c, rh_pow, D["mse_t"], tcor, D["mse_thr"], cv_scale, D["cv_rate"],
                            fex, D["diffusion"], D["nbr_off"], D["nbr_idx"], D["deg"], acc, acc_ls, acc_up, acc_q, S)
            k_move[nb, TPB](k, m, moved, D["move"], D["in_off"], D["in_src"], D["in_w"])
    cuda.synchronize()
    t2 = time.perf_counter()
    out = tuple(x.copy_to_host() / tail for x in (acc, acc_ls, acc_up, acc_q))
    t3 = time.perf_counter()
    return out, (t1 - t0, t2 - t1, t3 - t2)


H = dict(qs=qs, src_q=src_q, ocean=np.asarray(ocean), ls_rate=ls_rate, cv_rate=cv_rate, mse_t=mse_t,
         mse_thr=mse_thr, warm=warm, move=move, diffusion=diffusion, in_w=in_w, in_src=in_src, in_off=in_off,
         deg=deg, nbr_off=nbr_off, nbr_idx=nbr_idx, et=et)
gpu_rain(H)  # compile
runs = [gpu_rain(H) for _ in range(5)]
tot = [sum(r[1]) for r in runs]
best = runs[int(np.argmin(tot))]
res["gpu_total"] = (min(tot), float(np.median(tot)))
res["gpu_upload_compute_download"] = best[1]
res["launches_per_call"] = iterations * 2 * S + 3 * len([it for it in range(iterations) if it >= 20 and it % 10 == 0])
names = ("rain", "rain_ls", "sea_uptake", "vapour")
res["diff_maxabs_maxrel_meanrel"] = {
    nm: (float(np.abs(g - r).max()), float((np.abs(g - r) / np.maximum(np.abs(r), 1e-12)).max()),
         float((np.abs(g - r) / np.maximum(np.abs(r), 1e-12)).mean()))
    for nm, g, r in zip(names, best[0], ref)}
res["ref_scale"] = {nm: float(np.abs(r).max()) for nm, r in zip(names, ref)}
res["gpu_repeatable_bitwise"] = all(np.array_equal(x, y) for x, y in zip(runs[0][0], runs[1][0]))
print(json.dumps(res, indent=1))
