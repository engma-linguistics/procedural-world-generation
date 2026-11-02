"""Lane 137: before (main) vs after (density ladder) from the peoples_robust snapshot folders. Prints markdown; writes PNGs.
usage: python compare.py OUT_MAIN OUT_BRANCH PNG_DIR"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

A, B, PNG = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
BLUE, ORANGE, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#c3c2b7", "#1a1a19", "#6b6a63"


def load(d):
    out = {}
    for f in sorted(d.glob("*.json")):
        if f.name.endswith(".spec.json"):
            continue
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        if "peoples" in r:
            out[f.stem] = r
    return out


a, b = load(A), load(B)
common = sorted(set(a) & set(b))
print(f"runs: main {len(a)}, branch {len(b)}, both {len(common)}\n")


def fam(n):
    return "knob" if ("x0.5" in n or "x2-" in n) else "sm" if n.startswith("sm") else "dnd5" if n.startswith("dnd5") else \
        "dnd3" if n.startswith("dnd3") else "dnd+1" if n.startswith("dnd+1") else "dnd"


def med(rs, pid, key="share"):
    xs = [r["peoples"][pid][key] for r in rs if pid in r["peoples"]]
    return float(np.median(xs)) if xs else float("nan")


for tree in ("dnd", "sm"):
    names = [n for n in common if fam(n) == tree]
    if not names:
        continue
    ra, rb = [a[n] for n in names], [b[n] for n in names]
    pids = sorted({p for r in ra + rb for p in r["peoples"]}, key=lambda p: -max(med(ra, p), med(rb, p) if not np.isnan(med(rb, p)) else 0))
    print(f"### {tree}: {len(names)} paired runs (base + jitter), median over runs\n")
    print("| people | share before | after | cells led before | after | area Mkm2 before | after | extinct before | after | island fades before | after |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for p in pids:
        ea = sum(1 for r in ra if p in r["peoples"] and not r["peoples"][p]["alive"])
        eb = sum(1 for r in rb if p in r["peoples"] and not r["peoples"][p]["alive"])
        sa, sb = med(ra, p), med(rb, p)
        rows.append((p, sa, sb))
        print(f"| {p} | {sa:.1%} | {sb:.1%} | {med(ra, p, 'led'):.1%} | {med(rb, p, 'led'):.1%} | {med(ra, p, 'area_mkm2'):.1f} | "
              f"{med(rb, p, 'area_mkm2'):.1f} | {ea}/{len(ra)} | {eb}/{len(rb)} | {med(ra, p, 'faded'):.0f} | {med(rb, p, 'faded'):.0f} |")
    tpa = np.median([r["total_pop"] for r in ra]) / 1e6
    tpb = np.median([r["total_pop"] for r in rb]) / 1e6
    tops_a = [max(r["peoples"].values(), key=lambda v: v["share"])["share"] for r in ra]
    tops_b = [max(r["peoples"].values(), key=lambda v: v["share"])["share"] for r in rb]
    print(f"\ntotal people (median) {tpa:.0f} M -> {tpb:.0f} M; commonest share median {np.median(tops_a):.0%} -> {np.median(tops_b):.0%}\n")
    # chart: shares before/after
    rows = [r for r in rows if max(r[1], 0 if np.isnan(r[2]) else r[2]) >= 0.003][:18]
    fig, ax = plt.subplots(figsize=(7.5, 0.34 * len(rows) + 1.3), dpi=130)
    y = np.arange(len(rows))
    ax.barh(y - 0.2, [r[1] * 100 for r in rows], 0.38, color=BLUE, label="before (main)")
    ax.barh(y + 0.2, [0 if np.isnan(r[2]) else r[2] * 100 for r in rows], 0.38, color=ORANGE, label="after (density ladder)")
    ax.set_yticks(y, [r[0].replace("_", " ") for r in rows], color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("share of all people, % (median over runs)", color=MUTED)
    ax.set_title(f"{'D&D' if tree == 'dnd' else 'Seven Meals'}: who the people are, before and after ({len(names)} runs)", color=INK, loc="left", fontsize=10)
    ax.grid(axis="x", color="#e6e5df", lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(PNG / f"shares_{tree}.png"); plt.close(fig)

# ways of life by people, after (dnd base + jitter): share of each people's people per rung
RUNGS = ("forager", "fisher", "garden", "plough", "irrigation", "nomad", "agro_pastoral", "hold", "raider")
names = [n for n in common if fam(n) == "dnd"]
rb = [b[n] for n in names]
print("### Ways of life, after (dnd, share of each people's people on each rung, median over runs)\n")
print("| people | " + " | ".join(RUNGS) + " | mean presence |")
print("|---|" + "---|" * (len(RUNGS) + 1))
pids = sorted({p for r in rb for p in r["peoples"]}, key=lambda p: -med(rb, p))
for p in pids:
    sh = {k: [] for k in RUNGS}
    fill = []
    for r in rb:
        w = r["peoples"].get(p, {}).get("ways", {})
        tot = sum(v[0] for v in w.values())
        if tot <= 0:
            continue
        for k in RUNGS:
            sh[k].append(w.get(k, [0, 0, 0])[0] / tot)
        fill.append(tot / max(sum(v[2] for v in w.values()), 1e-9))
    if not fill:
        print(f"| {p} | " + " | ".join("-" for _ in RUNGS) + " | - |")
        continue
    print(f"| {p} | " + " | ".join((f"{np.median(sh[k]):.0%}" if np.median(sh[k]) >= 0.005 else "-") for k in RUNGS) + f" | {np.median(fill):.2f} |")

# realized density per rung vs ladder.md's sourced ranges (all dnd + sm after runs)
SRC = {"forager": (0.01, 0.41), "fisher": (0.1, 2.0), "garden": (2, 20), "plough": (2.5, 35), "irrigation": (30, 240),
       "nomad": (0.3, 2), "agro_pastoral": (1, 15), "hold": (None, None), "raider": (None, None)}
print("\n### Density by rung, after (all dnd and Seven Meals runs pooled): people per held km2 on that rung\n")
print("| rung | realized (per held km2) | at full presence (the rung's number there) | mean presence | sourced range (ladder.md) |")
print("|---|---|---|---|---|")
tot = {k: [0.0, 0.0, 0.0] for k in RUNGS}
for n in common:
    if fam(n) not in ("dnd", "sm"):
        continue
    for v in b[n]["peoples"].values():
        for k, x in v.get("ways", {}).items():
            for i in range(3):
                tot[k][i] += x[i]
pts = []
for k in RUNGS:
    t = tot[k]
    if t[1] <= 0:
        continue
    lo, hi = SRC[k]
    print(f"| {k} | {t[0] / t[1]:.3g} | {t[2] / t[1]:.3g} | {t[0] / max(t[2], 1e-9):.2f} | {'-' if lo is None else f'{lo:g}-{hi:g}'} |")
    pts.append((k, t[0] / t[1], t[2] / t[1], lo, hi))
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=130)
for i, (k, real, full, lo, hi) in enumerate(pts):
    if lo is not None:
        ax.plot([lo, hi], [i, i], color=GREY, lw=9, solid_capstyle="round", zorder=1, label="sourced range (ladder.md)" if i == 0 else None)
    ax.scatter([full], [i], s=55, color=BLUE, zorder=3, edgecolor="white", lw=1.5, label="the rung at full presence" if i == 0 else None)
    ax.scatter([real], [i], s=55, color=ORANGE, zorder=3, edgecolor="white", lw=1.5, label="realized, per held km2" if i == 0 else None)
ax.set_xscale("log")
ax.set_yticks(range(len(pts)), [p[0].replace("_", "-") for p in pts], color=INK)
ax.invert_yaxis()
ax.set_xlabel("people per km2 (log scale); irrigation's source is per watered km2, the model's per whole cell", color=MUTED, fontsize=8)
ax.set_title("Density by way of life after the change, against the published ranges", color=INK, loc="left", fontsize=10)
ax.grid(axis="x", color="#e6e5df", lw=0.8, which="both"); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig(PNG / "rungs.png"); plt.close(fig)

# whole-run invariants
print("\n### Per run: commonest people, extinctions\n")
print("| run | top before | top after | extinct before | extinct after |")
print("|---|---|---|---|---|")
for n in common:
    def top(r):
        p, v = max(r["peoples"].items(), key=lambda kv: kv[1]["share"])
        return f"{p} {v['share']:.0%}"
    ex = lambda r: ", ".join(p for p, v in r["peoples"].items() if not v["alive"]) or "-"
    print(f"| {n} | {top(a[n])} | {top(b[n])} | {ex(a[n])} | {ex(b[n])} |")
