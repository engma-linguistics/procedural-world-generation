"""The language check matrix (PW-1737): the language pass over several peoples runs x seeds at once, one table of every
check per cell and a pass rate per check. Every language lane is accepted on it, not on one draw of one world.

    uv run python -I tools/language/matrix.py --scratch DIR --json m.json --md m.md        # 4 runs x 2 seeds, 4 cells x 4 workers
    uv run python -I tools/language/matrix.py --scratch DIR --from-scratch --json m.json   # re-tabulate finished cells only
    uv run python -I tools/language/matrix.py --compare main.json branch.json               # main against a branch

Each cell runs `planet languages RUN --out DIR/RUN-sSEED --seed S --workers W` (never in place: the runs stay untouched),
under `systemd-run --user --scope -p MemoryMax=...` where systemd-run exists, with $PLANET_DATA pointing at the data root
(a worktree has no runs/ of its own: the main checkout's is used). When a cell is done its table goes to cell.json and its
languages*.json files are deleted (unless --keep): /tmp is RAM. `--code DIR` runs the pass from another checkout (an older
commit, for a before/after on the same cells).

The pass bar (PW-1737, first baseline 2026-11-11): every realism and guard check except the horizon passes in at least
PASS_BAR of the cells; invariants in all of them; the horizon is reported, not barred (owner 11-08)."""
from __future__ import annotations

import argparse
import concurrent.futures as CF
import datetime as dt
import json
import os
import shutil
import statistics as st
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = ("a24559", "de1cc6", "0141d1", "3e0eb4")   # D&D on dba204; Seven Meals on 2762ba (stress); D&D on 899985; D&D on dba204, 2nd draw
SEEDS = ("own", "7919")   # "own" = the run's meta.seed (the pass's default)
PASS_BAR = 0.7            # share of cells each non-horizon realism/guard check must pass (seed-pass-rate convention)
HORIZON = "scholars' horizon (human lects)"
SHORT = {"proto inventories vs PHOIBLE": "proto inventories", "sisters recognisable, distant not": "sisters",
         HORIZON: "horizon", "language shift happened": "shifts", "long generations change less": "long generations",
         "hubs simpler, isolated richer": "hubs", "living inventory sizes vs PHOIBLE": "living sizes",
         "living segment frequencies vs PHOIBLE": "living segments", "overused segments (all living lects)": "overuse",
         "typology agrees with the live grams": "typology", "loans follow borrowability (WOLD)": "WOLD",
         "areal signal (cross-family, near vs far)": "areal", "no impossible segments (all lects)": "impossible segs",
         "second voice only where there is a syrinx; second-voice tone shares": "second voice",
         "loans follow the contact kind": "contact kind", "doublets under elite rule": "doublets",
         "word starts vs NorthEuraLex": "word starts"}
NUMBERS = ("living", "sisters", "pronoun_loans", "horizon_judged", "horizon_2win", "word_starts_off", "simple_syll",
           "back_harmony", "uvular_R")


def data_root(arg: str | None) -> Path:
    """--data, else $PLANET_DATA, else this checkout if it has runs/, else the main checkout of this worktree."""
    for c in (arg, os.environ.get("PLANET_DATA")):
        if c:
            return Path(c).resolve()
    if (REPO / "runs").is_dir():
        return REPO
    common = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    main = (REPO / common).resolve().parent if common else None
    if main and (main / "runs").is_dir():
        return main
    raise SystemExit("no runs/ found: pass --data or set PLANET_DATA")


def commit_of(code: Path) -> str:
    r = subprocess.run(["git", "-C", str(code), "log", "-1", "--format=%h %s"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(code), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
    return r.stdout.strip()[:72] + (" (+uncommitted)" if dirty.stdout.strip() else "")


# ---- one cell -------------------------------------------------------------------------------------------------------------
def summarise(doc: dict) -> dict:
    """The table of one languages.json: every check (pass, kind, short value) and the key numbers."""
    checks = {}
    for c in doc.get("checks") or []:
        checks[c["name"]] = {"pass": bool(c["pass"]), "kind": c.get("kind", "?")}
    by = {c["name"]: c.get("value") or {} for c in doc.get("checks") or []}
    living = [l for l in doc["lects"] if l.get("died_kyr") is None and l.get("deme") is not None]

    def share(pred) -> float:
        return round(sum(1 for l in living if pred(l)) / max(len(living), 1), 3)

    def simple(l) -> bool:   # WALS 12A "simple": (C)V only
        sh = (l.get("inventory") or {}).get("shapes") or {}
        return bool(sh) and all(k in ("V", "CV") for k, w in sh.items() if w)

    def back_harmony(l) -> bool:
        return any(str(c[1]).startswith("harmony.back") for c in l.get("changes") or [])

    hz = by.get(HORIZON) or {}
    ws = by.get("word starts vs NorthEuraLex") or {}
    off = sum(1 for g, v in ws.items() if isinstance(v, dict) and "ref_p10_p50_p90" in v
              and not v["ref_p10_p50_p90"][0] <= v["median"] <= v["ref_p10_p50_p90"][2])
    nums = {"living": len(living),
            "sisters": (by.get("sisters recognisable, distant not") or {}).get("siblings"),
            "pronoun_loans": (by.get("loans follow borrowability (WOLD)") or {}).get("pronoun_loans"),
            "horizon_judged": hz.get("human_judged"), "horizon_2win": hz.get("human"),
            "horizon_logistic": hz.get("human_logistic"), "horizon_smoothed": hz.get("human_smoothed"),
            "word_starts_off": off,
            "simple_syll": share(simple), "back_harmony": share(back_harmony),
            "uvular_R": share(lambda l: "ʁ" in ((l.get("inventory") or {}).get("consonants") or [])),
            "overused": sorted((by.get("overused segments (all living lects)") or {}).get("overused") or {})}
    return {"seed": doc.get("seed"), "checks": checks, "numbers": nums}


def run_cell(run: str, seed: str, a, root: Path) -> dict:
    name = f"{run}-s{seed}"
    out = Path(a.scratch) / name
    done = out / "cell.json"
    if done.exists():
        return json.loads(done.read_text())
    if a.from_scratch and not (out / run / "languages.json").exists():
        return {"run": run, "seed_arg": seed, "cell": name, "error": "not run"}
    if not (out / run / "languages.json").exists():
        out.mkdir(parents=True, exist_ok=True)
        cmd = ["uv", "run", "python", "-m", "planet", "languages", run, "--out", str(out), "--workers", str(a.workers)]
        if seed != "own":
            cmd += ["--seed", seed]
        if shutil.which("systemd-run") and a.memory_max:
            cmd = ["systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={a.memory_max}"] + cmd
        t = time.time()
        with open(out / "pass.log", "w") as log:
            rc = subprocess.run(cmd, cwd=a.code, env={**os.environ, "PLANET_DATA": str(root)}, stdout=log,
                                stderr=subprocess.STDOUT).returncode
        print(f"  {name}: exit {rc} after {time.time() - t:.0f} s", flush=True)
        if rc or not (out / run / "languages.json").exists():
            return {"run": run, "seed_arg": seed, "cell": name, "error": f"exit {rc}; see {out / 'pass.log'}"}
    doc = json.loads((out / run / "languages.json").read_text(encoding="utf-8"))
    cell = {"run": run, "seed_arg": seed, "cell": name, **summarise(doc)}
    done.write_text(json.dumps(cell, ensure_ascii=False, indent=1))
    if not a.keep:
        for f in (out / run).glob("languages*.json"):
            f.unlink()
    return cell


# ---- the table --------------------------------------------------------------------------------------------------------------
def rates(cells: list[dict]) -> dict:
    ok = [c for c in cells if "checks" in c]
    names = list(dict.fromkeys(n for c in ok for n in c["checks"]))
    out = {}
    for n in names:
        v = [c["checks"][n]["pass"] for c in ok if n in c["checks"]]
        kind = next(c["checks"][n].get("kind", "?") for c in ok if n in c["checks"])
        out[n] = {"rate": round(sum(v) / len(v), 3), "cells": len(v), "kind": kind}
    return out


def verdict(rt: dict, bar: float) -> dict:
    """The lane bar: invariants in every cell, other non-horizon checks in >= bar of the cells; the horizon reported."""
    fails = []
    for n, r in rt.items():
        if n == HORIZON:
            continue
        need = 1.0 if r["kind"] == "invariant" else bar
        if r["rate"] < need - 1e-9:
            fails.append(SHORT.get(n, n))
    return {"bar": bar, "pass": not fails, "below_bar": fails}


def table_md(m: dict) -> str:
    cells = [c for c in m["cells"] if "checks" in c]
    L = [f"## Language check matrix: {m['meta']['code']}", "",
         f"{m['meta']['date']}; {len(cells)} cells ({', '.join(m['meta']['runs'])} x seeds {', '.join(m['meta']['seeds'])}), "
         f"{m['meta']['workers']} workers each. Bar: non-horizon checks pass in >= {m['verdict']['bar']:.0%} of cells, "
         f"invariants in all; verdict: **{'PASS' if m['verdict']['pass'] else 'below bar: ' + ', '.join(m['verdict']['below_bar'])}**", ""]
    bad = [c for c in m["cells"] if "checks" not in c]
    if bad:
        L += [f"cells without output: {', '.join(c['cell'] + ' (' + c.get('error', '') + ')' for c in bad)}", ""]
    L.append("| check | kind | " + " | ".join(c["cell"] for c in cells) + " | pass rate |")
    L.append("|---|---|" + "---|" * len(cells) + "---|")
    for n, r in m["rates"].items():
        L.append(f"| {SHORT.get(n, n)} | {r['kind']} | " + " | ".join(
            ("ok" if c["checks"][n]["pass"] else "**F**") if n in c["checks"] else "-" for c in cells) + f" | {r['rate']:.0%} |")
    L += ["", "| cell | seed | " + " | ".join(NUMBERS) + " | overused |", "|---|---|" + "---|" * (len(NUMBERS) + 1)]
    for c in cells:
        nb = c["numbers"]
        L.append(f"| {c['cell']} | {c['seed']} | " + " | ".join("-" if nb.get(k) is None else f"{nb[k]:g}" for k in NUMBERS)
                 + f" | {' '.join(nb.get('overused') or []) or '-'} |")
    L += ["", "sisters = strict cognate share of lects parted <= 2 kyr (bar > 0.5); horizon_judged = logistic (else smoothed) "
          "human reading, kyr; horizon_2win = the two-window read; word_starts_off = start classes outside NorthEuraLex p10-p90; "
          "simple_syll = living lects with (C)V syllables only (WALS 12A: ~12%); back_harmony = living lects that fired "
          "harmony.back; uvular_R = living lects with ʁ."]
    return "\n".join(L) + "\n"


def compare(a: dict, b: dict) -> str:
    """Pass rates and per-world median key numbers, A against B."""
    L = [f"## Matrix compare: A = {a['meta']['code']}  vs  B = {b['meta']['code']}", "",
         f"verdict A: {'PASS' if a['verdict']['pass'] else 'below: ' + ', '.join(a['verdict']['below_bar'])}; "
         f"B: {'PASS' if b['verdict']['pass'] else 'below: ' + ', '.join(b['verdict']['below_bar'])}", "",
         "| check | kind | A | B | change |", "|---|---|---|---|---|"]
    for n in dict.fromkeys(list(a["rates"]) + list(b["rates"])):
        ra, rb = a["rates"].get(n), b["rates"].get(n)
        d = "" if not (ra and rb) or ra["rate"] == rb["rate"] else ("better" if rb["rate"] > ra["rate"] else "**worse**")
        L.append(f"| {SHORT.get(n, n)} | {(ra or rb)['kind']} | {ra['rate']:.0%} | {rb['rate']:.0%} | {d} |" if ra and rb else
                 f"| {SHORT.get(n, n)} | {(ra or rb)['kind']} | {ra and format(ra['rate'], '.0%') or '-'} | "
                 f"{rb and format(rb['rate'], '.0%') or '-'} | |")
    keyed = {c["cell"]: c for c in b["cells"] if "numbers" in c}
    L += ["", "| cell | " + " | ".join(f"{k} A>B" for k in NUMBERS) + " |", "|---|" + "---|" * len(NUMBERS)]
    for c in a["cells"]:
        o = keyed.get(c["cell"])
        if "numbers" not in c or o is None:
            continue
        L.append(f"| {c['cell']} | " + " | ".join(f"{_g(c['numbers'].get(k))}>{_g(o['numbers'].get(k))}" for k in NUMBERS) + " |")
    L += ["", "| median over cells | A | B |", "|---|---|---|"]
    for k in NUMBERS:
        va = [c["numbers"][k] for c in a["cells"] if "numbers" in c and c["numbers"].get(k) is not None]
        vb = [c["numbers"][k] for c in b["cells"] if "numbers" in c and c["numbers"].get(k) is not None]
        L.append(f"| {k} | {_g(st.median(va)) if va else '-'} | {_g(st.median(vb)) if vb else '-'} |")
    return "\n".join(L) + "\n"


def _g(x) -> str:
    return "-" if x is None else f"{x:.3g}" if isinstance(x, float) else str(x)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default=",".join(RUNS), help=f"peoples runs, comma-separated (default {','.join(RUNS)})")
    ap.add_argument("--seeds", default=",".join(SEEDS), help="seeds, comma-separated; 'own' = the run's own (default own,7919)")
    ap.add_argument("--cells", type=int, default=4, help="cells run at once (default 4)")
    ap.add_argument("--workers", type=int, default=4, help="workers per cell (default 4; cells x workers <= the core budget)")
    ap.add_argument("--memory-max", default="24G", help="systemd-run MemoryMax per cell (default 24G; '' = none)")
    ap.add_argument("--scratch", help="folder for the cells' outputs (one subfolder per cell); finished cells are reused")
    ap.add_argument("--code", default=str(REPO), help="checkout to run the pass from (default this one)")
    ap.add_argument("--data", help="data root with runs/ (default $PLANET_DATA, else this or the main checkout)")
    ap.add_argument("--from-scratch", action="store_true", help="only tabulate cells already in --scratch; run nothing")
    ap.add_argument("--keep", action="store_true", help="keep the cells' languages*.json (default: deleted once tabulated)")
    ap.add_argument("--bar", type=float, default=PASS_BAR, help=f"pass bar per check (default {PASS_BAR})")
    ap.add_argument("--json", help="write the matrix here")
    ap.add_argument("--md", help="write the markdown table here (default: print it)")
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"), help="compare two matrix JSONs (A = main, B = the branch)")
    a = ap.parse_args(argv)
    if a.compare:
        text = compare(*(json.loads(Path(p).read_text()) for p in a.compare))
        Path(a.md).write_text(text) if a.md else print(text)
        return 0
    if not a.scratch:
        ap.error("--scratch is required")
    root = data_root(a.data)
    runs, seeds = [r for r in a.runs.split(",") if r], [s for s in a.seeds.split(",") if s]
    for r in runs:
        if not (root / "runs" / r / "demes.json").exists():
            raise SystemExit(f"{r}: not a peoples run under {root / 'runs'}")
    jobs = [(r, s) for r in runs for s in seeds]
    print(f"{len(jobs)} cells, {a.cells} at a time x {a.workers} workers, data {root}, code {a.code}", flush=True)
    with CF.ThreadPoolExecutor(max_workers=max(1, a.cells)) as ex:
        cells = list(ex.map(lambda j: run_cell(j[0], j[1], a, root), jobs))
    rt = rates(cells)
    m = {"meta": {"code": commit_of(Path(a.code)), "date": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "runs": runs,
                  "seeds": seeds, "workers": a.workers},
         "cells": cells, "rates": rt, "verdict": verdict(rt, a.bar)}
    if a.json:
        Path(a.json).write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n")
    text = table_md(m)
    Path(a.md).write_text(text) if a.md else print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
