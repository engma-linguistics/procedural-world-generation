"""Charts for lane 97's report (docs/review/peoples-brakes/report.md): the commonest people's share and the top-6 shares per tree and
world, across the stages and across a sweep of the brakes' dials, from lane 77 suite result folders.

    uv run python docs/review/peoples-brakes/charts.py STAGES.json

STAGES.json: {"stages": {"main": DIR, "after D27": DIR, "after D25": DIR}, "sweep": {"raiders=0 war=0": DIR, ...}} (each DIR a
tools/peoples_robust.py run --out folder). Writes PNGs and data.json beside this file."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
TREES = [("dnd", "full dnd tree"), ("dnd5", "dnd, five peoples"), ("dnd3", "dnd, three peoples"), ("seven_meals", "Seven Meals")]
WORLDS = ["4360a3", "af2677"]
# the reference palette (dataviz skill, references/palette.md), light mode, in its fixed order; one hue per people, never by rank
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
PEOPLE_ORDER = ["human", "elf", "halfling", "hobgoblin", "kobold", "dwarf", "gnome", "half_orc", "orc", "goblin", "dragonborn",
                "cervid_folk", "lizardfolk", "kenku"]
OTHER = "#b9b8b2"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def load(d):
    out = []
    for f in sorted(Path(d).glob("*.json")):
        if f.name.endswith(".spec.json") or f.name == "summary.json":
            continue
        r = json.loads(f.read_text())
        if "peoples" not in r or r.get("family") not in ("base", "subset"):
            continue
        out.append({"tree": r["tree"], "world": r["world"], "seed": r["seed"],
                    "shares": {k: v["share"] for k, v in r["peoples"].items()}})
    return out


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def commonest(runs, tree, world, seeds=None):
    return [100 * max(r["shares"].values()) for r in runs if r["tree"] == tree and r["world"] == world
            and (seeds is None or r["seed"] in seeds)]


def chart_stages(stages, path):
    """Small multiples, tree x world: the commonest people's share per run (dots, one per seed) and the median (line), per stage."""
    names = list(stages)
    fig, axs = plt.subplots(2, 4, figsize=(13, 6), sharey=True, facecolor=SURF)
    for j, (t, tl) in enumerate(TREES):
        for i, w in enumerate(WORLDS):
            ax = axs[i, j]
            style(ax)
            med = []
            for x, n in enumerate(names):
                v = commonest(stages[n], t, w)
                if v:
                    ax.scatter(np.full(len(v), x) + np.linspace(-0.08, 0.08, len(v)), v, s=22, color=PAL[0], alpha=0.55, lw=0)
                    med.append((x, float(np.median(v))))
            if med:
                ax.plot(*zip(*med), color=PAL[0], lw=2, marker="o", ms=6, mec=SURF, mew=1.5)
                for x, m in med:
                    ax.annotate(f"{m:.0f}%", (x, m), textcoords="offset points", xytext=(8, -3), fontsize=8, color=INK)
            ax.set_xticks(range(len(names)), names, fontsize=8)
            ax.set_xlim(-0.4, len(names) - 0.4)
            ax.set_ylim(0, 100)
            if i == 0:
                ax.set_title(tl, fontsize=10, color=INK, loc="left")
            if j == 0:
                ax.set_ylabel(f"world {w}\ncommonest people, % of all people", fontsize=8, color=INK2)
    fig.suptitle("The commonest people's share, per stage (dots: one try per seed; line: median)", fontsize=11, color=INK, x=0.01,
                 ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _colours(peoples):
    """A fixed hue per people (PEOPLE_ORDER's first eight), whatever the panel; the rest grey."""
    fixed = {p: PAL[i] for i, p in enumerate(PEOPLE_ORDER[:8])}
    return {p: fixed.get(p, OTHER) for p in peoples}


def chart_top6(stages, path):
    """Per tree x world, a stacked bar per stage: the median share of the six largest peoples (by their median over the stages), the
    rest as 'others'."""
    names = list(stages)
    fig, axs = plt.subplots(2, 4, figsize=(14, 6.5), sharey=True, facecolor=SURF)
    used = set()
    for j, (t, tl) in enumerate(TREES):
        for i, w in enumerate(WORLDS):
            ax = axs[i, j]
            style(ax)
            per = {n: [r["shares"] for r in stages[n] if r["tree"] == t and r["world"] == w] for n in names}
            allp = sorted({p for n in names for s in per[n] for p in s})
            if not allp:
                continue
            med = {n: {p: 100 * float(np.median([s.get(p, 0.0) for s in per[n]])) if per[n] else 0.0 for p in allp} for n in names}
            top = sorted(allp, key=lambda p: -max(med[n][p] for n in names))[:6]
            top = sorted(top, key=lambda p: PEOPLE_ORDER.index(p) if p in PEOPLE_ORDER else 99)
            col = _colours(top)
            for x, n in enumerate(names):
                b = 0.0
                for p in top:
                    v = med[n][p]
                    ax.bar(x, v, bottom=b, color=col[p], width=0.62, edgecolor=SURF, lw=1.5)
                    if v >= 6:
                        ax.text(x, b + v / 2, f"{p.replace('_', ' ')} {v:.0f}", ha="center", va="center", fontsize=6.5,
                                color="white" if col[p] not in (PAL[3], PAL[4], OTHER) else INK)
                    b += v
                    used.add(p)
                rest = max(0.0, 100 - b)
                ax.bar(x, rest, bottom=b, color="#ecebe7", width=0.62, edgecolor=SURF, lw=1.5)
            ax.set_xticks(range(len(names)), names, fontsize=8)
            ax.set_ylim(0, 100)
            if i == 0:
                ax.set_title(tl, fontsize=10, color=INK, loc="left")
            if j == 0:
                ax.set_ylabel(f"world {w}\nmedian share, %", fontsize=8, color=INK2)
    col = {p: c for p, c in _colours(sorted(used, key=lambda p: PEOPLE_ORDER.index(p) if p in PEOPLE_ORDER else 99)).items() if c != OTHER}
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [*col.values(), OTHER, "#ecebe7"]]
    fig.legend(handles, [p.replace("_", " ") for p in col] + ["another people of the six (named on its bar)", "all other peoples"],
               loc="lower center", ncol=10, fontsize=8, frameon=False)
    fig.suptitle("The six largest peoples per tree and world (median share over the seeds), per stage", fontsize=11, color=INK, x=0.01,
                 ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=130)
    plt.close(fig)


def chart_sweep(sweep, path, dial, fixed, label):
    """The commonest people's share (and the kobolds' and goblins' where the tree has them) against one dial, the other at `fixed`."""
    pts = {}
    for n, runs in sweep.items():
        d = dict(kv.split("=") for kv in n.split())
        if float(d[[k for k in d if k != dial][0]]) != fixed:
            continue
        pts[float(d[dial])] = runs
    xs = sorted(pts)
    fig, axs = plt.subplots(2, 4, figsize=(13, 6), sharey="row", facecolor=SURF)
    for j, (t, tl) in enumerate(TREES):
        for i, w in enumerate(WORLDS):
            ax = axs[i, j]
            style(ax)
            # (the peoples keep their colours from the other charts; the commonest people is the ink line, dashed)
            for p, c, nm in (("__top", INK, "commonest people (any)"), ("human", PAL[0], "humans"), ("kobold", PAL[4], "kobolds"),
                             ("goblin", "#7a7974", "goblins")):
                ys = []
                for x in xs:
                    rs = [r for r in pts[x] if r["tree"] == t and r["world"] == w and r["seed"] in (7, 10)]  # (the sweep's seeds; x1 is the suite)
                    if not rs or (p != "__top" and p not in rs[0]["shares"]):
                        continue
                    v = [100 * (max(r["shares"].values()) if p == "__top" else r["shares"].get(p, 0.0)) for r in rs]
                    ys.append((x, float(np.median(v))))
                if ys:
                    ax.plot(*zip(*ys), color=c, lw=2, marker="o", ms=5, mec=SURF, mew=1.2, label=nm, ls="--" if p == "__top" else "-")
            ax.set_xticks(xs, [f"x{x:g}" for x in xs], fontsize=8)
            ax.set_ylim(0, 100)
            if i == 0:
                ax.set_title(tl, fontsize=10, color=INK, loc="left")
            if j == 0:
                ax.set_ylabel(f"world {w}\nmedian share, %", fontsize=8, color=INK2)
    h, lab = [], []
    for ax in axs.flat:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in lab:
                h.append(hh)
                lab.append(ll)
    fig.legend(h, lab, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.suptitle(label, fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main(cfg_path):
    cfg = json.loads(Path(cfg_path).read_text())
    stages = {n: load(d) for n, d in cfg["stages"].items()}
    data = {"stages": stages}
    chart_stages(stages, HERE / "commonest-by-stage.png")
    chart_top6(stages, HERE / "top6-by-stage.png")
    if cfg.get("sweep"):
        sweep = {n: load(d) for n, d in cfg["sweep"].items()}
        data["sweep"] = sweep
        chart_sweep(sweep, HERE / "sweep-raiders.png", "raiders", 1.0,
                    "Shares against the raiders' dial (war at x1): median over the seeds, after D27 + D25")
        chart_sweep(sweep, HERE / "sweep-war.png", "war", 1.0,
                    "Shares against the war-torn-land dial (raiders at x1): median over the seeds, after D27 + D25")
    (HERE / "data.json").write_text(json.dumps(data, indent=0))


if __name__ == "__main__":
    main(sys.argv[1])
