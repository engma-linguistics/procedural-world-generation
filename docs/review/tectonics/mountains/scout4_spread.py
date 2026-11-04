"""PW-1446 scout 193: what widens the late-dT spread between two judge arms (reads scout4_table.py's JSON).

    uv run python docs/review/tectonics/mountains/scout4_spread.py table.json [--a main --b cap]

Prints, per arm over the 36 judged draws (rolls 0.0005 and 0.001): the spread (sd across draws) of late dT and of each
part of the carbon balance, ln source_raw - ln w_supply - ln w_plant - ln w_temp = ln co2_law(X) + YARDSTICK, their
correlations with dT, the within-run sensitivities, and the paired changes (b - a) against the change in |dT - arm
mean| (does a draw that moved out to a tail also lose supply, high land or the climate factor's slope?).
"""
import argparse
import json

import numpy as np

KEYS = ("dT", "co2", "co2_term", "albedo_term", "ghg", "drift", "star", "land", "w_area", "iced_land", "ln_source_raw",
        "ln_w_supply", "ln_w_plant", "ln_w_temp", "ln_sink_raw", "force", "w_rate", "w_T", "w_q", "w_bare", "w_a",
        "b_w_temp", "b_w_supply", "b_w_T", "b_w_q", "b_w_area", "b_w_rate", "r_src_sup_time", "sd_dT", "sd_ln_supply", "sd_co2", "plume_src")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--a", default="main")
    ap.add_argument("--b", default="cap")
    a = ap.parse_args()
    rows = json.load(open(a.table))
    arms = {}
    for r in rows:
        if not (r["draw"].startswith("r0.0005_") or r["draw"].startswith("r0.001_")):
            continue
        r["force"] = r["ln_source_raw"] - r["ln_w_supply"]
        arms.setdefault(r["arm"], {})[r["draw"]] = r
    A, B = arms[a.a], arms[a.b]
    draws = sorted(set(A) & set(B))
    print(len(draws), "paired draws")

    def col(arm, k):
        return np.array([arm[d].get(k) if arm[d].get(k) is not None else np.nan for d in draws], float)

    print(f"{'measure':14s} {'mean a':>8s} {'mean b':>8s} {'sd a':>7s} {'sd b':>7s} {'r(dT) a':>8s} {'r(dT) b':>8s}"
          f" {'paired d':>9s} {'r(d,d|dT|)':>10s}")
    dA, dB = col(A, "dT"), col(B, "dT")
    ddev = np.abs(dB - dB.mean()) - np.abs(dA - dA.mean())
    for k in KEYS:
        x, y = col(A, k), col(B, k)
        m = ~np.isnan(x) & ~np.isnan(y)
        ra = np.corrcoef(x[m], dA[m])[0, 1] if m.sum() > 3 else np.nan
        rb = np.corrcoef(y[m], dB[m])[0, 1] if m.sum() > 3 else np.nan
        rd = np.corrcoef(y[m] - x[m], ddev[m])[0, 1] if m.sum() > 3 else np.nan
        print(f"{k:14s} {np.nanmean(x):8.3f} {np.nanmean(y):8.3f} {np.nanstd(x, ddof=1):7.3f} {np.nanstd(y, ddof=1):7.3f}"
              f" {ra:8.2f} {rb:8.2f} {np.nanmean(y - x):9.3f} {rd:10.2f}")
    # the hypsometry: cap has it on all draws, main only on the screen's 8
    for k in ("h_p2", "h_p3", "h_p4", "h_max"):
        x, y = col(A, k), col(B, k)
        m = ~np.isnan(x)
        print(f"{k}: b mean {np.nanmean(y):.3f} sd {np.nanstd(y, ddof=1):.3f}, r(dT b) {np.corrcoef(y, dB)[0, 1]:.2f},"
              f" r(|dT-mean| b) {np.corrcoef(y, np.abs(dB - dB.mean()))[0, 1]:.2f};"
              f" paired on {m.sum()} draws: a {np.mean(x[m]):.3f} b {np.mean(y[m]):.3f}")
    # the two parts of the spread: the forcing's (outgassing against erosion supply) and the loop's gain
    rng = np.random.default_rng(0)
    for name, arm, dT in ((a.a, A, dA), (a.b, B, dB)):
        src, sup, tm = col(arm, "ln_source_raw"), col(arm, "ln_w_supply"), col(arm, "ln_w_temp")
        f = src - sup - col(arm, "ln_w_plant")
        boot = []
        for _ in range(2000):
            i = rng.integers(0, len(draws), len(draws))
            boot.append((np.corrcoef(src[i], sup[i])[0, 1], np.polyfit(dT[i], tm[i], 1)[0], np.polyfit(f[i], dT[i], 1)[0]))
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
        print(f"{name}: r(ln source, ln supply) {np.corrcoef(src, sup)[0, 1]:.2f} [{lo[0]:.2f}, {hi[0]:.2f}];"
              f" sd(forcing) {f.std(ddof=1):.3f}; d ln w_temp / d dT {np.polyfit(dT, tm, 1)[0]:.4f}"
              f" [{lo[1]:.4f}, {hi[1]:.4f}]; d dT / d forcing {np.polyfit(f, dT, 1)[0]:.1f} [{lo[2]:.1f}, {hi[2]:.1f}]")
    print("\nper draw (b - a): dT a, dT b, d ln supply, d ln source, d ln plant, d ln temp, d co2, d albedo, h_p3 b")
    for i, d in enumerate(draws):
        g = lambda k: (B[d].get(k) or np.nan) - (A[d].get(k) or np.nan)  # noqa: E731
        print(f"{d:24s} {dA[i]:6.2f} {dB[i]:6.2f} {g('ln_w_supply'):6.2f} {g('ln_source_raw'):6.2f}"
              f" {g('ln_w_plant'):6.2f} {g('ln_w_temp'):6.2f} {g('co2'):6.2f} {g('albedo_term'):6.2f}"
              f" {B[d].get('h_p3', np.nan):5.2f}")


if __name__ == "__main__":
    main()
