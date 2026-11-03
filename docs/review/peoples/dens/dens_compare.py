"""PW-1382 (lane 143): den peoples on the den ground, before vs after, from two tools/peoples_robust.py output directories (the same
14 D&D runs each). Prints the tables of round1.md and draws dens.png.

    uv run python docs/review/peoples/dens/dens_compare.py BEFORE_DIR AFTER_DIR [--png docs/review/peoples/dens/dens.png]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DEN = ("kobold", "goblin")


def load(d: Path) -> dict:
    out = {}
    for p in sorted(d.glob("*.json")):
        try:
            m = json.loads(p.read_text())
        except Exception:
            continue
        if isinstance(m, dict) and "peoples" in m and "den_ground" in m:
            out[p.stem] = m
    return out


def per_people(runs: dict) -> dict:
    """people -> {measure: [value per run]} (runs in name order)."""
    t: dict = {}
    for name in sorted(runs):
        m = runs[name]
        dg = m["den_ground"].get("peoples", {})
        for pid, o in m["peoples"].items():
            d = dg.get(pid, {})
            pop = d.get("pop", 0.0)
            r = t.setdefault(pid, {k: [] for k in ("share", "area", "alive", "pop_hi", "area_hi", "pop_broken", "fit_pop")})
            r["share"].append(o["share"])
            r["area"].append(o["area_mkm2"])
            r["alive"].append(o["alive"])
            r["pop_hi"].append(d.get("pop_hi", 0.0) / pop if pop > 0 else np.nan)
            r["area_hi"].append(d.get("mkm2_hi", 0.0) / d["mkm2"] if d.get("mkm2") else np.nan)
            r["pop_broken"].append(d.get("pop_broken", 0.0) / pop if pop > 0 else np.nan)
            r["fit_pop"].append(d.get("fit_pop", 0.0) / pop if pop > 0 else np.nan)
    return t


def med(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(np.median(x)) if len(x) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--png")
    a = ap.parse_args()
    B, A = load(Path(a.before)), load(Path(a.after))
    common = sorted(set(B) & set(A))
    B, A = {k: B[k] for k in common}, {k: A[k] for k in common}
    print(f"runs: {len(common)}")
    lb = [B[k]["den_ground"] for k in common]
    print("land on good den ground (>=0.5): median %.1f%%; broken country %.1f%%; mean den ground %.2f" % (
        100 * med([x["land_hi"] for x in lb]), 100 * med([x["land_broken"] for x in lb]), med([x["land_fit"] for x in lb])))
    tb, ta = per_people(B), per_people(A)
    print("\n| people | share b | a | range Mkm2 b | a | range on good den ground b | a | people on good den ground b | a | people on broken b | a | alive b | a |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = list(DEN) + sorted((p for p in ta if p not in DEN), key=lambda p: -med(ta[p]["share"]))
    for p in order:
        if p not in tb:
            continue
        b, x = tb[p], ta[p]
        print(f"| {p} | {100 * med(b['share']):.1f}% | {100 * med(x['share']):.1f}% | {med(b['area']):.2f} | {med(x['area']):.2f} | "
              f"{100 * med(b['area_hi']):.0f}% | {100 * med(x['area_hi']):.0f}% | {100 * med(b['pop_hi']):.0f}% | {100 * med(x['pop_hi']):.0f}% | "
              f"{100 * med(b['pop_broken']):.0f}% | {100 * med(x['pop_broken']):.0f}% | {sum(b['alive'])}/{len(b['alive'])} | {sum(x['alive'])}/{len(x['alive'])} |")
    print("\nper run, den kinds (share b -> a, range b -> a, people on good den ground b -> a):")
    for p in DEN:
        for i, k in enumerate(common):
            b, x = tb[p], ta[p]
            print(f"  {p:7s} {k:22s} {100 * b['share'][i]:5.1f}% -> {100 * x['share'][i]:5.1f}%   {b['area'][i]:6.2f} -> {x['area'][i]:6.2f} Mkm2"
                  f"   {100 * b['pop_hi'][i]:4.0f}% -> {100 * x['pop_hi'][i]:4.0f}%")
    non = [p for p in ta if p not in DEN and p in tb]
    rel = []
    for p in non:
        for i in range(len(common)):
            sb, sa = tb[p]["share"][i], ta[p]["share"][i]
            if sb > 0.005:
                rel.append(sa / sb - 1)
    rel = np.array(rel)
    print(f"\nnon-den peoples (share over 0.5%): relative share change median {100 * np.median(rel):+.1f}%, "
          f"10-90% {100 * np.percentile(rel, 10):+.1f}% .. {100 * np.percentile(rel, 90):+.1f}%")
    pooled = []
    for p in non:
        pb = sum(B[k]["peoples"][p]["pop"] for k in common) / sum(B[k]["total_pop"] for k in common)
        pa = sum(A[k]["peoples"][p]["pop"] for k in common) / sum(A[k]["total_pop"] for k in common)
        if pb > 0.005:
            pooled.append((p, pb, pa))
    print("non-den peoples, pooled over the runs (share b -> a): " + ", ".join(f"{p} {100 * x:.1f} -> {100 * y:.1f}" for p, x, y in
                                                                            sorted(pooled, key=lambda r: -r[1])))
    tot_b = [B[k]["total_pop"] for k in common]
    tot_a = [A[k]["total_pop"] for k in common]
    print(f"total people median {med(tot_b) / 1e6:.0f} -> {med(tot_a) / 1e6:.0f} million")
    if a.png:
        draw(tb, ta, non, common, a.png)


def draw(tb, ta, non, common, png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    B_C, A_C, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
    fig, axs = plt.subplots(1, 4, figsize=(15, 4.0))
    fig.patch.set_facecolor("#fcfcfb")
    panels = [("share", "share of all people", 100, "%"), ("area", "range (Mkm2)", 1, ""),
              ("pop_hi", "their people on good den ground", 100, "%")]
    x = np.arange(len(DEN))
    for ax, (key, title, sc, unit) in zip(axs[:3], panels):
        for j, (t, c, lab) in enumerate(((tb, B_C, "before (main 8c18ab01)"), (ta, A_C, "after (den ground)"))):
            v = [sc * med(t[p][key]) for p in DEN]
            lo = [sc * np.nanpercentile(t[p][key], 25) for p in DEN]
            hi = [sc * np.nanpercentile(t[p][key], 75) for p in DEN]
            ax.bar(x + (j - 0.5) * 0.36, v, 0.34, color=c, label=lab, edgecolor="#fcfcfb", linewidth=2)
            ax.errorbar(x + (j - 0.5) * 0.36, v, yerr=[np.subtract(v, lo), np.subtract(hi, v)], fmt="none", ecolor=MUTED, lw=1, capsize=3)
        ax.set_xticks(x, DEN)
        ax.set_title(title + " (median, IQR; 14 runs)", fontsize=9, color=INK)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8)
        ax.set_facecolor("#fcfcfb")
    axs[0].legend(fontsize=8, frameon=False)
    ax = axs[3]
    sb = [100 * med(tb[p]["share"]) for p in non]
    sa = [100 * med(ta[p]["share"]) for p in non]
    ax.scatter(sb, sa, s=40, color=A_C, edgecolor="#fcfcfb", linewidth=2, zorder=3)
    m = max(max(sb), max(sa)) * 1.08
    ax.plot([0, m], [0, m], color=MUTED, lw=1, ls="--", zorder=1)
    for p, u, v in zip(non, sb, sa):
        if u > 4:
            ax.annotate(p, (u, v), xytext=(4, -10), textcoords="offset points", fontsize=7, color=MUTED)
    ax.set_xlabel("share before, % (median)", fontsize=8, color=MUTED)
    ax.set_ylabel("share after, %", fontsize=8, color=MUTED)
    ax.set_title("the other peoples: share before vs after", fontsize=9, color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.set_facecolor("#fcfcfb")
    fig.suptitle("PW-1382: den peoples prefer den ground (D&D, worlds 4360a3 + af2677, seeds 7/10/13, jitters 1-4)", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


if __name__ == "__main__":
    main()
