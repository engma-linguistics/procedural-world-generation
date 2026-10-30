"""charts.py NUMBERS.json R2_DIR OUTDIR: the dragon-density page's charts, each drawn twice (NAME-light.png, NAME-dark.png) in the
page's own ink colours, so text keeps its contrast in both themes. Data: dragon_numbers.py's output and the round-2 sweep's per-cell
save of world 2a7385 roll 7000 (R2_DIR/on/cells/2a7385_7000.npz) for the map and boxes.

Run: PYTHONPATH=. uv run --with matplotlib python docs/review/megafauna/dragon-density/charts.py \\
       docs/review/megafauna/dragon-density/numbers.json R2_DIR docs/review/megafauna/dragon-density/charts
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap, LogNorm  # noqa: E402

from planet.geo import R_KM  # noqa: E402
from planet.grid import build_grid  # noqa: E402

N = json.loads(Path(sys.argv[1]).read_text())
R2 = Path(sys.argv[2])
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {  # page tokens (index.html): ink-2 for text, muted for ticks, rule for grids; validated categorical slots per mode
    "light": {"ink": "#2e3934", "muted": "#4f5b56", "grid": "#c9d2cc", "surface": "#eef1ec",
              "cat": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"], "pale": "#9ec5f4"},
    "dark": {"ink": "#dfe7e2", "muted": "#b4c1bb", "grid": "#34413c", "surface": "#141a18",
             "cat": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"], "pale": "#1c5cab"},
}
ROWS = ("none", "others", "foragers", "herders", "farmers")
LABEL = {"none": "Nobody's country", "others": "Others' country", "foragers": "Foragers' country", "herders": "Herders' country",
         "farmers": "Farmers' country", "all": "All land"}
ERAS = (("25", "25,000 years ago"), ("10", "10,000 years ago"), ("0", "the present"))


def theme(t):
    T = THEMES[t]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "text.color": T["ink"], "axes.labelcolor": T["ink"],
                         "xtick.color": T["muted"], "ytick.color": T["ink"], "axes.edgecolor": T["muted"], "axes.facecolor": "none",
                         "figure.facecolor": "none", "savefig.transparent": True, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "axes.titlecolor": T["ink"]})
    return T


def save(fig, name, t):
    fig.savefig(OUT / f"{name}-{t}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# 1. dragons per 1,000 km2 by who holds the land, pressure on and off (24 paired runs each): dots, with each run's value as a tick -
def density(t):
    T = theme(t)
    on_c, off_c = T["cat"][0], T["cat"][1]
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.9), sharey=True)
    for ax, (e, title) in zip(axs, ERAS):
        y = np.arange(len(ROWS))[::-1].astype(float)
        for arm, col, dy, lab in (("off", off_c, 0.17, "pressure off (no persecution, no overkill)"), ("on", on_c, -0.17, "the model (pressure on)")):
            E = N[arm]["eras"][e]
            for yy, c in zip(y, ROWS):
                runs = [v for v in E[c]["per_1000km2_runs"] if v > 0]
                ax.plot(runs, [yy + dy] * len(runs), "|", color=col, ms=7, alpha=0.55, mew=1.2)
                v = E[c]["per_1000km2"]
                ax.plot([v], [yy + dy], "o", ms=8.5, color=col, mec=T["surface"], mew=2, label=lab if (c == ROWS[0] and ax is axs[0]) else None, zorder=3)
                ax.text(v, yy + dy + (0.2 if dy > 0 else -0.2), f"{v:.2g}", ha="center", va="bottom" if dy > 0 else "top", fontsize=8, color=T["ink"])
        ax.set_xscale("log")
        ax.set_xlim(3e-5, 200)
        ax.set_title(title, fontsize=11)
        ax.grid(axis="x", color=T["grid"], lw=0.8)
        ax.set_yticks(y, [LABEL[c] for c in ROWS])
        ax.tick_params(axis="y", length=0)
        ax.set_ylim(-0.75, len(ROWS) - 0.3)
    axs[1].set_xlabel("dragons per 1,000 km² (log scale): dot = 24 runs pooled, ticks = each run")
    fig.legend(loc="lower center", bbox_to_anchor=(0.55, -0.1), ncol=2)
    save(fig, "density", t)


# 2. who takes the year's supply, by country, 25 kyr and now (24 runs, the model) ------------------------------------------------
def shares(t):
    T = theme(t)
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    labels, data = [], []
    for e, tt in (("25", "25 kyr ago"), ("0", "now")):
        for c in ROWS:
            s = N["on"]["eras"][e][c]["shares"]
            labels.append(f"{LABEL[c]}, {tt}")
            data.append((s["peoples"], s["giants"], s["guild"], s["dragons_need"], max(0.0, s["food"] - s["dragons_need"])))
    data = np.array(data)
    y = np.arange(len(labels))[::-1].astype(float)
    y[:len(ROWS)] += 0.6
    parts = (("peoples' hunters", T["cat"][1], None), ("giants", T["cat"][4], None), ("smaller predators", T["cat"][3], None),
             ("dragons (eaten)", T["cat"][0], None), ("dragons' share left uneaten", T["pale"], "////"))
    left = np.zeros(len(labels))
    for k, (nm, col, hatch) in enumerate(parts):
        ax.barh(y, data[:, k] * 100, left=left, height=0.72, color=col, label=nm, hatch=hatch, edgecolor=T["surface"], lw=1)
        left += data[:, k] * 100
    for yy, d in zip(y, data):
        ax.text(101, yy, f"dragons' share {100 * (d[3] + d[4]):.1f}%, eaten {100 * d[3]:.2g}%", va="center", fontsize=8.5)
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 100)
    ax.set_xlabel("share of the year's supply of prey (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=5, fontsize=9, handlelength=1.2)
    ax.grid(axis="x", color=T["grid"], lw=0.8)
    save(fig, "shares", t)


# 3. density against prey, with the literature lines at the ecological mass; points: 24 runs pooled, binned by prey -------------
def prey(t):
    T = theme(t)
    C, L = N["chain"], N["literature"]
    p = np.logspace(-1.3, 1.2, 60)
    fig, ax = plt.subplots(figsize=(8, 5.8))
    hl = []
    mh = L["marshall_per_km2"]
    hl.append(ax.fill_between(p, mh["lo"] * 1000, mh["hi"] * 1000, color=T["muted"], alpha=0.10, lw=0, label="Marshall et al. 2021: 95% range"))
    hl.append(ax.axhline(mh["mid"] * 1000, color=T["muted"], ls="-", lw=1.0, label="Marshall et al. 2021: dinosaur mesotherm, 1 per 47 km²"))
    hl.append(ax.fill_between(p, L["farlow_ratio_per_km2_per_t_200"] * p * 1000, L["farlow_ratio_per_km2_per_t_100"] * p * 1000, color=T["muted"],
                              alpha=0.22, lw=0, label="Farlow 1993: prey 100 to 200 × predator biomass"))
    hl += ax.plot(p, L["carbone_per_km2_per_t"] * p * 1000, color=T["muted"], ls="--", lw=1.5, label="Carbone & Gittleman 2002: carnivores per prey")
    hl.append(ax.axhline(1000 / L["jetz_carn_km2_each"], color=T["muted"], ls=":", lw=1.6, label="Jetz et al. 2004: mammal carnivores, 1 per 202 km²"))
    hl.append(ax.axhline(1000 * L["farlow_reptile_per_km2"], color=T["muted"], ls="-.", lw=1.3, label="Farlow 1993: reptiles, 1 per 27 km²"))
    hl += ax.plot(p, C["per_km2_per_t"] * p * 1000, color=T["cat"][0], lw=2.4, label="the model where nobody else eats (1 per 159 km² at 1 t/km²)")
    b = N["cells"]["on"]["0"]["binned"]
    hp = []
    hp += ax.plot([r["prey"] for r in b["none"]], [1000 * r["per_km2"] for r in b["none"]], "o", ms=8.5, color=T["cat"][0], mec=T["surface"], mew=2,
                  label="nobody's country, all cells")
    hp += ax.plot([r["prey"] for r in b["none"] if r["per_km2_occupied"]], [1000 * r["per_km2_occupied"] for r in b["none"] if r["per_km2_occupied"]], "s",
                  ms=8, mfc="none", mec=T["cat"][0], mew=1.8, label="nobody's country, cells a dragon kind holds")
    hp += ax.plot([r["prey"] for r in b["peopled"]], [1000 * r["food_fed_per_km2"] for r in b["peopled"]], "o", ms=8.5, mfc="none", mec=T["cat"][1], mew=1.8,
                  label="peopled country: the food-fed density")
    hp += ax.plot([r["prey"] for r in b["peopled"]], [1000 * r["per_km2"] for r in b["peopled"]], "o", ms=8.5, color=T["cat"][1], mec=T["surface"], mew=2,
                  label="peopled country: dragons there")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.05, 15)
    ax.set_ylim(3e-4, 400)
    ax.set_xlabel("prey biomass, wild herds plus livestock (t/km², log)")
    ax.set_ylabel("dragons per 1,000 km² (log)")
    ax.grid(color=T["grid"], lw=0.7)
    ax.legend(handles=hp, loc="lower right", fontsize=8.3, title="points: 24 runs pooled, now, binned by prey", title_fontsize=8.3)
    fig.legend(handles=hl, loc="upper left", bbox_to_anchor=(0.08, 0.01), fontsize=8.3, ncol=1,
               title="lines, at a dragon's ecological mass of 1.65 t", title_fontsize=8.3)
    save(fig, "prey", t)


# 4. dragons over the last 300,000 years on one world, three arms ----------------------------------------------------------------
def time_(t):
    T = theme(t)
    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    for key, col, lab in (("no_pressure", T["cat"][1], "pressure off"), ("no_persecution", T["cat"][2], "persecution off, overkill on"),
                          ("with_pressure", T["cat"][0], "the model (pressure on)")):
        s = N["series"].get(key)
        if not s:
            continue
        ts = sorted((float(tt), v["dragons"]) for tt, v in s.items() if float(tt) <= 400.0)
        ax.plot([max(tt, 0.0) for tt, _ in ts], [v for _, v in ts], color=col, lw=2, label=lab, drawstyle="steps-post")
    for x, txt in ((30, "30 kyr: glacial pass\nhands over to recent pass"), (300, "300 kyr: the deep\nepoch's flat rule ends")):
        ax.axvline(x, color=T["muted"], lw=0.8, ls="--")
        ax.text(x * (0.93 if x == 300 else 1.04), 2.6e6, txt, fontsize=8, va="top", ha="right" if x == 300 else "left")
    ax.set_xscale("symlog", linthresh=30)
    ax.set_xlim(400, 0)
    ax.set_xticks([400, 300, 200, 100, 30, 20, 10, 0], ["400", "300", "200", "100", "30", "20", "10", "now"])
    ax.set_yscale("log")
    ax.set_ylim(5e3, 3e6)
    ax.set_xlabel("thousands of years ago (linear from 30 kyr to now, logarithmic beyond)")
    ax.set_ylabel("dragons on the planet")
    ax.grid(color=T["grid"], lw=0.7)
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "time", t)


# 5. the sensitivity tornado: factor on the headline density, one constant at a time --------------------------------------------
def tornado(t):
    T = theme(t)
    S = N["sensitivity"]
    groups = {}
    for r in S["rows"]:
        groups.setdefault(r["group"], []).append(r)
    order = ["Intake: field metabolic rate law", "Prey: above-ground share of the NPP fed to the fit", "Yearly offtake", "Guild weighting exponent",
             "Share of a large carcass eaten", "Assimilation"]
    names = {"Intake: field metabolic rate law": "Intake law (mammal/bird ... varanid)", "Prey: above-ground share of the NPP fed to the fit":
             "Above-ground share of NPP (0.4 to 1; unsourced)", "Yearly offtake": "Offtake (5% to 26% a year)",
             "Guild weighting exponent": "Guild exponent b (0.6 to 0.889)", "Share of a large carcass eaten": "Carcass eaten (65% to 100%)",
             "Assimilation": "Assimilation (66% to 85%)"}
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    for i, gname in enumerate(order):
        rs = [r for r in groups[gname] if not r["label"].startswith("The model's law")]
        lo, hi = min(min(r["factor"] for r in rs), 1.0), max(max(r["factor"] for r in rs), 1.0)
        y = len(order) - 1 - i
        ax.barh(y, math.log10(hi), left=0, color=T["cat"][0], height=0.6)
        ax.barh(y, math.log10(lo), left=0, color=T["cat"][1], height=0.6)
        ax.text(math.log10(hi) + 0.02, y, f"×{hi:.2g}", va="center", fontsize=8.5)
        ax.text(math.log10(lo) - 0.02, y, f"×{lo:.2g}", va="center", ha="right", fontsize=8.5)
    ax.axvline(0, color=T["ink"], lw=1)
    ticks = [0.25, 0.5, 1, 2, 4]
    ax.set_xticks([math.log10(x) for x in ticks], [f"×{x:g}" for x in ticks])
    ax.set_xlim(-0.85, 0.65)
    ax.set_yticks(range(len(order))[::-1], [names[g] for g in order])
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=T["grid"], lw=0.7)
    ax.set_xlabel("factor on dragons per km² (log scale; 1 = the model's 1 per 159 km² at 1 t/km²)")
    save(fig, "tornado", t)


# 6. maps: who lives where (five classes) and dragon density, now, on world 2a7385 roll 7000; four Sword Coast-sized boxes ----------
g = build_grid(7)
Z = np.load(R2 / "on" / "cells" / "2a7385_7000.npz")
e = "0"
land = Z[f"land_{e}"]
pp = {c: Z[f"people_{c}_{e}"].astype(float) for c in ("foragers", "herders", "farmers", "others")}
allp = sum(pp.values())
cls = np.full(g.n, -1)
cls[land] = 0
cls[land & (allp >= 0.02)] = 1  # others' unless a named way of life leads (round 1 drew these as nobody's: peer S2)
for k, c in ((2, "foragers"), (3, "herders"), (4, "farmers")):
    cls[land & (allp >= 0.02) & np.all([pp[c] >= pp[o] for o in pp if o != c], axis=0)] = k
dens = Z[f"dragons_{e}"].astype(float) * 1000.0
px, ny = 1000, 500
LO, LA = np.meshgrid(np.linspace(-180, 180, px), np.linspace(90, -90, ny))
la, lo = np.radians(LA.ravel()), np.radians(LO.ravel())
cpx = g.locate(np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1))
v = g.centers
lat_c = np.degrees(np.arcsin(v[:, 2]))
lon_c = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
ns, ew = N["sword_coast"]["ns_km"], N["sword_coast"]["ew_km"]
food_t = N["chain"]["food_t_yr"]


def box_geom(la0, lo0):
    dla = ns / (math.pi * R_KM / 180.0)
    dlo = ew / (math.pi * R_KM / 180.0 * math.cos(math.radians(la0)))
    km2 = R_KM ** 2 * math.radians(dlo) * (math.sin(math.radians(la0 + dla / 2)) - math.sin(math.radians(la0 - dla / 2)))
    sel = (abs(lat_c - la0) <= dla / 2) & (abs(((lon_c - lo0 + 180) % 360) - 180) <= dlo / 2)
    return dla, dlo, km2, sel


best = {}
KINDS = ("none", "foragers", "herders", "farmers")
for la0 in range(-60, 61, 3):
    for lo0 in range(-180, 180, 3):
        _, _, _, s_ = box_geom(la0, lo0)
        if s_.sum() == 0 or land[s_].mean() < 0.7:
            continue
        cl = cls[s_ & land]
        for kn in KINDS:
            sh = float((cl == ROWS.index(kn)).mean())
            if sh > best.get(kn, (0, None))[0]:
                best[kn] = (sh, (la0, lo0))
boxinfo = []
for kn in KINDS:
    if kn not in best:
        continue
    la0, lo0 = best[kn][1]
    dla, dlo, km2, s_ = box_geom(la0, lo0)
    sl = s_ & land
    lf = float(land[s_].mean())
    boxinfo.append({"kind": kn, "lat": la0, "lon": lo0, "dlat": dla, "dlon": dlo, "box_km2": km2, "land_fraction": lf, "land_km2": lf * km2,
                    "dragons_per_1000km2": 1000 * float(Z[f"dragons_{e}"][sl].mean()), "dragons": float(Z[f"dragons_{e}"][sl].mean()) * lf * km2,
                    "prey_t_km2": float(Z[f"prey_{e}"][sl].mean()), "press_mean": float(Z[f"press_{e}"][sl].mean()),
                    "share_by_class": {c: float((cls[sl] == i).mean()) for i, c in enumerate(ROWS)},
                    "occupied_share": float((Z[f"dragon_present_{e}"][sl] > 0).mean()),
                    "food_fed": float((Z[f"food_{e}"][sl] / food_t).mean()) * lf * km2})
(OUT / "boxes.json").write_text(json.dumps(boxinfo, indent=1))


def maps(t):
    T = theme(t)
    fig, axs = plt.subplots(2, 1, figsize=(9, 10.2), gridspec_kw={"hspace": 0.32})
    img = np.zeros((ny * px, 4))
    cols = T["cat"]
    for i, col in enumerate(cols):
        rgb = matplotlib.colors.to_rgb(col)
        img[cls[cpx] == i] = (*rgb, 0.45 if i == 0 else 0.95)
    axs[0].imshow(img.reshape(ny, px, 4), extent=(-180, 180, -90, 90), interpolation="nearest")
    for i, c in enumerate(ROWS):
        axs[0].plot([], [], "s", ms=10, color=cols[i], alpha=0.45 if i == 0 else 0.95, label=LABEL[c])
    axs[0].legend(loc="upper center", fontsize=8.5, ncol=5, bbox_to_anchor=(0.5, -0.07))
    axs[0].set_title("Who holds the land, now", fontsize=11)
    img = np.zeros((ny * px, 4))
    dv = dens[cpx]
    norm = LogNorm(0.01, 30)
    cm = ListedColormap(plt.get_cmap("YlGn")(np.linspace(0.25, 1.0, 256)) if t == "light" else plt.get_cmap("viridis")(np.linspace(0.15, 1.0, 256)))
    sel = land[cpx] & (dv >= 0.01)
    img[land[cpx]] = (*matplotlib.colors.to_rgb(T["muted"]), 0.3)
    img[sel] = cm(norm(np.clip(dv[sel], 0.01, 30)))
    axs[1].imshow(img.reshape(ny, px, 4), extent=(-180, 180, -90, 90), interpolation="nearest")
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cm)
    cb = fig.colorbar(sm, cax=axs[1].inset_axes([0.15, -0.16, 0.7, 0.035]), orientation="horizontal")
    cb.set_label("dragons per 1,000 km², every kind (grey land: fewer than 0.01)")
    cb.outline.set_visible(False)
    axs[1].set_title("Dragons, now", fontsize=11)
    for ax in axs:
        ax.set_xticks(range(-180, 181, 60), [f"{abs(x)}°{'W' if x < 0 else 'E' if x > 0 else ''}" for x in range(-180, 181, 60)], fontsize=8)
        ax.set_yticks(range(-60, 61, 30), [f"{abs(y)}°{'S' if y < 0 else 'N' if y > 0 else ''}" for y in range(-60, 61, 30)], fontsize=8)
        ax.grid(color=T["grid"], lw=0.5)
        for sp in ax.spines.values():
            sp.set_visible(False)
        for k, bi in enumerate(boxinfo):
            ax.add_patch(plt.Rectangle((bi["lon"] - bi["dlon"] / 2, bi["lat"] - bi["dlat"] / 2), bi["dlon"], bi["dlat"], fill=False, ec=T["ink"], lw=1.6))
            ax.text(bi["lon"], bi["lat"] + bi["dlat"] / 2 + 1.5, chr(65 + k), ha="center", va="bottom", fontsize=10, fontweight="bold")
    save(fig, "map", t)


for t in THEMES:
    density(t)
    shares(t)
    prey(t)
    time_(t)
    tornado(t)
    maps(t)
print(json.dumps(boxinfo, indent=1))
