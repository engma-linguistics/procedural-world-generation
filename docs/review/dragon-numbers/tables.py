"""tables.py OUT_DIR [ARM=DIR ...]: the dragon-numbers report's tables (numbers.json, tables.md) and charts (PNG) from census.py outputs.

Each ARM=DIR names a directory of census.py outputs (WORLD_ROLL.census.json / .census.npz). The first arm is the main one (the
tables and charts); every arm gets the per-kind counts and the white / silver / bronze comparison. Nothing is tuned here; the
analogue figures are typed from the sources named in report.md (each marked there as read or secondary).
Run: uv run --with matplotlib python docs/review/dragon-numbers/tables.py docs/review/dragon-numbers on=OUT/on [B=OUT/B]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(sys.argv[1])
ARMS = dict(a.split("=", 1) for a in sys.argv[2:])
REGION_KM2 = 3.9e6  # the dragon-density paper's Sword Coast-sized region
BIOMES = ("forest", "grassland", "desert", "tundra", "mountain", "wetland", "other")
KINDS = ("red", "blue", "green", "black", "white", "gold", "silver", "bronze", "copper", "brass")
# deaths a year per tiger in India: 378 deaths in 2020-24 (Rajya Sabha reply, 1 Aug 2025; secondary) over 3,682 tigers (All-India
# estimate 2022; secondary): ~0.021. The stated estimate of the dragons' toll applies it to the dragons in peopled country.
TIGER_DEATHS_PER_TIGER = (378 / 5) / 3682.0


def med(xs):
    xs = [x for x in xs if x is not None]
    return (float(np.median(xs)), float(min(xs)), float(max(xs))) if xs else (None, None, None)


def biome_of(bits, tags):
    has = {t: (bits >> i) & 1 == 1 for i, t in enumerate(tags)}
    b = np.full(len(bits), 6)
    order = [(4, has["mountain"]), (3, has["tundra"]), (2, has["desert"]), (5, has["wetland"]), (0, has["forest"] | has["jungle"]),
             (1, has["steppe"] | has["open"])]
    for code, cond in reversed(order):
        b = np.where(cond, code, b)
    return b


def world_stats(npz, js):
    z = np.load(npz)
    ids = [str(i) for i in z["ids"]]
    a = float(z["cell_km2"])
    land = z["land"].astype(bool)
    land_km2 = float(land.sum() * a)
    keep = [j for j, i in enumerate(ids) if i.removesuffix("_dragon") in KINDS]  # (the ten kinds; the stems are gone by the present)
    ids = [ids[j] for j in keep]
    now, nop, cty = (z[x][keep].astype(float) for x in ("now", "nopeople", "nopeople_country"))
    people = z["people"].astype(float)
    biome = biome_of(z["biome_bits"].astype(np.int64), [str(t) for t in z["biome_tags"]])
    kinds = {}
    for j, lid in enumerate(ids):
        k = lid.removesuffix("_dragon")
        country = cty[j] > 0
        ckm2 = float(country.sum() * a)
        n, n0, nc = now[j].sum(), nop[j].sum(), cty[j].sum()
        kept = (now[j] >= 0.1 * cty[j]) & country
        held = (now[j] > 0) & country
        pc, ec = country & (people > 0), country & (people <= 0)
        kinds[k] = {"now": n, "nopeople": n0, "country_nopeople": nc, "country_km2": ckm2,
                    "per10k_now": n / ckm2 * 1e4 if ckm2 else None, "per10k_before": nc / ckm2 * 1e4 if ckm2 else None,
                    "held_share": float(held.sum() / max(country.sum(), 1)),
                    "held_peopled": float((held & pc).sum() / pc.sum()) if pc.any() else None,
                    "held_empty": float((held & ec).sum() / ec.sum()) if ec.any() else None,
                    "peopled_share": float(pc.sum() / max(country.sum(), 1)), "kept10_share": float(kept.sum() / max(country.sum(), 1)),
                    "region_now": n / land_km2 * REGION_KM2, "region_before": nc / land_km2 * REGION_KM2}
    tot_now, tot_c = now.sum(0), cty.sum(0)
    by_biome = {}
    for bi, bn in enumerate(BIOMES):
        m = land & (biome == bi)
        km2 = float(m.sum() * a)
        if km2 > 0:
            by_biome[bn] = {"land_share": km2 / land_km2, "per10k_now": float(tot_now[m].sum() / km2 * 1e4),
                            "per10k_before": float(tot_c[m].sum() / km2 * 1e4)}
    peopled = people > 0
    in_range = peopled & (tot_now > 0)
    dr_peopled = float(tot_now[in_range].sum())
    ppl_range = float(people[in_range].sum())
    tr = js["tracks"]
    times = sorted({t for rows in tr.values() for t, _ in rows}, reverse=True)
    series = {t: 0.0 for t in times}
    for rows in tr.values():
        for t, c in rows:
            series[t] += c
    peak_t = max(series, key=series.get) if series else None
    return {"kinds": kinds, "biomes": by_biome, "land_km2": land_km2, "total_now": float(now.sum()), "total_nopeople": float(nop.sum()),
            "total_country": float(cty.sum()), "region_now": float(now.sum()) / land_km2 * REGION_KM2,
            "region_before": float(cty.sum()) / land_km2 * REGION_KM2, "people": float(people.sum()),
            "people_in_range": ppl_range, "dragons_in_peopled": dr_peopled,
            "dragons_per_million_in_range": dr_peopled / ppl_range * 1e6 if ppl_range else None,
            "est_deaths_yr": dr_peopled * TIGER_DEATHS_PER_TIGER,
            "est_deaths_per_million_in_range": dr_peopled * TIGER_DEATHS_PER_TIGER / ppl_range * 1e6 if ppl_range else None,
            "peak": {"count": series.get(peak_t), "ago_kyr": peak_t}, "kill_w_sum": js.get("kill_w_sum")}


def arm_stats(d):
    out = {}
    for js in sorted(Path(d).glob("*.census.json")):
        key = js.name.removesuffix(".census.json")
        out[key] = world_stats(js.with_name(key + ".census.npz"), json.load(open(js)))
    return out


def fmt(x, nd=None):
    if x is None:
        return "-"
    if nd is None:
        nd = 0 if abs(x) >= 100 else 1 if abs(x) >= 10 else 2 if abs(x) >= 1 else 3
    return f"{x:,.{nd}f}"


def mr(t):
    m, lo, hi = t
    return "-" if m is None else f"{fmt(m)} ({fmt(lo)}-{fmt(hi)})"


res = {name: arm_stats(d) for name, d in ARMS.items()}
main = next(iter(res))
W = res[main]
lines = [f"Arm `{main}`, {len(W)} worlds ({', '.join(sorted(W))}); medians over the worlds (range).", ""]
lines += ["| | before people | today |", "|---|---|---|",
          f"| dragons on the world | {mr(med([w['total_country'] for w in W.values()]))} | {mr(med([w['total_now'] for w in W.values()]))} |",
          f"| ...on the cells they hold today, people taken out | {mr(med([w['total_nopeople'] for w in W.values()]))} | |",
          f"| in a Sword Coast-sized region (3.9 Mkm2, land average) | {mr(med([w['region_before'] for w in W.values()]))} | {mr(med([w['region_now'] for w in W.values()]))} |",
          f"| deep-time peak (all dragons) | {mr(med([w['peak']['count'] for w in W.values()]))} | at {', '.join(fmt(w['peak']['ago_kyr']) for w in W.values())} kyr ago |", ""]
lines += ["Per kind. Before people, the most: the kind's whole own country, no people (an upper bound: even without people a kind "
          "does not hold all of it). On today's land: the cells it holds now, with the people taken out. Today: the model's present.", "",
          "| kind | before people, the most | on today's land, no people | today | today / before | per 10,000 km2 of its country, before -> today | region, before -> today | country held (peopled part / empty part) | its country peopled | country at >= 10% of its pre-people density |",
          "|---|---|---|---|---|---|---|---|---|---|"]
for k in KINDS:
    rows = [w["kinds"][k] for w in W.values() if k in w["kinds"]]
    if not rows:
        continue
    b, n = med([r["country_nopeople"] for r in rows]), med([r["now"] for r in rows])
    ratio = med([r["now"] / r["country_nopeople"] if r["country_nopeople"] else None for r in rows])
    lines.append(f"| {k} | {mr(b)} | {mr(med([r['nopeople'] for r in rows]))} | {mr(n)} | {fmt(ratio[0], 2)} | {fmt(med([r['per10k_before'] for r in rows])[0])} -> {fmt(med([r['per10k_now'] for r in rows])[0])} | "
                 f"{fmt(med([r['region_before'] for r in rows])[0])} -> {fmt(med([r['region_now'] for r in rows])[0])} | "
                 f"{fmt(med([r['held_share'] for r in rows])[0], 2)} ({fmt(med([r['held_peopled'] for r in rows])[0], 2)} / {fmt(med([r['held_empty'] for r in rows])[0], 2)}) | "
                 f"{fmt(med([r['peopled_share'] for r in rows])[0], 2)} | {fmt(med([r['kept10_share'] for r in rows])[0], 2)} |")
lines += ["", "All dragons by biome (per 10,000 km2 of that biome's land):", "", "| biome | share of land | before people | today |", "|---|---|---|---|"]
for bn in BIOMES:
    rows = [w["biomes"][bn] for w in W.values() if bn in w["biomes"]]
    if rows:
        lines.append(f"| {bn} | {fmt(med([r['land_share'] for r in rows])[0], 2)} | {mr(med([r['per10k_before'] for r in rows]))} | {mr(med([r['per10k_now'] for r in rows]))} |")
lines += ["", "Meeting them (people living in cells with dragons; the toll is an estimate at India's tigers' rate per animal):", "",
          "| | median (range) |", "|---|---|",
          f"| people in the dragons' range, share of all | {mr(med([w['people_in_range'] / w['people'] for w in W.values()]))} |",
          f"| dragons in peopled country | {mr(med([w['dragons_in_peopled'] for w in W.values()]))} |",
          f"| dragons per million people there | {mr(med([w['dragons_per_million_in_range'] for w in W.values()]))} |",
          f"| estimated deaths a year, world (x {TIGER_DEATHS_PER_TIGER:.3f} a dragon) | {mr(med([w['est_deaths_yr'] for w in W.values()]))} |",
          f"| estimated deaths a year per million people in range | {mr(med([w['est_deaths_per_million_in_range'] for w in W.values()]))} |"]
if len(res) > 1:
    lines += ["", "Arms compared, median count today (range):", "", "| kind | " + " | ".join(res) + " |", "|---|" + "---|" * len(res)]
    for k in KINDS + ("all",):
        cells = []
        for name, R in res.items():
            if k == "all":
                cells.append(mr(med([w["total_now"] for w in R.values()])))
            else:
                cells.append(mr(med([w["kinds"][k]["now"] for w in R.values() if k in w["kinds"]])))
        lines.append(f"| {k} | " + " | ".join(cells) + " |")
    first = res[main]
    for name, R in list(res.items())[1:]:
        lines += ["", f"`{name}` over `{main}`, world by world (the worlds both arms ran), median ratio (range):", "", "| kind | ratio |", "|---|---|"]
        common = sorted(set(first) & set(R))
        for k in KINDS + ("all",):
            if k == "all":
                rs = [R[w]["total_now"] / first[w]["total_now"] for w in common if first[w]["total_now"]]
            else:
                rs = [R[w]["kinds"][k]["now"] / first[w]["kinds"][k]["now"] for w in common
                      if k in first[w]["kinds"] and k in R[w]["kinds"] and first[w]["kinds"][k]["now"] > 0]
            lines.append(f"| {k} | {mr(med(rs))} |")
(OUT / "tables.md").write_text("\n".join(lines) + "\n")
json.dump(res, open(OUT / "numbers.json", "w"), indent=1, default=float)
print("\n".join(lines))

# ---- charts (light surface, the dataviz reference palette: blue = before people, orange = today) ----
BLUE, ORANGE, INK, MUTED, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
                     "figure.facecolor": SURF, "axes.facecolor": SURF})
ks = [k for k in KINDS if any(k in w["kinds"] for w in W.values())]
b = [med([w["kinds"][k]["country_nopeople"] for w in W.values() if k in w["kinds"]])[0] for k in ks]
n = [med([w["kinds"][k]["now"] for w in W.values() if k in w["kinds"]])[0] for k in ks]
fig, ax = plt.subplots(figsize=(8, 5))
y = np.arange(len(ks))
ax.barh(y - 0.2, b, 0.38, color=BLUE, label="before people (its whole country, no people)")
ax.barh(y + 0.2, n, 0.38, color=ORANGE, label="today")
for yi, (bb, nn) in enumerate(zip(b, n)):
    ax.text(bb * 1.15, yi - 0.2, f"{bb:,.0f}", va="center", fontsize=8, color=MUTED)
    ax.text(nn * 1.15, yi + 0.2, f"{nn:,.0f}", va="center", fontsize=8, color=MUTED)
ax.set_xscale("log")
ax.set_yticks(y, [f"{k} dragons" for k in ks])
ax.invert_yaxis()
ax.set_xlabel("dragons on the world (median of the worlds, log scale)")
ax.set_title("Dragons before people and today, by kind", loc="left", color=INK, pad=24)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9)
ax.grid(axis="x", color="#e4e3df", lw=0.6)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "dragons_before_after_people.png", dpi=150)

# densities per 100 km2 beside the real apex predators (report.md's analogue table; flagged there as read or secondary)
an = [("lions, Serengeti (call-in survey)", 14.36, "lion"), ("lions, Kenyan community land >100 km from a park", 5.9, "lion"),
      ("lions, Queen Elizabeth NP", 2.4, "lion"), ("tigers, top Indian reserves (Bandipur)", 19.83, "tiger"),
      ("tigers, India mean of studies", 3.45, "tiger"), ("tigers, Russia mean of studies", 0.42, "tiger")]
dn = []
for k in ks:
    rows = [w["kinds"][k] for w in W.values() if k in w["kinds"]]
    dn.append((f"{k} dragons", med([r["per10k_before"] for r in rows])[0] / 100, med([r["per10k_now"] for r in rows])[0] / 100))
fig, ax = plt.subplots(figsize=(8, 6.5))
labels = [a[0] for a in an] + [d[0] for d in dn]
yy = np.arange(len(labels))
for i, (lab, v, kind) in enumerate(an):
    ax.plot([v], [i], "o", ms=8, color="#1baf7a" if kind == "lion" else "#6250d6", mec=SURF, mew=2)
    ax.text(v * 1.3, i, f"{v:g}", va="center", fontsize=8, color=MUTED)
for j, (lab, before, now_) in enumerate(dn):
    i = len(an) + j
    ax.plot([before, now_], [i, i], color="#c3c2b7", lw=2, zorder=1)
    ax.plot([before], [i], "o", ms=8, color=BLUE, mec=SURF, mew=2, label="dragons before people" if j == 0 else None)
    ax.plot([now_], [i], "o", ms=8, color=ORANGE, mec=SURF, mew=2, label="dragons today" if j == 0 else None)
ax.plot([], [], "o", color="#1baf7a", label="lions (Africa)")
ax.plot([], [], "o", color="#6250d6", label="tigers (Asia)")
ax.set_xscale("log")
ax.set_yticks(yy, labels)
ax.invert_yaxis()
ax.set_xlabel("per 100 km2, log scale (dragons: in their own country)")
ax.set_title("Animals per 100 km2", loc="left", color=INK)
ax.grid(axis="x", color="#e4e3df", lw=0.6)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, loc="upper left", fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "dragons_vs_lions_tigers.png", dpi=150)
print("charts", OUT)
