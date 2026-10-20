"""PW-030 evaluation: run a time zoom in memory, summarise swing, builds, terminations, interglacial ice.
usage: tz_eval.py TAG SOURCE KYR [k=v ...]   SOURCE: earth | <run_dir>@<myr> | l5test"""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path.cwd()))
from planet import timezoom as Z

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def source(s):
    if s == "earth":
        return Z.source_earth(6)
    d, at = s.split("@")
    return Z.source_from_run(Path(d), float(at))


def cycles(t, sl, min_swing=30.0):
    """Alternating extremes of sea level (highstands = max sl, lowstands = min sl) with hysteresis
    min_swing; returns list of (kind, t, sl)."""
    ext = []
    mode = None
    lo_i = hi_i = 0
    for i in range(len(sl)):
        if sl[i] > sl[hi_i]:
            hi_i = i
        if sl[i] < sl[lo_i]:
            lo_i = i
        if mode != "down" and sl[hi_i] - sl[i] >= min_swing:  # fell from a high
            ext.append(("high", hi_i)); mode = "down"; lo_i = i
        elif mode != "up" and sl[i] - sl[lo_i] >= min_swing:
            ext.append(("low", lo_i)); mode = "up"; hi_i = i
    return [(k, float(t[i]), float(sl[i])) for k, i in ext]


def summarise(res, src):
    ser = res["series"]
    t, sl = ser[:, 0], ser[:, 1]
    fr = res["frames"]
    ft = np.array([f["t"] for f in fr])
    ice_land = np.array([f["stats"]["ice_pct"] / max(f["stats"]["land_pct"], 1e-9) for f in fr])
    fsl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    burn = t >= 0
    out = {"min": float(sl.min()), "max": float(sl.max()), "swing": float(sl.max() - sl.min()),
           "t_min": float(t[sl.argmin()]), "mean": float(sl.mean()),
           "sl_at": {k: float(sl[np.searchsorted(t, k)]) for k in (20, 50, 100, 150, 300, 500) if k <= t[-1]},
           "ice_land_pct_start": float(100 * ice_land[0]),
           "ice_land_pct_p10_p90": [float(100 * np.percentile(ice_land, 10)), float(100 * np.percentile(ice_land, 90))],
           "ice_land_pct_min_max": [float(100 * ice_land.min()), float(100 * ice_land.max())]}
    ext = cycles(t, sl, 30.0)
    builds, terms, swings = [], [], []
    for a, b in zip(ext, ext[1:]):
        if a[0] == "high" and b[0] == "low":
            builds.append(round(b[1] - a[1], 1)); swings.append(round(a[2] - b[2], 1))
        elif a[0] == "low" and b[0] == "high":
            terms.append(round(b[1] - a[1], 1))
    out["extremes"] = [(k, round(tt, 1), round(s, 1)) for k, tt, s in ext]
    out["builds_kyr"], out["terms_kyr"], out["cycle_swings_m"] = builds, terms, swings
    # interglacial ice: ice share of land at the highstands
    hi = [e for e in ext if e[0] == "high"]
    out["interglacial_ice_land_pct"] = [round(float(100 * ice_land[np.argmin(np.abs(ft - e[1]))]), 1) for e in hi]
    lo = [e for e in ext if e[0] == "low"]
    out["glacial_ice_land_pct"] = [round(float(100 * ice_land[np.argmin(np.abs(ft - e[1]))]), 1) for e in lo]
    # spectrum of the sea level (detrended), periods of the top peaks
    x = sl - np.polyval(np.polyfit(t, sl, 1), t)
    dt = t[1] - t[0]
    f = np.fft.rfftfreq(len(x), dt)
    pw = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    order = np.argsort(pw[1:])[::-1][:5] + 1
    out["spectrum_top_periods_kyr"] = [round(1 / f[i], 1) for i in order]
    tot = pw[1:].sum()
    band = lambda lo_, hi_: float(pw[(f > 1 / hi_) & (f <= 1 / lo_)].sum() / tot)
    out["power_share"] = {"80-130": round(band(80, 130), 3), "35-50": round(band(35, 50), 3),
                          "18-25": round(band(18, 25), 3)}
    return out


def main():
    tag, s, kyr = sys.argv[1], sys.argv[2], float(sys.argv[3])
    kw = {}
    for a in sys.argv[4:]:
        k, v = a.split("=", 1)
        kw[k] = type(getattr(Z.TZParams(), k))(v)
    src = source(s)
    import os
    if os.environ.get("DT_SHIFT"):
        src = dict(src, dT=src["dT"] + float(os.environ["DT_SHIFT"]))
    t0 = time.time()
    res = Z.simulate(src, kyr, 0.5, 2.0, Z.TZParams(**kw))
    summ = summarise(res, src)
    summ.update(lake_m=res["budget"].get("lake", 0) / res["budget"]["ocean_area"], calved_m=res["budget"]["calved"] / res["budget"]["ocean_area"], tag=tag, source=s, params=kw, runtime_s=round(time.time() - t0),
                start_sea_level=src["sea_level"], start_ice_mkm3=float(res["series"][0, 2]))
    np.savez(OUT / f"{tag}.npz", series=res["series"],
             ice_land=np.array([f["stats"]["ice_pct"] / f["stats"]["land_pct"] for f in res["frames"]]),
             ft=np.array([f["t"] for f in res["frames"]]),
             dTg=np.array([f["stats"]["dT_global"] for f in res["frames"]]))
    (OUT / f"{tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "extremes"}))


if __name__ == "__main__":
    main()
