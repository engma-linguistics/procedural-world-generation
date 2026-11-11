"""The world catalogue (lane 307): a batch of 2 Gyr, L7, Earth-like worlds that differ by their levers, each made the way the
December candidates were (PW-1437: `planet make --preset earthlike --level 7 --peoples seven_meals`), then summed up in one
table Daniel can pick from. Runs are named "Catalogue <batch>-<nn>", so they show on the viewer's start screen.

    uv run python tools/catalogue.py plan                                  # the configs and the batch plan
    uv run python tools/catalogue.py run --data DIR --out OUT --only 01-06 --cores 24
    uv run python tools/catalogue.py summary --data DIR --out OUT          # summary.md / summary.json / thumbnails

`run` starts up to --jobs configs at once (default: all those picked), each stage of each config in its own
`systemd-run --user --scope -p MemoryMax=<cap> -p MemorySwapMax=0` scope, with NUMBA_NUM_THREADS (and the language pass's
workers) = --cores // jobs, so the batch stays within the core budget. Stages per config, each skipped when its id is already
in OUT/<nn>/state.json (so a re-run resumes):
  make       planet make --preset earthlike --level 7 --myr 2000 --kyr 2000 --seed S --set ... --name "Catalogue B-nn"
             (simulate, time zoom, finished world, highlights, zooms; no peoples: they get their own cap)    cap --mem-gb
  peoples    planet lineages WORLD --tree TREE --tries N --name "Catalogue B-nn TREE"                          cap --peoples-mem-gb
  languages  planet languages PEOPLES --workers T                                                              cap --peoples-mem-gb
  refine     (only with --refine) planet refine WORLD --level 8                                                 cap --mem-gb
A config waits to start until `free` shows --mem-gb + 8 GB available and /tmp has 40 GB free (docs/coordination.md, the
shared-machine rules). Nothing is deleted, ever; every `planet` command writes into --data (PLANET_DATA) only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = 1
MYR, KYR, LEVEL = 2000, 2000, 7
TREE = "seven_meals"  # (PW-1437: the December candidates' tree)

# The twelve configs. Every lever is a tectonics.Params field the run honours (planet/make.py SETTINGS, or --set), each kept
# inside the range the repo's own runs and docs back (the lever table in docs/review/catalogue/plan.md). One lever (or one
# pair) moves per config, so a world that disappoints names its suspect. Every config shares one known risk: 2 Gyr runs sat
# in icebox on L6 (0/13 on the bar, docs/review/base-climate/v1-finish-14, 2026-10-25 code; PW-894 todo), so a batch may
# come out colder than the 1 Gyr candidates. Seeds are fixed so a batch can be re-made exactly.
CONFIGS = [
    {"nn": "01", "seed": 307001, "set": {},
     "what": "the control: today's Earth-like defaults (supercontinent start, 40% continental crust, tilt 23.4, 12 plates)",
     "risk": "none beyond the preset's own: L7 soft pass 5/6 at 1 Gyr (docs/review/v1-cut/final-tally.md); 2 Gyr less tried"},
    {"nn": "02", "seed": 307002, "set": {"start": "scattered"},
     "what": "no supercontinent: continents scattered from the start, so many seas and coasts early and a later assembly",
     "risk": "PW-379 (wontdo): at L6 it stays dispersed with slow plates and an old ocean through 500 Myr; no climate pass rate"},
    {"nn": "03", "seed": 307003, "set": {"continental_fraction": 0.33},
     "what": "a wetter globe: less continental crust (~0.33), more ocean, island-rich, maritime climates",
     "risk": "below the default 0.4; the land share follows the crust only loosely (sea level), so land may land near 25-30%"},
    {"nn": "04", "seed": 307004, "set": {"continental_fraction": 0.48},
     "what": "a land-rich Earth: more continental crust (~0.48), wide interiors, more desert and steppe",
     "risk": "between the default and the land-heavy preset's 0.6; drier interiors could push the dry-land share up"},
    {"nn": "05", "seed": 307005, "set": {"start": "scattered", "continental_fraction": 0.48},
     "what": "scattered and land-rich: many mid-sized continents and long coastlines",
     "risk": "two levers at once (02 and 04 name the suspect if it fails)"},
    {"nn": "06", "seed": 307006, "set": {"tilt": 17.0},
     "what": "low tilt (17 deg): mild seasons, a narrow tropics, polar ice that lingers",
     "risk": "tilt alone is untested (cold preset: 15 with -6 C); with the 2 Gyr icebox risk (PW-894) this is the likeliest to end too icy"},
    {"nn": "07", "seed": 307007, "set": {"tilt": 30.0},
     "what": "high tilt (30 deg): hard winters and hot summers, wide tropics and wide polar circles",
     "risk": "the hothouse preset pairs tilt 45 with +3 C (and reads only +3.5 C); 30 alone is untested"},
    {"nn": "08", "seed": 307008, "set": {"n_plates": 8},
     "what": "few, big plates (8 at the start): large old continents, fewer young mountain belts",
     "risk": "plates rift and weld over 2 Gyr, so the start count may wash out; no repo measure of 8 at L7"},
    {"nn": "09", "seed": 307009, "set": {"n_plates": 18},
     "what": "many small plates (18 at the start): busy margins, island arcs, more young ranges",
     "risk": "rifting stops at 30 plates; no repo measure of 18 at L7"},
    {"nn": "10", "seed": 307010, "set": {"heat_start": 1.5},
     "what": "a hot young mantle (1.5x today's heat at the start): more plumes and faster plates in the first Gyr",
     "risk": "the water-world preset uses 2.0 with a near-empty start; hot sea floor raises the sea early (hot_sea)"},
    {"nn": "11", "seed": 307011, "set": {"climate_offset": 1.5, "tilt": 26.0},
     "what": "a warm Earth (+1.5 C, tilt 26): little ice, wide forests, a long growing season",
     "risk": "no measure of +1.5 alone; the cold, not the warm, side is the 2 Gyr risk (PW-894), so this is the likeliest to pass"},
    {"nn": "12", "seed": 307012, "set": {"star_thermostat": True},
     "what": "the guided star (PW-791): the owner's preferred 'hand of god' dims or brightens the star a little to keep ice ages",
     "risk": "off in every preset today (docs/overview.md); opt-in by owner ruling; bounded to +-4% of the star's output"},
]


def pick(only: str | None) -> list[dict]:
    if not only:
        return CONFIGS
    want = set()
    for part in only.split(","):
        a, _, b = part.partition("-")
        want |= {f"{k:02d}" for k in range(int(a), int(b or a) + 1)}
    return [c for c in CONFIGS if c["nn"] in want]


def name_of(c: dict, batch: int) -> str:
    return f"Catalogue {batch}-{c['nn']}"


def set_args(c: dict) -> list[str]:
    """KEY=VALUE as `planet --set` parses them (JSON values, so True is `true`; a bare word stays a string)."""
    return [f"{k}={v if isinstance(v, str) else json.dumps(v)}" for k, v in c["set"].items()]


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------
def avail_gb() -> float:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 2**20
    return 0.0


def wait_for_room(need_gb: float, log) -> None:
    """Wait (never fail) until `need_gb` + 8 GB is available and /tmp (RAM) keeps 40 GB free."""
    said = False
    while avail_gb() < need_gb + 8 or shutil.disk_usage("/tmp").free / 2**30 < 40:
        if not said:
            log(f"waiting for room: {avail_gb():.0f} GB available, need {need_gb + 8:.0f}")
            said = True
        time.sleep(60)


def capped(cmd: list[str], mem_gb: float, threads: int, data: Path, code: Path, logf: Path) -> tuple[int, str]:
    """One `planet` command in its own memory-capped scope, timed by /usr/bin/time -v; returns (exit, its output)."""
    env = {**os.environ, "PLANET_DATA": str(data), "NUMBA_NUM_THREADS": str(threads)}
    full = ["systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={mem_gb:g}G", "-p", "MemorySwapMax=0",
            "/usr/bin/time", "-v", "uv", "run", "--project", str(code), "python", "-m", "planet", *cmd]
    with open(logf, "a") as f:
        f.write(f"\n$ {' '.join(full)}\n")
        f.flush()
        p = subprocess.run(full, cwd=code, env=env, stdout=f, stderr=subprocess.STDOUT)
    return p.returncode, logf.read_text()


def _time_of(text: str) -> dict:
    """The last /usr/bin/time -v block's wall and peak RSS."""
    wall = re.findall(r"Elapsed \(wall clock\) time.*: ([\d:.]+)", text)
    rss = re.findall(r"Maximum resident set size \(kbytes\): (\d+)", text)
    return {"wall": wall[-1] if wall else None, "peak_gb": round(int(rss[-1]) / 2**20, 1) if rss else None}


def run_config(c: dict, a, threads: int, lock: threading.Lock) -> None:
    d = a.out / c["nn"]
    d.mkdir(parents=True, exist_ok=True)
    sp, logf = d / "state.json", d / "log.txt"
    st = json.loads(sp.read_text()) if sp.exists() else {"nn": c["nn"], "name": name_of(c, a.batch), "config": c, "stages": {}}

    def save():
        sp.write_text(json.dumps(st, indent=1))

    def log(msg):
        with lock:
            print(f"[{time.strftime('%H:%M:%S')}] {c['nn']}: {msg}", flush=True)

    def stage(key, cmd, mem, pattern):
        if st["stages"].get(key, {}).get("id"):
            log(f"{key} already made: {st['stages'][key]['id']}")
            return st["stages"][key]["id"]
        wait_for_room(mem, log)
        log(f"{key} starts")
        t0 = time.time()
        rc, text = capped(cmd, mem, threads, a.data, a.code, logf)
        tail = text[text.rfind("\n$ "):]
        m = pattern(tail)
        st["stages"][key] = {"id": m, "exit": rc, "secs": round(time.time() - t0), **_time_of(tail)}
        save()
        log(f"{key} {'done: ' + str(m) if rc == 0 and m else f'FAILED (exit {rc}), see {logf}'}")
        return m if rc == 0 else None

    def make_ids(t):
        js = [ln for ln in t.splitlines() if ln.startswith("{") and '"world"' in ln]
        if not js:
            return None
        out = json.loads(js[-1])
        st["make"] = out
        return out.get("world")

    world = stage("make", ["make", "--preset", "earthlike", "--level", str(a.level), "--myr", str(a.myr), "--kyr", str(a.kyr),
                           "--seed", str(c["seed"]), "--name", name_of(c, a.batch), "--no-languages",
                           *(["--set", *set_args(c)] if c["set"] else [])], a.mem_gb, make_ids)
    if not world:
        return
    if a.tree:
        ppl = stage("peoples", ["lineages", world, "--tree", a.tree, "--tries", str(a.tries),
                                "--name", f"{name_of(c, a.batch)} {a.tree}"], a.peoples_mem_gb,
                    lambda t: (re.findall(r"runs/([0-9a-f]{6})", t) or [None])[-1])
        if ppl and a.languages:
            stage("languages", ["languages", ppl, "--workers", str(threads)], a.peoples_mem_gb,
                  lambda t: ppl if "Traceback" not in t else None)
    if a.refine:
        stage("refine", ["refine", world, "--level", "8"], a.mem_gb,
              lambda t: (re.findall(r"worlds/([0-9a-f]{6})", t) or [None])[-1])


def cmd_run(a) -> None:
    cs = pick(a.only)
    jobs = min(a.jobs or len(cs), len(cs))
    threads = max(1, a.cores // jobs)
    a.out.mkdir(parents=True, exist_ok=True)
    print(f"{len(cs)} configs, {jobs} at once, {threads} numba threads each ({jobs * threads} of a {a.cores}-core budget); "
          f"data {a.data}, code {a.code}, logs {a.out}", flush=True)
    lock, todo = threading.Lock(), list(cs)
    tlock = threading.Lock()

    def worker():
        while True:
            with tlock:
                if not todo:
                    return
                c = todo.pop(0)
            try:
                run_config(c, a, threads, lock)
            except Exception as e:  # noqa: BLE001 (one config's failure leaves the others running)
                print(f"{c['nn']}: runner error {type(e).__name__}: {e}", flush=True)

    ts = [threading.Thread(target=worker) for _ in range(jobs)]
    for k, t in enumerate(ts):
        t.start()
        time.sleep(a.stagger if k < len(ts) - 1 else 0)  # (staggered starts: the numba caches and the slices don't collide)
    for t in ts:
        t.join()
    print("batch done; next: tools/catalogue.py summary", flush=True)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def summarise(st: dict, out_dir: Path) -> dict:
    sys.path.insert(0, str(ROOT))
    from planet import store as S
    import numpy as np
    row = {"nn": st["nn"], "name": st["name"], "set": st["config"]["set"], "stages": {k: v.get("id") for k, v in st["stages"].items()},
           "cost": {k: {"wall": v.get("wall"), "peak_gb": v.get("peak_gb")} for k, v in st["stages"].items()}}
    mk = st.get("make") or {}
    if mk.get("world"):
        w = json.loads(S.find_world(mk["world"]).read_text())
        sm = w["summary"]
        row["world"] = mk["world"]
        row["land_pct"] = sm.get("land_pct")
        row["landmasses"] = len(sm.get("landmasses") or [])
        row["ice_sheet_land_pct"] = (sm.get("land_biomes_pct") or {}).get("ice sheet", 0.0)
        row["ice_volume_mkm3"] = w["meta"].get("ice_volume_mkm3")
        row["tree_cover_pct"] = sm.get("tree_cover_mean_pct")
        lay = S.world_layers(mk["world"], ["temperature", "elevation"])
        if "temperature" in lay:
            T = np.asarray(lay["temperature"], float)
            row["mean_T_c"] = round(float(T.mean()), 1)  # (icosphere cells are near equal-area)
            land = np.asarray(lay["elevation"], float) > 0
            row["mean_land_T_c"] = round(float(T[land].mean()), 1) if land.any() else None
    if mk.get("run"):
        rd = S.find_run(mk["run"])
        run = json.loads((rd / "run.json").read_text())
        fm = run["meta"].get("finish_moment") or {}
        row["finish_passes"] = fm.get("passes")
        row["finish_why"] = fm.get("why")
        end = run["frames"][-1]["stats"]
        row["end_pco2"] = end.get("pco2")
        try:  # the run's own checks (tools/health.py: the ice-age criteria and icehouse share)
            from tools import health
            ch = health.measure_run(rd)["checks"]
            row["ice_criteria"] = ch.get("ice_new")
            row["icehouse_pct"] = ch.get("icehouse_pct")
            png = out_dir / f"{st['nn']}.png"
            health.thumbnails(rd, png, [run["frames"][-1]["t"]], width=240)
            row["thumb"] = png.name
        except Exception as e:  # noqa: BLE001 (a summary never fails on one measure)
            row["health_error"] = f"{type(e).__name__}: {e}"
    pid = st["stages"].get("peoples", {}).get("id")
    if pid:
        m = json.loads((S.find_run(pid) / "run.json").read_text())["meta"]
        lines = (m.get("present") or {}).get("lines") or {}
        alive = [k for k, v in lines.items() if not v.get("overlay") and (v.get("population") or 0) > 0]
        row["peoples_alive"] = len(alive)
        row["population_m"] = round(sum(lines[k]["population"] for k in alive) / 1e6, 1)
        row["cultures_alive"] = (m.get("cultures") or {}).get("alive")
        row["cities"] = ((m.get("settlements") or {}).get("now") or {}).get("city")
    return row


def cmd_summary(a) -> None:
    os.environ["PLANET_DATA"] = str(a.data)
    rows = []
    for c in CONFIGS:
        sp = a.out / c["nn"] / "state.json"
        if sp.exists():
            rows.append(summarise(json.loads(sp.read_text()), a.out))
    (a.out / "summary.json").write_text(json.dumps(rows, indent=1))
    f = lambda v, nd=1: "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))
    md = ["| # | name | levers | world | land % | mean T (C) | land T (C) | ice sheet % of land | icehouse % | finish | ice criteria | "
          "end pCO2 | peoples alive | cultures | cities | make wall / peak | peoples wall / peak |",
          "|" + "---|" * 17]
    for r in rows:
        lev = ", ".join(f"{k}={v}" for k, v in r["set"].items()) or "defaults"
        cost = lambda k: f"{(r['cost'].get(k) or {}).get('wall') or '-'} / {(r['cost'].get(k) or {}).get('peak_gb') or '-'} GB"
        md.append(f"| {r['nn']} | {r['name']} | {lev} | {r.get('world', '-')} | {f(r.get('land_pct'))} | {f(r.get('mean_T_c'))} | "
                  f"{f(r.get('mean_land_T_c'))} | {f(r.get('ice_sheet_land_pct'))} | {f(r.get('icehouse_pct'))} | "
                  f"{'pass' if r.get('finish_passes') else ('fail' if r.get('finish_passes') is False else '-')} | "
                  f"{r.get('ice_criteria') or '-'} | {f(r.get('end_pco2'), 0)} | {f(r.get('peoples_alive'))} | "
                  f"{f(r.get('cultures_alive'))} | {f(r.get('cities'))} | {cost('make')} | {cost('peoples')} |")
    md.append("")
    md += [f"![{r['nn']}]({r['thumb']})" for r in rows if r.get("thumb")]
    (a.out / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


def cmd_plan(a) -> None:
    cs = pick(a.only)
    for c in cs:
        print(f"{name_of(c, a.batch)}  seed {c['seed']}  {' '.join(set_args(c)) or 'defaults'}\n    {c['what']}\n    risk: {c['risk']}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "run", "summary"):
        p = sub.add_parser(name)
        p.add_argument("--only", help="configs, e.g. 01-06 or 01,03,07-09 (default all)")
        p.add_argument("--batch", type=int, default=BATCH, help="the catalogue's number in the run names")
        if name == "plan":
            continue
        p.add_argument("--data", type=Path, required=True, help="the data root the planet commands write into (PLANET_DATA)")
        p.add_argument("--out", type=Path, required=True, help="logs, per-config state, summary and thumbnails")
        if name == "summary":
            continue
        p.add_argument("--code", type=Path, default=ROOT, help="the checkout whose code runs (default this one)")
        p.add_argument("--jobs", type=int, help="configs at once (default: all picked)")
        p.add_argument("--cores", type=int, default=24, help="core budget for the whole batch (numba threads = cores // jobs)")
        p.add_argument("--mem-gb", type=float, default=24, help="MemoryMax of a make / refine scope")
        p.add_argument("--peoples-mem-gb", type=float, default=32, help="MemoryMax of a peoples / languages scope")
        p.add_argument("--tree", default=TREE, help="peoples tree ('' for none)")
        p.add_argument("--tries", type=int, default=4, help="peoples tries (planet make's default, as December A-C)")
        p.add_argument("--no-languages", dest="languages", action="store_false")
        p.add_argument("--refine", action="store_true", help="also refine each world to L8 (~5 min, ~12 GB each)")
        p.add_argument("--level", type=int, default=LEVEL)
        p.add_argument("--myr", type=float, default=MYR)
        p.add_argument("--kyr", type=float, default=KYR)
        p.add_argument("--stagger", type=float, default=30, help="seconds between the first starts")
    a = ap.parse_args(argv)
    if getattr(a, "data", None):
        a.data, a.out = a.data.resolve(), a.out.resolve()
    if getattr(a, "code", None):
        a.code = a.code.resolve()
    {"plan": cmd_plan, "run": cmd_run, "summary": cmd_summary}[a.cmd](a)


if __name__ == "__main__":
    main()
