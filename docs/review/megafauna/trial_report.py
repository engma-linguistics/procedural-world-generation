"""trial_report.py OUTDIR: PW-923 density-trial figures + html from trial/{1000,5000,10000}/2a7385-7000.npz."""
import json, sys, base64, io
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from planet.grid import build_grid

S = Path("/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/trial")
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
DENS = ["1000", "5000", "10000"]
KINDS = {"red": "#d33", "blue": "#2a6fdb", "green": "#2b8a3e", "black": "#222", "white": "#9ad",
         "gold": "#d4a017", "silver": "#8a8f98", "bronze": "#b0702c", "copper": "#c8643b", "brass": "#c9b037"}
runs = {}
for d in DENS:
    z = np.load(S / d / "2a7385-7000.npz")
    runs[d] = {"pres": json.loads(str(z["pres"])), "tags": dict(zip([str(x) for x in z["tagnames"]], z["tags"])),
               "label": z["label"], "level": int(z["level"])}
g = build_grid(runs["5000"]["level"])
lat = np.degrees(np.arcsin(g.centers[:, 2]))
lon = np.degrees(np.arctan2(g.centers[:, 1], g.centers[:, 0]))
T = runs["5000"]["tags"]
land = T["land"]
names = {nm["rank"]: nm["name"] for nm in runs["5000"]["pres"]["landmasses"]}


def kind_of(lid):
    return lid.removesuffix("_dragon") if lid.removesuffix("_dragon") in KINDS else None


def dragons(d):
    mf = runs[d]["pres"]["megafauna"]
    return {kind_of(k): v for k, v in mf.items() if kind_of(k)}


def base(ax, box=None, country=None):
    sel = land if box is None else land & (lat > box[2]) & (lat < box[3]) & (lon > box[0]) & (lon < box[1])
    sea = ~land if box is None else ~land & (lat > box[2]) & (lat < box[3]) & (lon > box[0]) & (lon < box[1])
    s = 0.25 if box is None else 9
    ax.scatter(lon[sea], lat[sea], s=s, c="#dfe9f3", marker="s", linewidths=0)
    ax.scatter(lon[sel], lat[sel], s=s, c="#e8e2d0", marker="s", linewidths=0)
    if country is not None:
        c = sel & T[country[0]]
        ax.scatter(lon[c], lat[c], s=s, c=country[1], marker="s", linewidths=0)
    ax.set_xticks([]); ax.set_yticks([])
    if box:
        ax.set_xlim(box[0], box[1]); ax.set_ylim(box[2], box[3])
    else:
        ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ax.set_aspect("equal")


def png(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


imgs = {}
# 1. world maps: every dragon pocket, a dot sized by count, one panel per density
fig, axs = plt.subplots(1, 3, figsize=(15, 3.4))
for ax, d in zip(axs, DENS):
    base(ax)
    tot = 0
    for k, r in dragons(d).items():
        ps = r["pocket_list"]
        tot += r["count"]
        ax.scatter([p["lon"] for p in ps], [p["lat"] for p in ps], s=[4 + 3 * p["count"] for p in ps], c=KINDS[k],
                   edgecolors="k", linewidths=0.2, alpha=0.85)
    ax.set_title(f"1 per {int(d):,} km²: ~{tot:,} dragons", fontsize=11)
imgs["world"] = png(fig)

# 2. close views at 1 per 5,000: a swamp of black dragons and a volcano country of red ones (the best-filled pockets)
def close(d, lid, tag, col, word, km=900):
    r = runs[d]["pres"]["megafauna"].get(lid)
    if not r or not r["pocket_list"]:
        return None
    ps = sorted(r["pocket_list"], key=lambda p: (-(p["count"] in (2, 3)), -p["count"]))
    p = ps[0]
    dl = km / 111.0
    dlon = dl / max(np.cos(np.radians(p["lat"])), 0.3)
    box = (p["lon"] - dlon, p["lon"] + dlon, p["lat"] - dl, p["lat"] + dl)
    fig, ax = plt.subplots(figsize=(3.6, 3.6))
    base(ax, box, (tag, col))
    near = [q for q in r["pocket_list"] if box[0] < q["lon"] < box[1] and box[2] < q["lat"] < box[3]]
    for q in near:
        ax.scatter(q["lon"], q["lat"], s=60 + 40 * q["count"], c=KINDS[kind_of(lid)], edgecolors="w", linewidths=1.2, zorder=3)
        ax.annotate(str(q["count"]), (q["lon"], q["lat"]), ha="center", va="center", color="w", fontsize=9, weight="bold", zorder=4)
    n = sum(q["count"] for q in near)
    title = f"this {word} has {p['count']} {kind_of(lid)} dragon{'s' if p['count'] > 1 else ''}"
    ax.set_title(title, fontsize=10)
    return png(fig), title, f"{p['landmass_name'] or ''} {p['lat']}, {p['lon']}; {n} in this {2 * km:,} km square ({len(near)} pockets)"


imgs["close"] = [c for c in (close("5000", "black_dragon", "wetland", "#7fb3a0", "swamp"),
                              close("5000", "red_dragon", "volcanic", "#e4a08a", "volcano country"),
                              close("5000", "white_dragon", "mountain", "#c9d6e3", "cold range")) if c]

# 3. a coarser regional view: the biggest continent's busiest 3,000 km square, at each density
mf5 = runs["5000"]["pres"]["megafauna"]
allp = [(p, kind_of(k)) for k, r in mf5.items() if kind_of(k) for p in r["pocket_list"]]
best, bc = None, -1
for p, _ in allp:
    c = sum(q["count"] for q, _ in allp if abs(q["lat"] - p["lat"]) < 13 and abs(q["lon"] - p["lon"]) < 13 / max(np.cos(np.radians(p["lat"])), 0.3))
    if c > bc:
        best, bc = p, c
dl = 13.5
dlon = dl / max(np.cos(np.radians(best["lat"])), 0.3)
box = (best["lon"] - dlon, best["lon"] + dlon, best["lat"] - dl, best["lat"] + dl)
fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
region = {}
for ax, d in zip(axs, DENS):
    base(ax, box)
    n = 0
    for k, r in dragons(d).items():
        ps = [p for p in r["pocket_list"] if box[0] < p["lon"] < box[1] and box[2] < p["lat"] < box[3]]
        n += sum(p["count"] for p in ps)
        ax.scatter([p["lon"] for p in ps], [p["lat"] for p in ps], s=[15 + 12 * p["count"] for p in ps], c=KINDS[k], edgecolors="k", linewidths=0.3)
    region[d] = n
    ax.set_title(f"1 per {int(d):,} km²: expect ~{n} here", fontsize=10)
imgs["region"] = png(fig)
region_where = f"{best.get('landmass_name') or ''}, a 3,000 km square around {best['lat']}, {best['lon']}"

# 4. counts by kind per landmass at each density (the landmasses with the most dragons)
tbl = {}
for d in DENS:
    for k, r in dragons(d).items():
        for p in r["pocket_list"]:
            m = p["landmass_name"] or "islands"
            tbl.setdefault(m, {}).setdefault(k, {}).setdefault(d, 0)
            tbl[m][k][d] += p["count"]
top = sorted(tbl, key=lambda m: -sum(v.get("5000", 0) for v in tbl[m].values()))[:5]
json.dump({"tbl": tbl, "top": top, "region": region, "region_where": region_where, "close": [c[1:] for c in imgs["close"]],
           "totals": {d: {k: r["count"] for k, r in dragons(d).items()} for d in DENS},
           "pockets": {d: {k: r["pockets"] for k, r in dragons(d).items()} for d in DENS},
           "reached": {d: {k: r.get("suitable_reached") for k, r in dragons(d).items()} for d in DENS}},
          open(OUT / "trial.json", "w"), indent=1)
rows = []
for m in top:
    for k in KINDS:
        if k in tbl[m]:
            rows.append((m, k, [tbl[m][k].get(d, 0) for d in DENS]))
th = "".join(f"<th>1 per {int(d):,}</th>" for d in DENS)
body = []
last = None
for m, k, v in rows:
    body.append(f"<tr><td>{m if m != last else ''}</td><td><span class='sw' style='background:{KINDS[k]}'></span>{k}</td>" + "".join(f"<td>{x}</td>" for x in v) + "</tr>")
    last = m
tot = [sum(runs[d]["pres"]["megafauna"][x]["count"] for x in runs[d]["pres"]["megafauna"] if kind_of(x)) for d in DENS]
body.append("<tr class='tot'><td>whole world</td><td>all dragons</td>" + "".join(f"<td>{x:,}</td>" for x in tot) + "</tr>")
closes = "".join(f"<figure><img src='{c[0]}'><figcaption>{c[2]}</figcaption></figure>" for c in imgs["close"])
html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dragon density trial</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e0d8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#18181a;--fg:#eee;--mut:#a0a0a6;--line:#333}}}}
:root[data-theme=dark]{{--bg:#18181a;--fg:#eee;--mut:#a0a0a6;--line:#333}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:15px;margin:14px 0 4px}} .mut{{color:var(--mut)}}
img{{max-width:100%;border-radius:6px;background:#fff}} .row{{display:flex;flex-wrap:wrap;gap:10px}} figure{{margin:0;flex:1 1 300px}}
figcaption{{font-size:12px;color:var(--mut)}} table{{border-collapse:collapse;font-size:13px}} td,th{{padding:2px 10px;border-bottom:1px solid var(--line);text-align:right}}
td:first-child,td:nth-child(2),th:first-child,th:nth-child(2){{text-align:left}} .sw{{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}}
.tot td{{font-weight:600}}
</style></head><body>
<h1>Dragon density trial: 1 per 1,000 / 5,000 / 10,000 km²</h1>
<div class="mut">World 2a7385 (seed 11, L7), dnd peoples seed 7000, PW-923. Dots are pockets of country with dragons, sized by how many; colours are the kinds. Pick one density.</div>
<h2>The world</h2><img src="{imgs['world']}">
<h2>Close up (1 per 5,000 km²)</h2><div class="row">{closes}</div>
<h2>A region: {region_where}</h2><img src="{imgs['region']}">
<h2>Dragons by kind, on the five landmasses with the most</h2>
<table><tr><th>landmass</th><th>kind</th>{th}</tr>{''.join(body)}</table>
<p class="mut">Megafauna are counted per pocket (presence x density x area, rounded). Giants are unchanged by this trial (~1 per 100-200 km², in steadings). The code default is 1 per 5,000 km².</p>
</body></html>"""
(OUT / "density-trial.html").write_text(html)
print(json.dumps({"totals": tot, "region": region, "top": top}))
