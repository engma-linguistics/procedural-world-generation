"""Lane 139 (PW-1373): ways of life per kind, before vs after, from peoples_robust snapshot folders. Prints markdown; writes a PNG.
usage: python hunters_lag.py OUT_BEFORE OUT_AFTER [OUT_AFTER2 ...] --png PNG [--labels before,10x,5x]
Runs: the D&D base + jitter variants (names dnd-s*, dnd-j*). A cell's people count on its main rung (as lane 137's tables)."""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

args = sys.argv[1:]
png = Path(args[args.index("--png") + 1]); del args[args.index("--png"):args.index("--png") + 2]
labels = None
if "--labels" in args:
    labels = args[args.index("--labels") + 1].split(","); del args[args.index("--labels"):args.index("--labels") + 2]
dirs = [Path(a) for a in args]
labels = labels or [d.name for d in dirs]
COLS = ["#2a78d6", "#eb6834", "#1f9e89"]
INK, MUTED = "#1a1a19", "#6b6a63"
WAYS = {"forager": ("forager", "fisher", "raider"), "herder": ("nomad",), "agro-pastoral": ("agro_pastoral",), "garden": ("garden",),
        "plough": ("plough",), "irrigation": ("irrigation",), "hold": ("hold",)}
FARM = ("agro-pastoral", "garden", "plough", "irrigation", "hold")


def load(d, tree="dnd"):
    out = {}
    for f in sorted(d.glob("*.json")):
        if f.name.endswith(".spec.json") or not (f.stem.startswith(f"{tree}-s") or f.stem.startswith(f"{tree}-j")):
            continue
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        if "peoples" in r:
            out[f.stem] = r
    return out


def table(runs):
    """{people: (median share of all people, {way: pooled share of its people}, runs where < 5% of it farm / runs it lives in)}"""
    ids = sorted({p for r in runs.values() for p in r["peoples"]})
    res = {}
    for p in ids:
        sh = [r["peoples"][p]["share"] for r in runs.values() if p in r["peoples"]]
        pool = {w: 0.0 for w in WAYS}
        low = live = 0
        for r in runs.values():
            ways = r["peoples"].get(p, {}).get("ways", {})
            tot = sum(v[0] for v in ways.values())
            if tot <= 0:
                continue
            live += 1
            farm = 0.0
            for w, rs in WAYS.items():
                x = sum(ways.get(k, [0])[0] for k in rs)
                pool[w] += x
                farm += x if w in FARM else 0.0
            low += farm / tot < 0.05
        t = sum(pool.values()) or 1.0
        res[p] = (float(np.median(sh)) if sh else 0.0, {w: v / t for w, v in pool.items()}, low, live)
    return res


T = [table(load(d)) for d in dirs]
print(f"runs: " + ", ".join(f"{lab} {len(load(d))}" for lab, d in zip(labels, dirs)) + "\n")
order = sorted(T[0], key=lambda p: -T[-1].get(p, (0,))[0])
pct = lambda x: "-" if x < 0.005 else f"{100 * x:.0f}%"  # noqa: E731
for lab, t in zip(labels, T):
    print(f"### {lab}\n")
    print("| people | share of all people | " + " | ".join(WAYS) + " | farming | runs < 5% farming |")
    print("|---|---|" + "---|" * (len(WAYS) + 2))
    for p in order:
        if p not in t:
            continue
        s, w, low, live = t[p]
        print(f"| {p} | {100 * s:.1f}% | " + " | ".join(pct(w[k]) for k in WAYS) + f" | {pct(sum(w[k] for k in FARM))} | {low}/{live} |")
    print()

KINDS = ["tabaxi", "leonin", "goliath", "bugbear", "firbolg", "goblin", "kenku", "orc", "elf", "dragonborn", "human"]
KINDS = [k for k in KINDS if all(k in t for t in T)]
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=130)
y = np.arange(len(KINDS))
hgt = 0.8 / len(T)
for i, (lab, t) in enumerate(zip(labels, T)):
    v = [100 * sum(t[k][1][w] for w in FARM) for k in KINDS]
    ax.barh(y + (i - (len(T) - 1) / 2) * hgt, v, height=hgt * 0.9, color=COLS[i], label=lab)
ax.set_yticks(y, [k.replace("_", " ") for k in KINDS], color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("share of the kind's people living by farming (garden, plough, irrigation, agro-pastoral), %", color=MUTED)
ax.set_title("Hunting kinds learn crops later (PW-1373): D&D base + jitter runs, pooled", color=INK, fontsize=11, loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#e4e3dc", lw=0.6)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(png)
print(f"wrote {png}")
