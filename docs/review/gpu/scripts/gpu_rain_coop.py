"""Persistent cooperative-kernel variant of the _rain prototype: the whole iteration loop in one
launch, grid.sync() between phases. Runs gpu_rain.py first (same args) for the CPU and multi-launch
numbers. gpuvenv/bin/python gpu_rain_coop.py rain_L7.pkl"""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpu_rain.py")).read())


@cuda.jit
def k_all(m, moved, src_q, ocean, ema, et, warm, qs, ls_rate, rh_c, rh_pow, mse_t, tcor, mse_thr,
          cv_scale, cv_rate, fex, diffusion, nbr_off, nbr_idx, deg, acc, acc_ls, acc_up, acc_q, S,
          move, in_off, in_src, in_w, part, scale_arr, evap, mean_mm, iterations):
    g = cuda.cg.this_grid()
    n = m.shape[1]
    start = cuda.grid(1)
    stride = cuda.gridsize(1)
    tid = cuda.threadIdx.x
    sh = cuda.shared.array(TPB, float64)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        if evap != 0 and it >= 20 and it % 10 == 0:
            v = 0.0
            for i in range(start, n, stride):
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
            g.sync()
            if start == 0:
                tot = 0.0
                for b in range(cuda.gridDim.x):
                    tot += part[b]
                scale_arr[0] = mean_mm * S * n / max(tot, 1e-12)
            g.sync()
            scale = scale_arr[0]
            for i in range(start, n, stride):
                if not ocean[i]:
                    for k in range(S):
                        lp = math.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
                        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))
            g.sync()
        last = it >= iterations - tail
        for k in range(S):
            p = k - 1 if k > 0 else (S - 1 if it > 0 else -1)
            for i in range(start, n, stride):
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
            g.sync()
            for i in range(start, n, stride):
                mo = (1 - move[k, i]) * m[k, i]
                for e in range(in_off[i], in_off[i + 1]):
                    j = in_src[e]
                    mo += move[k, j] * m[k, j] * in_w[k, e]
                moved[k, i] = mo
            g.sync()


def gpu_rain_coop(H, nblocks):
    t0 = time.perf_counter()
    D = {k: cuda.to_device(np.ascontiguousarray(v)) for k, v in H.items()}
    cuda.synchronize()
    t1 = time.perf_counter()
    m = cuda.to_device(H["src_q"])
    z = lambda: cuda.to_device(np.zeros((S, n)))
    acc, acc_ls, ema, tcor, acc_up, acc_q = z(), z(), z(), z(), z(), z()
    moved = cuda.device_array((S, n))
    part = cuda.device_array(nblocks)
    scale = cuda.device_array(1)
    tail = max(iterations // 4, 1)
    k_all[nblocks, TPB](m, moved, D["src_q"], D["ocean"], ema, D["et"], D["warm"], D["qs"], D["ls_rate"], rh_c,
                        rh_pow, D["mse_t"], tcor, D["mse_thr"], cv_scale, D["cv_rate"], fex, D["diffusion"],
                        D["nbr_off"], D["nbr_idx"], D["deg"], acc, acc_ls, acc_up, acc_q, S, D["move"],
                        D["in_off"], D["in_src"], D["in_w"], part, scale, evap, mean_mm, iterations)
    cuda.synchronize()
    t2 = time.perf_counter()
    out = tuple(x.copy_to_host() / tail for x in (acc, acc_ls, acc_up, acc_q))
    t3 = time.perf_counter()
    return out, (t1 - t0, t2 - t1, t3 - t2)


dev = cuda.get_current_device()
sm = dev.MULTIPROCESSOR_COUNT
gpu_rain_coop(H, sm)  # compile
try:
    maxb = k_all.overloads[k_all.signatures[0]].max_cooperative_grid_blocks(TPB)
except Exception as e:  # noqa
    print("max_cooperative_grid_blocks failed:", e)
    maxb = 2 * sm
res2 = {"sm_count": sm, "max_coop_blocks": maxb}
for nbk in sorted({sm // 2, sm, 2 * sm, min(maxb, (n + TPB - 1) // TPB)}):
    if nbk > maxb:
        continue
    rs = [gpu_rain_coop(H, nbk) for _ in range(5)]
    tt = [sum(r[1]) for r in rs]
    b = rs[int(np.argmin(tt))]
    res2[f"coop_{nbk}blocks_total"] = (min(tt), float(np.median(tt)))
    res2[f"coop_{nbk}blocks_up_compute_down"] = b[1]
    res2[f"coop_{nbk}blocks_maxrel"] = max(float((np.abs(g_ - r) / np.maximum(np.abs(r), 1e-12)).max())
                                           for g_, r in zip(b[0], ref))
    res2[f"coop_{nbk}blocks_repeatable"] = all(np.array_equal(x, y) for x, y in zip(rs[0][0], rs[1][0]))
print(json.dumps(res2, indent=1))
