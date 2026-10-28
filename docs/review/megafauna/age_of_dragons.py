"""age_of_dragons.py RUN.npz SERIES.json OUTDIR: the PW-967 review (age of dragons) from one dnd history run.

RUN.npz comes from a probe that saves the present (fun lane 41's probe, REVIEW_DIR): presences, the megafauna's suitability, the
peoples' pressure, the prey field (wild after overkill, livestock) and the present summary. SERIES.json is that probe's output
(counts over time). Writes OUTDIR/age-of-dragons.html and its PNGs. Every number comes from the run or from planet.lineages
(dragon_ages, prey, history.megafauna): nothing is tuned here. The candidates are shown side by side; none is picked.

Run: uv run python docs/review/megafauna/age_of_dragons.py RUN.npz SERIES.json docs/review/megafauna
"""
import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.patches
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from planet.grid import build_grid  # noqa: E402
from planet.lineages import dragon_ages as DA  # noqa: E402
from planet.lineages import prey as PR  # noqa: E402
from planet.lineages.history import megafauna as MG  # noqa: E402

NPZ, SERIES, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FIG = OUT / "age-of-dragons"
FIG.mkdir(parents=True, exist_ok=True)
z = np.load(NPZ, allow_pickle=False)
pres = json.loads(str(z["pres"]))
series = json.loads(SERIES.read_text())
ids = [str(x) for x in z["ids"]]
mf_ids = [str(x) for x in z["mf_ids"]]
P, S = z["P"], z["S"]
g = build_grid(int(z["level"]))
lat, lon = g.lat, g.lon
land = z["land"]
AREA = 4 * np.pi * 6371.0 ** 2 / g.n  # km2 per cell
KINDS = {"red": "#d33", "blue": "#2a6fdb", "green": "#2b8a3e", "black": "#222", "white": "#9ad",
         "gold": "#d4a017", "silver": "#8a8f98", "bronze": "#b0702c", "copper": "#c8643b", "brass": "#c9b037"}
STAGE_COL = ["#cfe0f5", "#86b2e6", "#3f7dc9", "#14407e"]  # wyrmling -> ancient: one hue, light to dark (ordered)
NAT_COL, NOW_COL = "#2a78d6", "#eb6834"  # natural (the age of dragons) vs present
SCHED = list(DA.SCHEDULES)
AREAS = [("Washington DC", 180), ("a county", 2000), ("Wales", 21000), ("California", 424000), ("France", 550000)]
DKM2 = 5000.0  # meta.dragon_km2 (present, peopled country) in this run
mf = pres["megafauna"]
dragons = {k: r for k, r in mf.items() if k.removesuffix("_dragon") in KINDS}
kind = lambda lid: lid.removesuffix("_dragon")
dmask = np.zeros(g.n, bool)  # the dragons' own country: any kind's suitability >= 0.5
for lid in dragons:
    dmask |= S[mf_ids.index(lid)] >= MG.SUITABLE
prey, wild0, wild, lvs, press = z["prey"], z["wild0"], z["wild"], z["livestock"], z["press"]
prey_med = float(np.median(prey[dmask])) if dmask.any() else 1.0


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0


def raster(ax, values=None, box=None, cmap="Greens", vmax=None, px=900, mask=None):
    x0, x1, y0, y1 = box or (-180, 180, -90, 90)
    ny = max(2, int(px * (y1 - y0) / max(x1 - x0, 1e-6) * (1 if box is None else 1 / max(np.cos(np.radians(0.5 * (y0 + y1))), 0.3))))
    LO, LA = np.meshgrid(np.linspace(x0, x1, px), np.linspace(y1, y0, ny))
    la, lo = np.radians(LA.ravel()), np.radians(LO.ravel())
    c = g.locate(np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1))
    img = np.where(land[c][:, None], rgb("#e9e4d3"), rgb("#d3e2ef"))
    if values is not None:
        v = values[c]
        sel = land[c] & (v > 0) & (True if mask is None else mask[c])
        cm = plt.get_cmap(cmap)
        t = np.clip(v / (vmax or np.percentile(values[values > 0], 98)), 0, 1)
        img = np.where(sel[:, None], cm(0.15 + 0.85 * t)[:, :3], img)
    ax.imshow(img.reshape(ny, px, 3), extent=(x0, x1, y0, y1), aspect="auto" if box else "equal", interpolation="nearest")
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xlim(x0, x1), ax.set_ylim(y0, y1)


def save(fig, name):
    fig.savefig(FIG / name, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return f"age-of-dragons/{name}"


def stages_txt(n, name):
    st = np.array(DA.structure(name)["share"]) * n
    r = lambda x: f"{x:.0f}" if x >= 1 else (f"{x:.1f}" if x >= 0.1 else f"{x:.2f}")
    return f"~{r(n)}: {r(st[3])} anc, {r(st[2])} ad, {r(st[1])} yg, {r(st[0])} wy"


# ---- densities: the candidates (natural) next to the present value --------------------------------------------------------
def nat_density(name, mode, prey_t=None):
    s = DA.structure(name)
    m = s["eco_mass_kg"]
    if mode == "prey":
        return MG.CARBONE_A * m ** -MG.CARBONE_B / 10.0 * (prey_med if prey_t is None else prey_t)
    return 10 ** MG.LOG_A[mode] * (1000 * m) ** -MG.DAMUTH_EXP * s["all_ages"]


MODES = [("prey", "prey-based (Carbone & Gittleman 2002)"), ("mesotherm", "Damuth, Marshall's dinosaur line"),
         ("mammal", "Damuth, mammal carnivores")]
country_km2 = float(dmask.sum() * AREA)
dens_rows = []
for mode, label in MODES:
    for name in SCHED:
        d = nat_density(name, mode)
        cnt = float((nat_density(name, mode, prey) * dmask * AREA).sum()) if mode == "prey" else d * country_km2
        dens_rows.append((label, name, 1 / d, cnt))
now_total = sum(r["count"] for r in dragons.values())
rp = sorted(DKM2 / x[2] for x in dens_rows if x[0].startswith("prey"))[::len(SCHED) - 1]
rd = sorted(DKM2 / x[2] for x in dens_rows if x[0].startswith("Damuth"))
rd = (rd[0], rd[-1])

# fig 1: maps. natural (prey, base) density over the dragons' country, and the present pockets
fig, axs = plt.subplots(1, 2, figsize=(15, 3.9))
natd = nat_density("base", "prey", prey) * dmask
raster(axs[0], natd, cmap="Blues", vmax=np.percentile(natd[dmask], 95))
axs[0].set_title(f"The age of dragons: natural density from the prey (base schedule)\n~{dens_rows[0][3]:,.0f} dragons in their country; darker = more", fontsize=10)
raster(axs[1], press * land, cmap="Oranges", vmax=2.5)
for lid, r in dragons.items():
    ps = r["pocket_list"]
    axs[1].scatter([p["lon"] for p in ps], [p["lat"] for p in ps], s=[5 + 9 * np.sqrt(p["count"]) for p in ps], c=KINDS[kind(lid)],
                   edgecolors="k", linewidths=0.25, alpha=0.9)
axs[1].set_title(f"The present: ~{now_total:,} dragons (dots, by kind), peoples' pressure shaded\n1 per {DKM2:,.0f} km² where peoples press them", fontsize=10)
img_maps = save(fig, "maps.png")

# fig 2: prey field
fig, axs = plt.subplots(1, 2, figsize=(15, 3.9))
raster(axs[0], wild0, cmap="Greens", vmax=12)
axs[0].set_title("Wild herbivores before the peoples (t/km², from grazing NPP; 0-12 shaded)", fontsize=10)
raster(axs[1], lvs, cmap="Purples", vmax=12)
axs[1].set_title(f"Livestock now (t/km², by way of life); wild herds left: {wild[land].sum() / max(wild0[land].sum(), 1e-9):.0%} of before", fontsize=10)
img_prey = save(fig, "prey.png")

# fig 3: age schedules, stage shares (count, biomass, food)
fig, axs = plt.subplots(1, 3, figsize=(15, 3.0), sharey=True)
for ax, key, title in zip(axs, ("share", "biomass_share", "food_share"), ("share of dragons", "share of biomass", "share of food")):
    left = np.zeros(len(SCHED))
    for s_ in range(4):
        v = np.array([DA.structure(n)[key][s_] for n in SCHED])
        ax.barh(SCHED, v, left=left, color=STAGE_COL[s_], edgecolor="white", linewidth=2, label=DA.STAGES[s_])
        for i, (x, l0) in enumerate(zip(v, left)):
            if x > 0.07:
                ax.text(l0 + x / 2, i, f"{x:.0%}", ha="center", va="center", fontsize=8, color="white" if s_ >= 2 else "#222")
        left += v
    ax.set_title(title, fontsize=10)
    ax.set_xlim(0, 1), ax.set_xticks([])
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
axs[0].invert_yaxis()
axs[2].legend(ncol=4, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(-0.6, -0.02))
img_ages = save(fig, "schedules.png")

# fig 4: the age of dragons over time (the run's frames)
ts = sorted(float(t) for t in series["series"])
fig, ax = plt.subplots(figsize=(7.5, 2.6))
for k_, col in (("dragons", NAT_COL), ("giants", NOW_COL)):
    ax.plot([-t for t in ts], [series["series"][str(t) if str(t) in series["series"] else repr(t)][k_] for t in ts], color=col, lw=2, label=k_)
ax.set_yscale("log"), ax.set_xlabel("kyr before the present"), ax.legend(frameon=False, fontsize=9)
ax.set_xlim(-max(ts), 0)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.grid(axis="y", color="#ddd", lw=0.6)
ax.set_title("Counts over the history (one dnd run): the age of dragons is the left end", fontsize=10)
img_time = save(fig, "over-time.png")

# ---- familiar areas: counts by stage, present vs natural, per schedule ------------------------------------------------------
def area_rows(dens_fn):
    return [(nm, km2, [stages_txt(km2 * dens_fn(n), n) for n in SCHED]) for nm, km2 in AREAS]


present_rows = area_rows(lambda n: 1.0 / DKM2)
natprey_rows = area_rows(lambda n: nat_density(n, "prey"))
natmeso_rows = area_rows(lambda n: nat_density(n, "mesotherm"))

# ---- food against livestock, in California-sized squares of dragon country --------------------------------------------------
# expected dragons per cell: presence x the run's local density (MG.local_density with the run's prey and pressure) x area
base = DA.structure("base")
coef = MG.CARBONE_A * base["eco_mass_kg"] ** -MG.CARBONE_B / 10.0
dloc = np.maximum(coef * prey, 1e-12)
dloc = dloc * np.minimum(1.0, (1.0 / DKM2) / dloc) ** press  # (MG.local_density, as the run had it)
expd = np.zeros(g.n)
for lid in dragons:
    expd += np.where(P[ids.index(lid)] >= 0.02, P[ids.index(lid)], 0.0) * dloc * AREA
side = np.sqrt(424000.0)  # km
cand = np.flatnonzero(dmask & land)
best = []
taken = np.zeros(g.n, bool)
for _ in range(3):  # (the three busiest squares that do not overlap)
    score = []
    for c in cand[:: max(1, len(cand) // 3000)]:
        dl = side / 2 / 111.0
        dlo = dl / max(np.cos(np.radians(lat[c])), 0.2)
        sel = (np.abs(lat - lat[c]) < dl) & (np.abs(((lon - lon[c] + 180) % 360) - 180) < dlo)
        if not (sel & taken).any():
            score.append((float(expd[sel].sum()), c, sel))
    if not score:
        break
    sc, c, sel = max(score, key=lambda x: x[0])
    taken |= sel
    best.append((c, sel))
food_rows = []
for c, sel in best:
    n = float(expd[sel].sum())
    n_st = np.array(base["share"]) * n
    eaten = int(round(sum(x * f for x, f in zip(n_st, base["stage_cattle_yr"]))))
    head = float(lvs[sel].sum() * AREA / PR.HEAD_T)
    food_rows.append((round(float(lat[c]), 1), round(float(lon[c]), 1), np.round(n_st).astype(int), eaten, head))

# fig 5: ranges over herders' country. Around the pocket with the most ancients among livestock, a 500 km square: each cell's
# expected adults and ancients (presence x the run's local density x area x the stage share) drawn as Poisson numbers, each a
# circle whose area is its food over the local prey's sustainable offtake (MG.OFFTAKE)
cands = [(p["stages"][3], p.get("livestock_head", 0), lid, p) for lid, r in dragons.items() for p in r["pocket_list"]
         if p.get("stages") and p["stages"][3] and p.get("livestock_head")]
if not cands:
    cands = [(p["stages"][3], 0, lid, p) for lid, r in dragons.items() for p in r["pocket_list"] if p.get("stages")]
_, _, lid0, p0 = max(cands, key=lambda x: (x[0], x[1]))
half = 250.0 / 111.0
cl = max(np.cos(np.radians(p0["lat"])), 0.3)
box = (p0["lon"] - half / cl, p0["lon"] + half / cl, p0["lat"] - half, p0["lat"] + half)
inb = (lat > box[2]) & (lat < box[3]) & (np.abs(((lon - p0["lon"] + 180) % 360) - 180) < half / cl)
fig, ax = plt.subplots(figsize=(6.2, 6.2))
raster(ax, lvs, box=box, cmap="Purples", vmax=12, px=500)
rng = np.random.default_rng(967)
n_circ = {2: 0, 3: 0}
for lid in dragons:
    k = ids.index(lid)
    for c in np.flatnonzero(inb & (P[k] >= 0.02)):
        e = float(P[k][c] * dloc[c] * AREA)
        pt = max(float(prey[c]), 0.05)
        for s_ in (2, 3):
            for _ in range(rng.poisson(e * base["share"][s_])):
                rkm = np.sqrt(base["stage_cattle_yr"][s_] * PR.HEAD_T / (MG.OFFTAKE * pt) / np.pi)
                x = lon[c] + rng.uniform(-0.5, 0.5) * np.sqrt(AREA) / 111.0 / cl
                y = lat[c] + rng.uniform(-0.5, 0.5) * np.sqrt(AREA) / 111.0
                ax.add_patch(matplotlib.patches.Ellipse((x, y), 2 * rkm / 111.0 / cl, 2 * rkm / 111.0, fill=False, ec=KINDS[kind(lid)],
                                                        lw=2.2 if s_ == 3 else 1.0, ls="-" if s_ == 3 else "--"))
                n_circ[s_] += 1
herd_here = float(lvs[inb].sum() * AREA / PR.HEAD_T)
ax.set_title(f"An ancient's country: {n_circ[3]} ancients (solid), {n_circ[2]} adults (dashed)\n500 km square at {p0['lat']}, {p0['lon']};"
             f" livestock shaded, ~{herd_here:,.0f} head", fontsize=10)
img_range = save(fig, "ranges.png")
anc_rng = base["stage_cattle_yr"][3] * PR.HEAD_T / (MG.OFFTAKE * 1.0)

# ---- per kind -------------------------------------------------------------------------------------------------------------------
kind_rows = sorted(((kind(lid), r["count"], r.get("stages") or [0] * 4, r.get("natural_count"), r.get("peopled_share"),
                     r.get("suitable_reached")) for lid, r in dragons.items()), key=lambda x: -x[1])
giants = {k: r for k, r in mf.items() if k not in dragons}
bounties = []
for lid, r in dragons.items():
    for p in r["pocket_list"]:
        if p.get("stages") and p["stages"][3] and p.get("livestock_head"):
            bounties.append((p["livestock_head"], kind(lid), p))
bounties = [b for b in bounties if b[0] / max(b[2]["km2"], 1) * b[2].get("ancient_range_km2", 0) >= 20]  # (at least a herd of 20 in its range)
bounties.sort(key=lambda x: x[0] / max(x[2]["km2"], 1) * x[2].get("ancient_range_km2", 0))  # (the smallest herds under an ancient first: the ruined valleys)

# ---- html -----------------------------------------------------------------------------------------------------------------------
T = lambda rows: "".join(f"<tr><td>{nm}</td><td>{km2:,}</td>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>" for nm, km2, cells in rows)
sched_head = "".join(f"<th>{n}</th>" for n in SCHED)
sched_tbl = "".join(
    f"<tr><td>{n}</td><td>{'/'.join(f'{x:g}' for x in DA.structure(n)['mortality'])}</td><td>{DA.structure(n)['share'][3]:.1%}</td>"
    f"<td>{DA.structure(n)['eco_mass_kg'] / 1000:.1f} t</td><td>{DA.structure(n)['generation_yr']:.0f} / {DA.structure(n)['generation_mass_yr']:.0f}</td>"
    f"<td>{DA.structure(n)['cattle_yr']:.1f}</td><td>{DA.structure(n)['stage_cattle_yr'][2]:.0f} / {DA.structure(n)['stage_cattle_yr'][3]:.0f}</td></tr>"
    for n in SCHED)
dens_tbl = "".join(f"<tr><td>{lab}</td><td>{n}</td><td>1 per {inv:,.0f}</td><td>{cnt:,.0f}</td></tr>" for lab, n, inv, cnt in dens_rows)
food_tbl = "".join(f"<tr><td>{a}, {b}</td><td>{DA.stages_text(list(st)) or '-'}</td><td>{e:,}</td><td>{h:,.0f}</td><td>{(e / h if h else float('nan')):.2%}</td></tr>"
                   for a, b, st, e, h in food_rows)
kind_tbl = "".join(f"<tr><td><span class='sw' style='background:{KINDS[k]}'></span>{k}</td><td>{n:,}</td><td>{DA.stages_text(st)}</td>"
                   f"<td>{(nc or 0):,}</td><td>{(ps or 0):.0%}</td><td>{(sr or 0):.0%}</td></tr>" for k, n, st, nc, ps, sr in kind_rows)
def _bounty_li(h, k, p):
    dens_head = h / max(p["km2"], 1)  # head of stock per km2 in the pocket
    herd = dens_head * p.get("ancient_range_km2", 0)
    eat = base["stage_cattle_yr"][3]
    return (f"<li>{p['stages'][3]} ancient {k} dragon{'s' if p['stages'][3] > 1 else ''} in the {p['country']} at {p['lat']}, {p['lon']}: each takes"
            f" ~{eat:.0f} head a year; its ~{p.get('ancient_range_km2', 0):,} km² range holds ~{herd:,.0f} head of the herders' stock"
            f" ({eat / max(herd, 1e-9):.0%} a year)</li>")


bounty_li = "".join(_bounty_li(h, k, p) for h, k, p in bounties[:4])
giant_line = ", ".join(f"{k.replace('_', ' ')} {r['count']:,} now / ~{r.get('natural_count', 0):,} natural" for k, r in giants.items())
html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Age of dragons</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e0d8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#18181a;--fg:#eee;--mut:#a0a0a6;--line:#333}}}}
:root[data-theme=dark]{{--bg:#18181a;--fg:#eee;--mut:#a0a0a6;--line:#333}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:15px;margin:16px 0 4px}} .mut{{color:var(--mut)}}
img{{max-width:100%;border-radius:6px;background:#fff}} .row{{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-start}}
table{{border-collapse:collapse;font-size:12.5px;margin:4px 0}} td,th{{padding:2px 8px;border-bottom:1px solid var(--line);text-align:right}}
td:first-child,th:first-child{{text-align:left}} .sw{{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}}
.wrap{{overflow-x:auto}}
</style></head><body>
<h1>The age of dragons: natural against present numbers</h1>
<div class="mut">PW-967 review, for the owner. World 2a7385 (L7), dnd peoples, roll 7000, settings at their (not final) defaults: natural density from the prey,
base age schedule, generation from the schedule, 1 dragon per {DKM2:,.0f} km² and 1 giant per 2,000 km² where peoples press them. The other candidates are
worked from the same run's fields. Nothing is picked: the settings are meta.megafauna_natural, meta.dragon_ages, meta.dragon_generation.</div>
<h2>1. Before the peoples, and now</h2><img src="{img_maps}" alt="maps">
<div class="row"><div class="wrap"><table><tr><th>natural density</th><th>schedule</th><th>per dragon</th><th>dragons in their country</th></tr>{dens_tbl}
<tr><td><b>present, peopled country</b></td><td>any</td><td>1 per {DKM2:,.0f}</td><td>{now_total:,} (the run)</td></tr></table>
<div class="mut">Their country: {country_km2 / 1e6:.1f} M km², any kind's habitat &ge; 0.5. Prey-based rows use the run's prey cell by cell (median there {prey_med:.1f} t/km²);
Damuth rows are uniform. Present: 1 per {DKM2:,.0f} is {rp[0]:.0f}-{rp[1]:.0f}x below the prey-based values, {rd[0]:.0f}-{rd[1]:.0f}x below Damuth's.</div></div>
<img src="{img_time}" alt="over time" style="max-width:520px"></div>
<h2>2. What they eat from: wild herds and livestock</h2><img src="{img_prey}" alt="prey">
<div class="mut">Wild herbivores proportional to grazing NPP through ~10 t/km² on rich savanna (the McNaughton 1989 / Coe 1976 fits are not on file yet);
small folk cut them by up to 60% outside tundra and mountains; livestock by way of life. A model, not a fit: see planet/lineages/prey.py.</div>
<h2>3. Age schedules (PW-958)</h2><img src="{img_ages}" alt="schedules">
<table><tr><th>schedule</th><th>mortality wy/yg/ad/anc</th><th>ancients</th><th>ecological mass</th><th>generation (flat / ~mass), yr</th><th>cattle/yr per dragon</th><th>adult / ancient cattle/yr</th></tr>{sched_tbl}</table>
<h2>4. Counts over familiar areas (anc = ancients, ad = adults, yg = young, wy = wyrmlings)</h2>
<div class="mut">Owner's hunch to compare, not a target: California ~2 ancients, ~10 adults, 30+ young.</div>
<div class="wrap"><b>Present, peopled dragon country (1 per {DKM2:,.0f} km²)</b><table><tr><th>area</th><th>km²</th>{sched_head}</tr>{T(present_rows)}</table></div>
<div class="wrap"><b>Natural, from the prey (at the dragon country's median, {prey_med:.1f} t/km²)</b><table><tr><th>area</th><th>km²</th>{sched_head}</tr>{T(natprey_rows)}</table></div>
<div class="wrap"><b>Natural, Damuth on Marshall's dinosaur line</b><table><tr><th>area</th><th>km²</th>{sched_head}</tr>{T(natmeso_rows)}</table></div>
<h2>5. Food against the livestock beside them (present, base schedule)</h2>
<div class="row"><div class="wrap"><table><tr><th>California-sized square at</th><th>dragons there</th><th>cattle eaten a year</th><th>livestock head there</th><th>share</th></tr>{food_tbl}</table>
<div class="mut">In aggregate small. Locally an ancient takes ~{base['stage_cattle_yr'][3]:.0f} head a year (~{base['stage_cattle_yr'][3] * PR.HEAD_T:.0f} t live): at 1 t/km² of prey and
10%/yr offtake that is ~{anc_rng:,.0f} km² of wild country, or a valley of herders. That is where bounties come from (PW-961):</div><ul>{bounty_li or '<li>none in this run</li>'}</ul></div>
<img src="{img_range}" alt="ranges" style="max-width:460px"></div>
<h2>6. Per kind (present, base)</h2><table><tr><th>kind</th><th>now</th><th>by stage</th><th>natural in the same country</th><th>in peopled country</th><th>of their country reached</th></tr>{kind_tbl}</table>
<div class="mut">Giants (no stages): {giant_line}.</div>
<p class="mut">Made by docs/review/megafauna/age_of_dragons.py from one run; sources in docs/references/megafauna/README.md (Carbone &amp; Gittleman 2002 and Marshall et al. 2021 on file;
Nagy et al. 1999's reptile intercept unverified).</p>
</body></html>"""
(OUT / "age-of-dragons.html").write_text(html)
print("wrote", OUT / "age-of-dragons.html", "circles", n_circ, "squares", len(food_rows), "range box", p0["lat"], p0["lon"])
