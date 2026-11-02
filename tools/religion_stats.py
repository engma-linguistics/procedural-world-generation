"""Religion stress and stats (PW-1311): peoples runs over several trees, worlds and seeds, then the religion readouts of each, and the
distributions of individuation, pantheon size, faiths and taboo counts across all their cultures.

    uv run python tools/religion_stats.py runs --out DIR [--jobs 4] [--trees dnd,seven_meals] [--seeds 1,2,3] [--worlds 4360a3,af2677]
    uv run python tools/religion_stats.py religion --out DIR [--extra b4d502,a24559,3c1caf]   # (re)derive gods/faiths/taboos into DIR
    uv run python tools/religion_stats.py report --out DIR [--md docs/review/religion/stats-round1.md --png docs/review/religion]

`runs` makes each peoples run with the stock sample tree at that seed (as tools/peoples_robust.py's base family) and saves it under
DIR/runs/<id> (never under the data root's runs/: store.path_of is redirected for new ids only). `religion` reads each run (and the
--extra stored runs, read-only) and writes DIR/religion/<run>/{gods,taboos}.json. `report` reads those and writes the stats.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import planet  # noqa: E402,F401  (thread defaults before numpy)

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ["4360a3", "af2677"]


def _redirect(out: Path):
    """New runs go under out/runs; existing ones are read from the data root."""
    from planet import store as S
    real = S.path_of

    def path_of(kind, item_id):
        p = real(kind, item_id)
        if kind == "run" and not p.exists():
            return out / "runs" / item_id
        return p
    S.path_of = path_of


def one(world: str, tree: str, seed: int, out: Path) -> str:
    sys.path.insert(0, str(ROOT / "tools"))
    import peoples_robust as PR
    from planet.lineages import run as RN
    from planet.lineages import spec as SP
    _redirect(out)
    raw = PR.with_seed(PR._load(tree), seed)
    t = SP.parse(raw)
    t.source = tree
    d = RN.run(world, t, tries=1, name=f"rel-{tree}-{world}-s{seed}")
    (out / "made.jsonl").open("a").write(json.dumps({"run": d.name, "path": str(d), "tree": tree, "world": world, "seed": seed}) + "\n")
    return d.name


def runs(out: Path, jobs: int, trees, seeds, worlds):
    out.mkdir(parents=True, exist_ok=True)
    todo = [(w, t, s) for t in trees for w in worlds for s in seeds]
    procs: list = []
    env = {**os.environ, "NUMBA_NUM_THREADS": "4", "OMP_NUM_THREADS": "4"}
    while todo or procs:
        while todo and len(procs) < jobs:
            w, t, s = todo.pop(0)
            log = open(out / f"log-{t}-{w}-{s}.txt", "w")
            procs.append(subprocess.Popen([sys.executable, __file__, "one", w, t, str(s), "--out", str(out)], stdout=log, stderr=subprocess.STDOUT, env=env))
        time.sleep(5)
        procs = [p for p in procs if p.poll() is None]


def religion(out: Path, extra):
    from planet import store as S
    from planet.lineages import taboos as TB
    made = [json.loads(x) for x in (out / "made.jsonl").read_text().splitlines()] if (out / "made.jsonl").exists() else []
    items = [(m["run"], Path(m["path"]), m["tree"]) for m in made] + [(r, S.find_run(r), "stored") for r in extra]
    for rid, d, tree in items:
        t0 = time.time()
        dest = out / "religion" / rid
        try:
            s = TB.write_religion(d, dest, rebuild=tree == "stored")
            (dest / "tree.txt").write_text(tree)
            print(rid, tree, round(time.time() - t0, 1), "s", s["gods"]["living"], "beings", s.get("faiths", {}).get("faiths"), "faiths", flush=True)
        except Exception as e:  # (one bad run does not stop the rest)
            print(rid, "FAILED", type(e).__name__, e, flush=True)


# ---------------------------------------------------------------- report

def _collect(out: Path):
    rows, odd = [], []
    for dest in sorted((out / "religion").iterdir()):
        if not (dest / "taboos.json").exists():
            continue
        gd = json.loads((dest / "gods.json").read_text())
        tb = json.loads((dest / "taboos.json").read_text())
        tree = (dest / "tree.txt").read_text() if (dest / "tree.txt").exists() else "?"
        B = gd["beings"]
        fa = gd.get("faiths") or {}
        for cid, cu in tb["cultures"].items():
            liv = [B[i] for i in (gd["cultures"].get(cid) or {}).get("living", [])]
            inds = [b["individuation"] for b in liv]
            r = {"run": dest.name, "tree": tree, "culture": cu["name"], "people": cu["people"], "pantheon": len(liv),
                 "lead_ind": max(inds, default=None), "inds": inds, "spells": sum(b["grants_spells"] for b in liv),
                 "taboos": len(cu["taboos"]), "kinds": {}, "faith": (gd["cultures"].get(cid) or {}).get("faith_now")}
            for t in cu["taboos"]:
                r["kinds"][t["kind"]] = r["kinds"].get(t["kind"], 0) + 1
            rows.append(r)
        frs = list(fa.get("list") or [])
        for f in frs:
            f["_run"] = dest.name
        rows_f = frs
        odd.append((dest.name, tree, gd["summary"], rows_f))
    return rows, odd


def _hist(vals, bins):
    h, _ = np.histogram(vals, bins=bins)
    return h


def report(out: Path, md: Path | None, png: Path | None) -> str:
    rows, per = _collect(out)
    if not rows:
        return "no religion outputs: run `religion` first"
    tiers = [0.1, 0.2, 0.45, 0.6, 0.9]
    runs_ = sorted({r["run"] for r in rows})
    L = [f"# Religion stats, round 1 (PW-1311)\n", f"{len(rows)} living cultures in {len(runs_)} peoples runs "
         f"({', '.join(sorted({r['tree'] for r in rows}))}). Made by `tools/religion_stats.py report`.\n"]
    # individuation tier of each culture's leading being
    lead = np.array([r["lead_ind"] for r in rows if r["lead_ind"] is not None])
    allind = np.array([x for r in rows for x in r["inds"]])
    pan = np.array([r["pantheon"] for r in rows])
    tab = np.array([r["taboos"] for r in rows])
    nog = sum(r["lead_ind"] is None for r in rows)
    def tier_name(x):
        return ("none" if x is None else "spirit (<0.15)" if x < 0.15 else "burial spirits (0.15-0.33)" if x < 0.33 else
                "temple powers (0.33-0.53)" if x < 0.53 else "kingship gods (0.53-0.75)" if x < 0.75 else "high god (0.75+)")
    order = ["none", "spirit (<0.15)", "burial spirits (0.15-0.33)", "temple powers (0.33-0.53)", "kingship gods (0.53-0.75)", "high god (0.75+)"]
    cnt = {k: 0 for k in order}
    for r in rows:
        cnt[tier_name(r["lead_ind"])] += 1
    L.append("## Leading god's individuation per culture (the tier it reached)\n")
    L.append("| tier | cultures | share |\n|---|---|---|")
    for k in order:
        L.append(f"| {k} | {cnt[k]} | {100 * cnt[k] / len(rows):.0f}% |")
    L.append(f"\nAll living beings: {len(allind)}; median individuation {np.median(allind):.2f}; {100 * (allind >= 0.5).mean():.0f}% grant spells.\n")
    L.append("## Pantheon size (living beings per culture)\n")
    L.append(f"mean {pan.mean():.1f}, median {np.median(pan):.0f}, min {pan.min()}, max {pan.max()}; cultures with no gods (no spirit ritual): {nog}.\n")
    L.append("| beings | " + " | ".join(str(i) for i in range(0, 16)) + " |\n|" + "---|" * 17)
    L.append("| cultures | " + " | ".join(str(int((pan == i).sum())) for i in range(0, 16)) + " |\n")
    L.append("## Taboos per culture\n")
    L.append(f"mean {tab.mean():.1f}, median {np.median(tab):.0f}, min {tab.min()}, max {tab.max()}.\n")
    kinds: dict = {}
    for r in rows:
        for k, v in r["kinds"].items():
            kinds.setdefault(k, []).append(v)
    L.append("| kind | cultures with one | share | rules in all |\n|---|---|---|---|")
    for k, v in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
        L.append(f"| {k} | {len(v)} | {100 * len(v) / len(rows):.0f}% | {sum(v)} |")
    # faiths
    L.append("\n## Faiths\n")
    L.append("| run | tree | cultures | faiths ever | living | founded | schisms | conversions | died out with no followers | largest now (cultures) |\n|---|---|---|---|---|---|---|---|---|---|")
    fsizes = []
    for rid, tree, sm, frs in per:
        fs = sm.get("faiths") or {}
        liv = [f for f in frs if f["ended_kyr"] is None]
        fsizes += [len(f["cultures_now"]) for f in liv]
        big = max((len(f["cultures_now"]) for f in liv), default=0)
        L.append(f"| {rid} | {tree} | {sum(r['run'] == rid for r in rows)} | {len(frs)} | {len(liv)} | {fs.get('founded', 0)} | {fs.get('schisms', 0)} | "
                 f"{fs.get('conversions', 0)} | {sum(f['end'] == 'no followers left' for f in frs)} | {big} |")
    fsizes = np.array(fsizes or [0])
    L.append(f"\nLiving faiths hold {fsizes.mean():.1f} cultures on average (median {np.median(fsizes):.0f}, max {fsizes.max()}).\n")
    # odd cases
    L.append("## Odd cases\n")
    oddc = []
    for r in rows:
        if r["lead_ind"] is not None and r["pantheon"] >= 14:
            oddc.append(f"- full pantheon (15): {r['culture']} ({r['run']})")
        if r["taboos"] == 0:
            oddc.append(f"- no taboos at all: {r['culture']} ({r['run']})")
        if r["spells"] >= 3:
            oddc.append(f"- three or more spell-granting gods: {r['culture']} ({r['spells']}, {r['run']})")
    for rid, tree, sm, frs in per:
        for f in frs:
            if f["ended_kyr"] is None and len(f["peoples_now"]) >= 3:
                oddc.append(f"- a faith across {len(f['peoples_now'])} peoples: {f['name']} ({rid})")
    L.append("\n".join(oddc[:40]) + (f"\n- ... and {len(oddc) - 40} more" if len(oddc) > 40 else "") + "\n" if oddc else "None found.\n")
    if png:
        _charts(png, lead, pan, tab, kinds, len(rows), fsizes)
        L.append("Charts: `religion_stats_individuation.png`, `religion_stats_pantheon.png`, `religion_stats_taboos.png`.\n")
    txt = "\n".join(L)
    if md:
        md.write_text(txt)
    (out / "report.md").write_text(txt)
    return txt


def _charts(png: Path, lead, pan, tab, kinds, n, fsizes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    png.mkdir(parents=True, exist_ok=True)
    col = "#4a7fb5"
    for name, vals, bins, xl in (("individuation", lead, np.linspace(0, 1, 21), "individuation of the culture's leading god"),
                                 ("pantheon", pan, np.arange(-0.5, 16.5, 1), "living gods and spirits per culture"),
                                 ("taboos", tab, np.arange(-0.5, max(int(tab.max()) + 2, 5), 1), "taboos per culture")):
        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=110)
        ax.hist(vals, bins=bins, color=col, edgecolor="white", linewidth=0.6)
        ax.set_xlabel(xl)
        ax.set_ylabel("cultures")
        ax.spines[["top", "right"]].set_visible(False)
        if name == "individuation":
            for x, t in ((0.1, "ritual"), (0.2, "burial"), (0.45, "temples"), (0.6, "kingship"), (0.9, "high god")):
                ax.axvline(x, color="#999", lw=0.7, ls=":")
                ax.text(x, ax.get_ylim()[1] * 0.95, t, rotation=90, va="top", ha="right", fontsize=7, color="#666")
        fig.tight_layout()
        fig.savefig(png / f"religion_stats_{name}.png")
        plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("runs")
    a.add_argument("--out", required=True)
    a.add_argument("--jobs", type=int, default=4)
    a.add_argument("--trees", default="dnd,seven_meals")
    a.add_argument("--seeds", default="1,2,3")
    a.add_argument("--worlds", default=",".join(WORLDS))
    a = sub.add_parser("one")
    a.add_argument("world")
    a.add_argument("tree")
    a.add_argument("seed", type=int)
    a.add_argument("--out", required=True)
    a = sub.add_parser("religion")
    a.add_argument("--out", required=True)
    a.add_argument("--extra", default="")
    a = sub.add_parser("report")
    a.add_argument("--out", required=True)
    a.add_argument("--md", default=None)
    a.add_argument("--png", default=None)
    args = ap.parse_args(argv)
    out = Path(args.out)
    if args.cmd == "runs":
        runs(out, args.jobs, args.trees.split(","), [int(s) for s in args.seeds.split(",")], args.worlds.split(","))
    elif args.cmd == "one":
        print(one(args.world, args.tree, args.seed, out))
    elif args.cmd == "religion":
        religion(out, [x for x in args.extra.split(",") if x])
    else:
        print(report(out, Path(args.md) if args.md else None, Path(args.png) if args.png else None))


if __name__ == "__main__":
    main()
