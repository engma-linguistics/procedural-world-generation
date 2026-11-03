"""Lane 141, PW-1385 A: where the wild still feeds people, before and after (pooled over a robust-suite folder each). Reads
`forage_land` (tools/peoples_robust.py::forage_land). Tables: by biome, the share of peopled land led by the wild (cells whose people
are mostly on the forager, fisher or raider rung) and the share of people on it; by kind, its wild people's share, the wild-led land
(median Mkm2 a run), the runs where it leads wild land of at least 0.5 Mkm2, and the share of its farmable land it farms.
usage: python rich_foragers.py DIR_BEFORE DIR_AFTER [chart.png]"""
import json
import sys
from pathlib import Path

import numpy as np


def load(d):
    out = []
    for f in sorted(Path(d).glob("*.json")):
        if f.name.endswith(".spec.json") or f.name == "summary.json":
            continue
        r = json.loads(f.read_text())
        fl = r.get("forage_land") or {}
        if "biomes" in fl:
            out.append((r["name"], fl))
    return out


def biomes(runs):
    B = {}
    for _, fl in runs:
        for b, v in fl["biomes"].items():
            a = B.setdefault(b, np.zeros(4))
            a += [v["cells"], v["wild_cells"], v["pop"], v["wild_pop"]]
    return B


def kinds(runs):
    K = {}
    for _, fl in runs:
        for k, v in fl["peoples"].items():
            K.setdefault(k, []).append(v)
    return K


A, Bf = load(sys.argv[1]), load(sys.argv[2])
print(f"runs: before {len(A)}, after {len(Bf)}\n")
ba, bb = biomes(A), biomes(Bf)
pct = lambda x, y: f"{100 * x / y:.1f}%" if y > 0 else "-"  # noqa: E731
print("| biome | peopled cells (b / a) | wild-led land b | a | people on the wild b | a |")
print("|---|---|---|---|---|---|")
order = sorted(set(ba) | set(bb), key=lambda b: -bb.get(b, ba.get(b))[2])
for b in order:
    x, y = ba.get(b, np.zeros(4)), bb.get(b, np.zeros(4))
    print(f"| {b} | {x[0]:.0f} / {y[0]:.0f} | {pct(x[1], x[0])} | {pct(y[1], y[0])} | {pct(x[3], x[2])} | {pct(y[3], y[2])} |")
tx, ty = sum(ba.values()), sum(bb.values())
print(f"| **all** | {tx[0]:.0f} / {ty[0]:.0f} | {pct(tx[1], tx[0])} | {pct(ty[1], ty[0])} | {pct(tx[3], tx[2])} | {pct(ty[3], ty[2])} |\n")

ka, kb = kinds(A), kinds(Bf)
print("| people | wild people b | a | wild-led Mkm2, median b | a | runs with >= 0.5 Mkm2 wild-led b | a | farmable land farmed b | a |")
print("|---|---|---|---|---|---|---|---|---|")
order = sorted(set(ka) | set(kb), key=lambda k: -sum(v["pop"] for v in kb.get(k, ka.get(k, []))))
for k in order:
    row = [k]
    for K in (ka, kb):
        v = K.get(k, [])
        p, w = sum(x["pop"] for x in v), sum(x["wild_pop"] for x in v)
        row.append(pct(w, p))
    for K in (ka, kb):
        row.append(f"{np.median([x['wild_mkm2'] for x in K.get(k, [])] or [0]):.2f}")
    for K in (ka, kb):
        row.append(f"{sum(x['wild_mkm2'] >= 0.5 for x in K.get(k, []))}/{len(K.get(k, []))}")
    for K in (ka, kb):
        v = K.get(k, [])
        fa, fd = sum(x["farmable"] for x in v), sum(x["farmed"] for x in v)
        row.append(pct(fd, fa) if fa > 0 else "-")
    print("| " + " | ".join(row) + " |")

if len(sys.argv) > 3:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = [b for b in order if False] or sorted(set(ba) | set(bb), key=lambda b: -bb.get(b, ba.get(b))[0])
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    yy = np.arange(len(order))
    for ax, j, t in ((axs[0], (1, 0), "share of peopled land led by foragers or fishers"), (axs[1], (3, 2), "share of people living off the wild")):
        va = [100 * ba[b][j[0]] / max(ba[b][j[1]], 1e-9) if b in ba else 0 for b in order]
        vb = [100 * bb[b][j[0]] / max(bb[b][j[1]], 1e-9) if b in bb else 0 for b in order]
        ax.barh(yy - 0.2, va, 0.38, color="#b07a2a", label="before (main 4ae5191c)")
        ax.barh(yy + 0.2, vb, 0.38, color="#1f6fb5", label="after (rich wild resists farming)")
        ax.set_title(t, fontsize=10)
        ax.set_xlabel("%")
        ax.grid(axis="x", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].set_yticks(yy, order)
    axs[0].invert_yaxis()
    axs[1].legend(loc="upper right", fontsize=8, frameon=False)
    fig.suptitle(f"D&D preset, robust suite base + jitter ({len(A)} / {len(Bf)} runs, pooled), end of history (~1500 AD)", fontsize=10)
    fig.tight_layout()
    fig.savefig(sys.argv[3], dpi=110)
    print("chart", sys.argv[3])
