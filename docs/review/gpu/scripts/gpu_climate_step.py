"""GPU prototype of timezoom_kernels.climate_step (numba-cuda, fp64 and fp32), against the CPU
kernel serial (as shipped) and a prange copy at 16/48 threads. Run in the scratch GPU venv:
gpuvenv/bin/python gpu_climate_step.py capture.pkl [tile]"""
import os, sys, pickle, time, math
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numpy as np
import numba
from numba import njit, prange, cuda, float32
from planet import timezoom_kernels as TK

DAYS, SQRT2PI = TK.DAYS, TK.SQRT2PI
d = pickle.load(open(sys.argv[1], "rb"))
tile = int(sys.argv[2]) if len(sys.argv) > 2 else 1
a = d["args"]
# args: land north t_mean half p_jul p_jan dt_base dt_wet k_orb band dq f_ice f_alb cool damp hold bare_share
# snow_w sigma ddf_snow ddf_ice refreeze precip_k | smb t_ann t_warm t_cold p_scale f_sum
ins, outs = a[:23], a[23:]


def tl(x):
    if isinstance(x, np.ndarray) and x.ndim == 1:
        return np.tile(x, tile)
    return x


ins = [tl(x) for x in ins]
n = ins[2].shape[0]
print("cells", n, "dq", ins[10].shape, "k_orb nonzero", bool(np.any(ins[8])))
new_outs = lambda dt=np.float64: [np.zeros(n, dt) for _ in range(6)]

# CPU: shipped serial kernel, and a prange copy (same body)
src = TK.climate_step.py_func


def make_par():
    import inspect, textwrap
    s = textwrap.dedent(inspect.getsource(src)).split("\n", 1)[1]  # drop decorator
    s = s.replace("for i in range(n):", "for i in prange(n):", 1)
    ns = {"math": math, "prange": prange, "DAYS": DAYS, "SQRT2PI": SQRT2PI}
    exec(s, ns)
    return njit(parallel=True)(ns["climate_step"])


par = make_par()


def bench(fn, reps=7):
    ts = []
    for _ in range(reps):
        o = new_outs()
        t0 = time.perf_counter()
        fn(o)
        ts.append(time.perf_counter() - t0)
    return min(ts), float(np.median(ts)), o


ser_t = bench(lambda o: TK.climate_step(*ins, *o))
ref = ser_t[2]
res = {"n": n, "load": os.getloadavg()}
res["cpu_serial"] = ser_t[:2]
for th in (16, 48):
    numba.set_num_threads(min(th, numba.config.NUMBA_NUM_THREADS))
    par(*ins, *new_outs())  # compile
    pt = bench(lambda o: par(*ins, *o))
    res[f"cpu_prange_{numba.get_num_threads()}"] = pt[:2]
    assert all(np.array_equal(x, y) for x, y in zip(pt[2], ref)), "prange differs from serial"


def make_gpu(ft):
    @cuda.jit
    def k(land, north, t_mean, half, p_jul, p_jan, dt_base, dt_wet, k_orb, band, dq, f_ice, f_alb,
          cool, damp, hold, bare_share, snow_w, sigma, ddf_snow, ddf_ice, refreeze, precip_k,
          smb, t_ann, t_warm, t_cold, p_scale, f_sum):
        i = cuda.grid(1)
        if i >= t_mean.shape[0]:
            return
        peak = 3 if north[i] else 9
        b = band[i]
        osum = ft(0.0)
        for m in range(12):
            osum += k_orb[i] * ft(0.5) * (dq[b, m] + dq[b, (m + 11) % 12])
        ps = math.exp(precip_k * (dt_wet[i] + osum / ft(12.0)))
        ps = min(ft(3.0), max(ft(0.02), ps))
        p_scale[i] = ps
        tsum, tmax, tmin = ft(0.0), ft(-1e9), ft(1e9)
        lying, snow, lost, ice_melt = ft(0.0), ft(0.0), ft(0.0), ft(0.0)
        fs, ns = ft(0.0), 0
        bare = bare_share * f_alb[i]
        for kk in range(12):
            m = (peak + 3 + kk) % 12
            d_orb = k_orb[i] * ft(0.5) * (dq[b, m] + dq[b, (m + 11) % 12])
            sw = half[i] * math.cos(ft(2 * math.pi) * (m - peak) / ft(12.0))
            lit = min(ft(1.0), lying / snow_w) if land[i] else ft(0.0)
            f = lit + (ft(1.0) - lit) * bare
            if sw > 0.0:
                fs += f
                ns += 1
                sw *= ft(1.0) - f * damp[i]
            t = t_mean[i] + dt_base[i] + sw + d_orb - f_ice[i] * cool
            if f > 0.0 and t > 0.0:
                t *= ft(1.0) - f * (ft(1.0) - hold)
            tsum += t
            tmax = max(tmax, t)
            tmin = min(tmin, t)
            if land[i]:
                sf = min(ft(1.0), max(ft(0.0), ft(0.5) - t / ft(4.0)))
                p = p_jul[i] if m < 6 else p_jan[i]
                fall = sf * p / ft(12.0) * ps
                snow += fall
                lying += fall
                x = t / sigma
                pdd = ft(DAYS) * (sigma / ft(SQRT2PI) * math.exp(ft(-0.5) * x * x)
                                  + ft(0.5) * t * math.erfc(-x / ft(math.sqrt(2.0))))
                melt = min(lying, ddf_snow * pdd)
                lying -= melt
                lost += (ft(1.0) - refreeze) * melt
                ice_melt += ddf_ice * (pdd - melt / ddf_snow)
        t_ann[i], t_warm[i], t_cold[i] = tsum / ft(12.0), tmax, tmin
        f_sum[i] = fs / max(ns, 1)
        if land[i]:
            smb[i] = (snow - lost - ice_melt) / ft(917.0)
        else:
            smb[i] = ft(0.0)
    return k


for name, ft, dt in (("fp64", np.float64, np.float64), ("fp32", np.float32, np.float32)):
    k = make_gpu(ft)
    cast = [(x.astype(dt) if isinstance(x, np.ndarray) and x.dtype == np.float64 else
             (dt(x) if isinstance(x, float) else x)) for x in ins]
    tpb = 128
    blocks = (n + tpb - 1) // tpb
    # device-resident timing (inputs already on the GPU), and with transfers both ways
    dins = [cuda.to_device(x) if isinstance(x, np.ndarray) else x for x in cast]
    douts = [cuda.device_array(n, dt) for _ in range(6)]
    k[blocks, tpb](*dins, *douts); cuda.synchronize()
    ts = []
    for _ in range(20):
        t0 = time.perf_counter(); k[blocks, tpb](*dins, *douts); cuda.synchronize(); ts.append(time.perf_counter() - t0)
    res[f"gpu_{name}_resident"] = (min(ts), float(np.median(ts)))
    ts = []
    for _ in range(10):
        t0 = time.perf_counter()
        di = [cuda.to_device(x) if isinstance(x, np.ndarray) else x for x in cast]
        do = [cuda.device_array(n, dt) for _ in range(6)]
        k[blocks, tpb](*di, *do)
        got = [x.copy_to_host() for x in do]
        ts.append(time.perf_counter() - t0)
    res[f"gpu_{name}_with_transfer"] = (min(ts), float(np.median(ts)))
    diffs = {}
    for nm, g, r in zip(("smb", "t_ann", "t_warm", "t_cold", "p_scale", "f_sum"), got, ref):
        ad = np.abs(g.astype(np.float64) - r)
        diffs[nm] = (float(ad.max()), float((ad / np.maximum(np.abs(r), 1e-6)).max()),
                     float(ad.mean()))
    res[f"gpu_{name}_diff_maxabs_maxrel_meanabs"] = diffs
    # determinism on the device: rerun, compare bits
    do2 = [cuda.device_array(n, dt) for _ in range(6)]
    k[blocks, tpb](*dins, *do2)
    res[f"gpu_{name}_bitwise_repeatable"] = all(np.array_equal(x.copy_to_host(), y.copy_to_host())
                                                 for x, y in zip(douts, do2))
import json
print(json.dumps(res, indent=1))
