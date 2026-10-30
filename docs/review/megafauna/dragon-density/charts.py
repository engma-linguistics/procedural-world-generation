"""charts.py NUMBERS.json ERAS.npz OUTDIR: the dragon-density page's charts (transparent PNGs in mid-tone colours, so they read on the
page's light and dark themes) from dragon_numbers.py's output and the 45b sweep's per-cell save (world 2a7385, roll 7000).

Run: PYTHONPATH=. uv run --with matplotlib python docs/review/megafauna/dragon-density/charts.py \\
       docs/review/megafauna/dragon-density/numbers.json L45B_DIR/save2/run/ERAS.npz docs/review/megafauna/dragon-density/charts
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm, ListedColormap  # noqa: E402

from planet.grid import build_grid  # noqa: E402

N = json.loads(Path(sys.argv[1]).read_text())
Z = np.load(sys.argv[2])
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

INK = "#7f8783"  # mid grey: legible on both the light and the dark page
GRID = (0.5, 0.53, 0.51, 0.25)
DRAGON, DRAGON_PALE = "#2f8a66", "#93c9b1"
PEOPLE, GIANT, GUILD = "#c0543a", "#7b6cc0", "#b07a16"
COUNTRY = {"none": ("nobody", "#2f8a66"), "foragers": ("foragers", "#b07a16"), "herders": ("herders", "#7b6cc0"), "farmers": ("farmers", "#c0543a")}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.edgecolor": INK, "axes.facecolor": "none", "figure.facecolor": "none",
                     "savefig.transparent": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
ERAS = (("25", "25,000 years ago"), ("10", "10,000 years ago"), ("0", "the present"))
LABEL = {"none": "Nobody's country", "foragers": "Foragers' country", "herders": "Herders' country", "farmers": "Farmers' country"}


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


# 1. dragons per 1,000 km2 by who lives there: with the peoples' pressure (24 runs) and with it off (6 runs) ------------------
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.6), sharey=True)
rows = ("none", "foragers", "herders", "farmers")
for ax, (e, title) in zip(axs, ERAS):
    y = np.arange(len(rows))[::-1]
    w = [N["sweep"]["eras"][e][c]["per_1000km2"] for c in rows]
    o = [N["nopress"]["eras"][e][c]["per_1000km2"] for c in rows]
    ax.barh(y + 0.19, o, height=0.36, color=DRAGON_PALE, label="food alone (pressure off)")
    ax.barh(y - 0.19, w, height=0.36, color=DRAGON, label="with the peoples' pressure")
    for yy, a, b in zip(y, w, o):
        ax.text(b * 1.15, yy + 0.19, f"{b:.2g}" if b < 1 else f"{b:.1f}", va="center", fontsize=9)
        ax.text(a * 1.15, yy - 0.19, f"{a:.2g}" if a < 1 else f"{a:.1f}", va="center", fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.004, 60)
    ax.set_title(title, color=INK, fontsize=11)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_yticks(y, [LABEL[c] for c in rows])
    ax.tick_params(axis="y", length=0)
axs[1].set_xlabel("dragons per 1,000 km² (log scale)")
axs[0].legend(loc="upper center", bbox_to_anchor=(1.65, -0.2), ncol=2)
save(fig, "density.png")

# 2. who eats the year's supply (wild offtake + herders' tolerable stock loss), by country, 25 kyr and present -----------------
fig, ax = plt.subplots(figsize=(10, 3.9))
labels, data = [], []
for e, t in (("25", "25 kyr"), ("0", "now")):
    for c in rows:
        s = N["sweep"]["eras"][e][c]["shares"]
        labels.append(f"{LABEL[c]}, {t}")
        data.append((s["peoples"], s["giants"], s["guild"], s["dragons_need"], s["food"] - s["dragons_need"]))
data = np.array(data)
y = np.arange(len(labels))[::-1].astype(float)
y[:4] += 0.5
parts = (("peoples' hunters", PEOPLE, None), ("giants", GIANT, None), ("smaller predators", GUILD, None),
         ("dragons (eaten)", DRAGON, None), ("dragons' share left uneaten", DRAGON_PALE, "////"))
left = np.zeros(len(labels))
for k, (nm, col, hatch) in enumerate(parts):
    ax.barh(y, data[:, k] * 100, left=left, height=0.72, color=col, label=nm, hatch=hatch, edgecolor="none" if hatch is None else DRAGON, lw=0)
    left += data[:, k] * 100
for yy, d in zip(y, data):
    ax.text(101, yy, f"dragons' share {100 * (d[3] + d[4]):.1f}%, eaten {100 * d[3]:.2g}%", va="center", fontsize=8.5)
ax.set_yticks(y, labels)
ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 100)
ax.set_xlabel("share of the year's supply of prey (%)")
ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.18), ncol=5, fontsize=9, handlelength=1.2)
ax.grid(axis="x", color=GRID, lw=0.8)
save(fig, "shares.png")

# 3. density against prey biomass, with the literature lines at the dragons' ecological mass -------------------------------------
C, L = N["chain"], N["literature"]
p = np.logspace(-1, 1.1, 50)
fig, ax = plt.subplots(figsize=(7.6, 5.4))
hl = []
hl.append(ax.fill_between(p, L["farlow_ratio_per_km2_per_t_200"] * p * 1000, L["farlow_ratio_per_km2_per_t_100"] * p * 1000, color=INK, alpha=0.16, lw=0,
                          label="Farlow 1993: prey 100 to 200 times the predators' biomass"))
hl += ax.plot(p, L["carbone_per_km2_per_t"] * p * 1000, color=INK, ls="--", lw=1.5, label="Carbone & Gittleman 2002: carnivores per prey biomass")
hl.append(ax.axhline(1000 / L["jetz_carn_km2_each"], color=INK, ls=":", lw=1.6, label="Jetz et al. 2004: mammal carnivores, 1 per 202 km²"))
hl.append(ax.axhline(1000 * L["farlow_reptile_per_km2"], color=INK, ls="-.", lw=1.3, label="Farlow 1993: reptiles, 1 per 27 km²"))
hl += ax.plot(p, C["per_km2_per_t"] * p * 1000, color=DRAGON, lw=2.4, label="the model where nobody else eats (1 per 159 km² at 1 t/km²)")
b = N["cells_2a7385"]["0"]["binned"]
hp = []
hp += ax.plot([r["prey"] for r in b["none"]], [1000 * r["per_km2"] for r in b["none"]], "o", ms=8, color=DRAGON, mec="white", mew=1.2,
              label="nobody's country: dragons there")
hp += ax.plot([r["prey"] for r in b["peopled"]], [1000 * r["food_allows_per_km2"] for r in b["peopled"]], "o", ms=8, mfc="none", mec=PEOPLE, mew=1.8,
              label="peopled country: what the food left would feed")
hp += ax.plot([r["prey"] for r in b["peopled"]], [1000 * r["per_km2"] for r in b["peopled"]], "o", ms=8, color=PEOPLE, mec="white", mew=1.2,
              label="peopled country: dragons there, with pressure")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.1, 12)
ax.set_ylim(0.001, 100)
ax.set_xlabel("prey biomass, wild herds plus livestock (t/km², log)")
ax.set_ylabel("dragons per 1,000 km² (log)")
ax.grid(color=GRID, lw=0.7)
ax.legend(handles=hp, loc="lower right", fontsize=8.5, title="points: one run (2a7385), now, binned by prey", title_fontsize=8.5)
fig.legend(handles=hl, loc="upper left", bbox_to_anchor=(0.08, 0.02), fontsize=8.5, title="lines, at a dragon's ecological mass of 1.65 t", title_fontsize=8.5)
save(fig, "prey.png")

# 4. dragons over the last 300,000 years on one world (2a7385, roll 7000) -------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.4, 3.5))
for key, col, lab in (("no_pressure", DRAGON_PALE, "food alone (pressure off)"), ("with_pressure", DRAGON, "with the peoples' pressure")):
    s = N["series"][key]
    ts = sorted((float(t), v["dragons"]) for t, v in s.items() if float(t) <= 296.0)
    ax.plot([max(t, 0.0) for t, _ in ts], [v for _, v in ts], color=col, lw=2, label=lab, drawstyle="steps-post")
ax.axvline(30, color=INK, lw=0.8, ls="--")
ax.text(31, 2.2e6, "the run's finer\nlast-30,000-year pass", fontsize=8.5, va="top")
ax.set_xscale("symlog", linthresh=30)
ax.set_xlim(296, 0)
ax.set_xticks([296, 200, 100, 30, 20, 10, 0], ["296", "200", "100", "30", "20", "10", "now"])
ax.set_yscale("log")
ax.set_ylim(8e3, 3e6)
ax.set_xlabel("thousands of years ago")
ax.set_ylabel("dragons on the planet")
ax.grid(color=GRID, lw=0.7)
ax.legend(loc="center left", bbox_to_anchor=(0.25, 0.53), fontsize=9)
save(fig, "time.png")

# 5. maps: who lives where, and dragon density, at the present (2a7385 roll 7000) -----------------------------------------------
g = build_grid(7)
e = "0"
land = Z[f"land_{e}"]
pp = {c: Z[f"people_{c}_{e}"] for c in ("foragers", "herders", "farmers", "others")}
allp = sum(pp.values())
cls = np.full(g.n, -1)
cls[land] = 0
for k, c in enumerate(("foragers", "herders", "farmers"), 1):
    m = land & (allp >= 0.02) & np.all([pp[c] >= pp[o] for o in pp if o != c], axis=0)
    cls[m] = k
dens = Z[f"dragons_{e}"] * 1000.0
px = 1000
ny = px // 2
LO, LA = np.meshgrid(np.linspace(-180, 180, px), np.linspace(90, -90, ny))
la, lo = np.radians(LA.ravel()), np.radians(LO.ravel())
c = g.locate(np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1))
SEA = (0, 0, 0, 0)  # the sea: the page shows through
LANDGREY = (0.5, 0.53, 0.51, 0.3)


def base(ax):
    img = np.zeros((ny * px, 4))
    img[~land[c]] = SEA
    return img


# a Sword Coast-sized box (2,414 x 1,609 km), placed on this world's land; its dragons counted from the per-cell field
area = N["cell_km2"]
ns, ew = N["sword_coast"]["ns_km"], N["sword_coast"]["ew_km"]
v = g.centers
lat_c = np.degrees(np.arcsin(v[:, 2]))
lon_c = np.degrees(np.arctan2(v[:, 1], v[:, 0]))


def box_cells(la0, lo0):
    dla = ns / (math.pi * 6371.0 / 180.0)
    dlo = ew / (math.pi * 6371.0 / 180.0 * math.cos(math.radians(la0)))
    return (abs(lat_c - la0) <= dla / 2) & (abs(((lon_c - lo0 + 180) % 360) - 180) <= dlo / 2)


# place one box per kind of country: on a 3-degree grid of centres (|lat| <= 60), the box at least 70% land whose land is most of
# that kind (nobody's, foragers', herders', farmers')
best = {}
for la0 in range(-60, 61, 3):
    for lo0 in range(-180, 180, 3):
        s_ = box_cells(la0, lo0)
        n_ = s_.sum()
        if n_ == 0 or land[s_].mean() < 0.7:
            continue
        cl = cls[s_ & land]
        for i, k in enumerate(("none", "foragers", "herders", "farmers")):
            sh = float((cl == i).mean())
            if sh > best.get(k, (0, None))[0]:
                best[k] = (sh, (la0, lo0))
BOXES = [best[k][1] for k in ("none", "foragers", "herders", "farmers") if k in best]
boxinfo = []
for la0, lo0 in BOXES:
    dla = ns / (math.pi * 6371.0 / 180.0)
    dlo = ew / (math.pi * 6371.0 / 180.0 * math.cos(math.radians(la0)))
    sl = box_cells(la0, lo0) & land
    boxinfo.append({"kind": ("none", "foragers", "herders", "farmers")[len(boxinfo)], "lat": la0, "lon": lo0, "dlat": dla, "dlon": dlo, "land_km2": float(sl.sum() * area),
                    "dragons": float(Z[f"dragons_{e}"][sl].sum() * area), "prey_t_km2": float(Z[f"prey_{e}"][sl].mean()),
                    "share_by_class": {k: float((cls[sl] == i).mean()) for i, k in enumerate(("none", "foragers", "herders", "farmers"))},
                    "food_allows": float((Z[f"food_{e}"][sl] / (N["chain"]["food_t_yr"])).sum() * area)})
(OUT / "boxes.json").write_text(json.dumps(boxinfo, indent=1))

fig, axs = plt.subplots(2, 1, figsize=(9, 9.2))
img = base(axs[0])
cols = [COUNTRY[k][1] for k in ("none", "foragers", "herders", "farmers")]
for i, col in enumerate(cols):
    rgb = matplotlib.colors.to_rgb(col)
    sel = cls[c] == i
    img[sel] = (*rgb, 0.35 if i == 0 else 0.9)
axs[0].imshow(img.reshape(ny, px, 4), extent=(-180, 180, -90, 90), interpolation="nearest")
for i, k in enumerate(("none", "foragers", "herders", "farmers")):
    axs[0].plot([], [], "s", ms=10, color=cols[i], alpha=0.35 if i == 0 else 0.9, label=LABEL[k])
axs[0].legend(loc="lower left", fontsize=8.5, ncol=4, bbox_to_anchor=(0, -0.13))
axs[0].set_title("Who lives where, now", color=INK, fontsize=11)
img = base(axs[1])
dv = dens[c]
norm = LogNorm(0.01, 30)
cm = ListedColormap(plt.get_cmap("YlGn")(np.linspace(0.25, 1.0, 256)))
sel = land[c] & (dv >= 0.01)
img[land[c]] = LANDGREY
img[sel] = cm(norm(np.clip(dv[sel], 0.01, 30)))
im = axs[1].imshow(img.reshape(ny, px, 4), extent=(-180, 180, -90, 90), interpolation="nearest")
sm = plt.cm.ScalarMappable(norm=norm, cmap=cm)
cb = fig.colorbar(sm, cax=axs[1].inset_axes([0.15, -0.1, 0.7, 0.035]), orientation="horizontal")
cb.set_label("dragons per 1,000 km² (grey land: fewer than 0.01)")
cb.outline.set_visible(False)
axs[1].set_title("Dragons, now (every kind together)", color=INK, fontsize=11)
for ax in axs:
    ax.set_xticks([]), ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for bi in boxinfo:
        ax.add_patch(plt.Rectangle((bi["lon"] - bi["dlon"] / 2, bi["lat"] - bi["dlat"] / 2), bi["dlon"], bi["dlat"], fill=False, ec=INK, lw=1.6, ls="-"))
for k, bi in enumerate(boxinfo):
    for ax in axs:
        ax.text(bi["lon"], bi["lat"] + bi["dlat"] / 2 + 1.5, chr(65 + k), ha="center", va="bottom", fontsize=10, fontweight="bold")
save(fig, "map.png")
print(json.dumps(boxinfo, indent=1))
