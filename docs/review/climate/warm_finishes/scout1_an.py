"""Scout 203 (PW-1161 pass 1): per-draw split of the finish on scout 194's 72 L6 runs (copied, read only).

usage: uv run python docs/review/climate/warm_finishes/scout1_an.py JUDGE_DIR [ARM ...]
JUDGE_DIR holds <arm>_r<roll>_<tag>/seed*_L6.json.gz (paired.sh layout). For every draw: the end T and the finish
moment's T against pre-industrial, why the finish moment fails, the dT split at the end (co2_term + albedo_term +
ghg + drift + star = target), lane 80's forcing F = ln src - ln erosion supply (last 10 Myr; supply against 250-300
Myr), the erosion rate and weathering area against 250-300, land share, the land ice, and the pCO2 at the end.
Then: counts against the bar (-6..+5, owner D19) and the old edge +3, and a regression of end T on F and albedo.
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from planet import highlights as H  # noqa: E402
from tools import judge as J  # noqa: E402


def mean(st, k, a, b, f=lambda x: x):
    v = [f(r[k]) for r in st if a <= r["t"] < b and r.get(k) is not None]
    return float(np.mean(v)) if v else float("nan")


def draw(p):
    raw = json.load(gzip.open(p))
    s, bar, st, fm = J.judge_draw(raw)
    end = st[-1]["t"]
    e = st[-1]
    win = [r for r in st if r["t"] >= end - 10 - 1e-9]
    wT = [r["true_temp_c"] - H.PREIND_T for r in win]
    sup0, sup1 = mean(st, "w_supply", 250, 300), mean(st, "w_supply", end - 10, end + 1)
    rate0, rate1 = mean(st, "w_rate", 250, 300), mean(st, "w_rate", end - 10, end + 1)
    ar0, ar1 = mean(st, "w_area", 250, 300), mean(st, "w_area", end - 10, end + 1)
    src10 = mean(st, "src", end - 10, end + 1, np.log)
    sup = np.log(sup1 / sup0)
    ups = [u for u in raw["updates"] if u.get("pco2") is not None]
    return dict(
        ok=bool(bar["ok"] and fm["passes"]), why=",".join(H.habitable(e)) or "-", fm_back=fm["before_end_myr"],
        endT=e["true_temp_c"] - H.PREIND_T, minwT=min(wT), maxwT=max(wT), dT=e["dT"], target=e["target"],
        co2=e["co2"], co2t=e["co2_term"], alb=e["albedo_term"], ghg=e["ghg"], drift=e["drift"], star=e["star"],
        star_ctl=e.get("star_ctl", 0.0), ice=e["iced_land_pct"], trees=e["wet_eq_trees_pct"],
        pco2=ups[-1]["pco2"] if ups else float("nan"), src10=src10, sup=sup, F=src10 - sup,
        rate=np.log(rate1 / rate0), area=np.log(ar1 / ar0), land0=mean(st, "land", 290, 310), land1=mean(st, "land", end - 10, end + 1),
        lnsrc_850=mean(st, "src", 850, end - 10, np.log), lnsink10=mean(st, "sink", end - 10, end + 1, np.log),
        co2_late=mean(st, "co2", 600, 1000), alb_late=mean(st, "albedo_term", 600, 1000),
        ice_late_min=min(r["iced_land_pct"] for r in st if r["t"] >= 600 and r.get("iced_land_pct") is not None),
        ice_late_max=max(r["iced_land_pct"] for r in st if r["t"] >= 600 and r.get("iced_land_pct") is not None),
        ice_850_max=max(r["iced_land_pct"] for r in st if r["t"] >= 850 and r.get("iced_land_pct") is not None),
    )


def main():
    jd = Path(sys.argv[1])
    arms = sys.argv[2:] or ["main", "cap"]
    allrows = {}
    for a in arms:
        rows = []
        for d in sorted(jd.glob(f"{a}_r*_*")):
            roll, tag = d.name[len(a) + 2:].split("_", 1)
            for p in sorted(d.glob("seed*_L6.json.gz")):
                r = draw(p)
                r["name"] = f"{roll} {tag:5} {p.name.split('_')[0][4:]:>6}"
                rows.append(r)
        allrows[a] = rows
        print(f"\n== arm {a}: {len(rows)} draws (T against pre-industrial 13.8 C; split at the run's end)")
        print(f"{'roll   tag     seed':22} pass  endT  wmin  wmax fails_at_end        | dT    co2t   alb   ghg drift  star | co2e  pCO2 | "
              f"lnsrc10 lnsup  F    rate  area | land  ice  iceMx850 | co2late alblate")
        for r in sorted(rows, key=lambda r: -r["endT"]):
            print(f"{r['name']:22} {'Y' if r['ok'] else '-':>4} {r['endT']:+5.1f} {r['minwT']:+5.1f} {r['maxwT']:+5.1f} {r['why'][:19]:19} | "
                  f"{r['dT']:+5.1f} {r['co2t']:+5.1f} {r['alb']:+5.1f} {r['ghg']:+5.1f} {r['drift']:+5.2f} {r['star']:+5.1f} | "
                  f"{r['co2']:+.2f} {r['pco2']:5.0f} | {r['src10']:+.2f} {r['sup']:+.2f} {r['F']:+.2f} {r['rate']:+.2f} {r['area']:+.2f} | "
                  f"{100 * r['land1']:4.1f} {r['ice']:4.1f} {r['ice_850_max']:5.1f} | {r['co2_late']:+.2f} {r['alb_late']:+.2f}")
        T = np.array([r["endT"] for r in rows])
        wmin = np.array([r["minwT"] for r in rows])
        print(f"  end T median {np.median(T):+.2f} sd {T.std():.2f}; end T > +5: {(T > 5).sum()}, > +3: {(T > 3).sum()}, < -6: {(T < -6).sum()}")
        print(f"  whole last 10 Myr above +5 (no moment inside the warm edge): {(wmin > 5).sum()}; soft pass {sum(r['ok'] for r in rows)}/{len(rows)}")
        print(f"  fails: " + "; ".join(f"{r['name'].split()[1]} {r['name'].split()[2]} r{r['name'].split()[0]} end {r['endT']:+.1f} ({r['why']})"
                                     for r in rows if not r["ok"]))
        X = {k: np.array([r[k] for r in rows]) for k in ("F", "src10", "sup", "alb", "co2t", "drift", "ghg", "rate", "area", "land1", "co2_late")}
        for cols in (["F"], ["src10", "sup"], ["F", "alb"]):
            A = np.c_[[X[c] for c in cols]].T
            A = np.c_[A, np.ones(len(T))]
            c, *_ = np.linalg.lstsq(A, T, rcond=None)
            r2 = 1 - ((T - A @ c) ** 2).sum() / ((T - T.mean()) ** 2).sum()
            print(f"  end T ~ {'+'.join(cols):12} coef {np.round(c, 2)} R2 {r2:.2f}")
        for k in ("co2t", "alb", "drift", "ghg", "rate", "area", "land1"):
            print(f"  corr(end T, {k}) {np.corrcoef(X[k], T)[0, 1]:+.2f}; median {np.median(X[k]):+.3f}")
    json.dump({a: [{k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in r.items()} for r in rows]
               for a, rows in allrows.items()}, open(Path(sys.argv[1]).parent / "rows203.json", "w"), indent=0)


if __name__ == "__main__":
    main()
