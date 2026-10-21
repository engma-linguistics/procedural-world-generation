"""Command line entry point.  Run `uv run python -m planet --help`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import highlights as H
from . import parallel as P
from . import store as S
from . import timeline as T
from . import world as W
from .generators import GENERATORS


def _parse_set(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        try:
            out[k] = json.loads(v)
        except json.JSONDecodeError:
            out[k] = v
    return out


def cmd_generate(args):
    methods = list(GENERATORS) if args.method == "all" else [args.method]
    for method in methods:
        params = _parse_set(args.set)
        w = W.generate(method, seed=args.seed, level=args.level, erosion=args.erosion, **params)
        name = args.name or f"{method}-s{args.seed}-L{args.level}"
        if args.name and len(methods) > 1:
            name = f"{args.name}-{method}"
        path = W.save(w, name)
        s = json.loads(path.read_text())["summary"]
        lm = ", ".join(f"{m['name']}:{m['pct_of_surface']}%" for m in s["landmasses"][:4])
        print(f"{S.rel(path)}  [{w['meta']['generated_in_s']}s]  "
              f"land {s['land_pct']}%  landmasses {lm}  peak {s['highest_m']['elevation']} m")


def cmd_show(args):
    w = W.load(args.file)
    print(W.LEGENDS[args.layer])
    print(W.ascii_map(w, args.layer, args.width))


def cmd_simulate(args):
    if len(args.seed) > 1:  # several runs at once, one worker process each (parallel.simulate_many)
        specs = [{"seed": s, "level": args.level, "myr": args.myr, "dt": args.dt, "every": args.every,
                  "set": _parse_set(args.set), "checkpoint_every": args.checkpoint_every,
                  **({"name": f"{args.name} (seed {s})"} if args.name else {})} for s in args.seed]
        print(f"{len(specs)} runs, {P.default_workers(len(specs)) if not args.jobs else args.jobs} at once...",
              flush=True)
        P.simulate_many(specs, args.jobs, args.threads,
                        on_done=lambda i, rid: _print_run(S.find_run(rid), f"seed {specs[i]['seed']}: "))
        return
    params = T.make_params(_parse_set(args.set))
    name = args.name or f"seed {args.seed[0]}, level {args.level}"
    out = T.simulate(args.seed[0], args.level, args.myr, args.dt, args.every, name, params,
                     checkpoint_every=args.checkpoint_every)
    _print_run(out)


def _print_run(out, prefix=""):
    run = json.loads((out / "run.json").read_text())
    kinds = {}
    for e in run["events"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    last = run["frames"][-1]["stats"]
    print(f"{prefix}{S.rel(out)}  [{run['meta']['generated_in_s']}s, {len(run['frames'])} keyframes]  "
          f"events {kinds}  final: {last['plates']} plates, land {last['land_pct']}%")


def _at(v: str):
    """--at: a time in Myr, or 'auto' for the run's representative moment."""
    if v == "auto":
        return v
    try:
        return float(v)
    except ValueError:
        raise argparse.ArgumentTypeError("a time in Myr, or 'auto'") from None


def _resolve_at(run_dir, at):
    """'auto' -> highlights.representative_time of the run (printed)."""
    if at != "auto":
        return at
    t = H.representative_time(json.loads((Path(run_dir) / "run.json").read_text())["frames"])
    print(f"representative moment: {t:g} Myr", flush=True)
    return t


def cmd_slice(args):
    run_dir = T.find_run(args.run)
    try:
        path = T.slice_world(run_dir, _resolve_at(run_dir, args.at), args.erosion, force=args.force)
    except T.ReplayMismatch as e:
        raise SystemExit(f"ERROR: {e}")
    print(S.rel(path))


def cmd_zoom(args):
    from . import zoom as Z
    kind, _, ref = args.world.rpartition(":")
    if kind == "zoom" or (not kind and S.exists("zoom", ref) and not S.exists("world", ref)):
        return _fine_zoom(args, ref)
    size_km = 1000.0 if args.size_km is None else args.size_km
    res_km = 2.0 if args.res_km is None else args.res_km
    out = Z.zoom(ref, args.lat, args.lon, size_km, res_km, args.seed, args.iterations)
    m = json.loads((out / "zoom.json").read_text())
    s = m["stats"]
    print(f"{S.rel(out)}/  [{m['generated_in_s']}s, {m['nx']}x{m['ny']} px @ {m['res_km']:g} km]")
    print(f"  land {s['land_pct']}% (coarse {s['coarse_land_pct']}%, land/sea agreement {s['land_sea_agreement_pct']}%)"
          f"  elevation {s['min_m']:.0f}..{s['max_m']:.0f} m, mean {s['mean_elev_m']:.0f} m"
          f" (coarse {s['coarse_mean_elev_m']:.0f} m)")
    print(f"  biggest river {s['max_discharge_m3s']:.0f} m3/s, {s['lakes']} lakes;"
          f" view: http://127.0.0.1:8765/viewer/zoom.html?id={m['id']}")
    v = s.get("vegetation") or {}
    if v.get("vegetation_pct"):
        top = ", ".join(f"{k} {p:g}%" for k, p in list(v["vegetation_pct"].items())[:4])
        print(f"  vegetation: {top}; trees {v['tree_cover_mean_pct']}%, wetlands {v['wetland_pct']}% of the land")
    for f in s.get("waterfalls", [])[:3]:
        print(f"  waterfall {f['height_m']:.0f} m over {f['length_km']:g} km, {f['discharge_m3s']:,.0f} m3/s"
              f"{' (lake outlet)' if f['from_lake'] else ''} at {f['lat']:.2f}, {f['lon']:.2f}")


def _fine_zoom(args, parent: str):
    """planet zoom <zoom id>: a fine zoom (zoom_fine, PW-129) of that zoom."""
    from . import zoom_fine as ZF
    out = ZF.zoom(parent, args.lat, args.lon, args.size_km, args.res_km, args.seed)
    m = json.loads((out / "zoom.json").read_text())
    s = m["stats"]
    print(f"{S.rel(out)}/  [{m['generated_in_s']}s, {m['nx']}x{m['ny']} px @ {m['res_km'] * 1000:g} m, "
          f"in zoom {m['parent_zoom']['id']}]")
    print(f"  land {s['land_pct']}%  elevation {s['min_m']:.0f}..{s['max_m']:.0f} m, mean {s['mean_elev_m']:.0f} m "
          f"(parent {s['parent_mean_elev_m']:.0f} m); parent means kept to {s['parent_block_mean_rms_error_m']} m "
          f"rms over 3x3 parent px; view: http://127.0.0.1:8765/viewer/zoom.html?id={m['id']}")
    for f in s["falls"][:3]:
        print(f"  fall {f['height_m']:.0f} m (parent fall {f['parent_fall']}), lip {f['top_m']:.1f} m, "
              f"gorge {f['gorge_km']:g} km, pool {f['plunge_pool_m']:g} m deep")
    for v in s["volcanoes"][:3]:
        print(f"  volcano {v.get('form', '')}: summit {v['top_m']:.0f} m (parent volcano {v['parent_volcano']})")


def cmd_satellite(args):
    """Adds (or redoes) the satellite view of saved worlds and zooms in place."""
    from . import satellite as SAT
    from . import zoom as Z
    for ref in args.ids:
        kind, _, rid = ref.rpartition(":")
        kinds = [kind] if kind else [k for k in S.kinds_of(rid) if k in ("world", "zoom")]
        if len(kinds) != 1:
            raise SystemExit(f"{ref}: {'ambiguous, give world:' + rid + ' or zoom:' + rid if kinds else 'no such world or zoom'}")
        if kinds[0] == "zoom":
            print(S.rel(Z.add_satellite(rid)))
        else:
            path = S.find_world(rid)
            w = W.load(path)
            w["layers"].update(SAT.world_layers(w["grid"], w["layers"], float(w["meta"]["params"].get("tilt", 23.4))))
            print(S.rel(W.save(w, w["name"], rid)))


def cmd_timezoom(args):
    from . import timezoom as TZ
    out = TZ.timezoom(args.run, args.at, args.kyr, args.step, args.every, _parse_set(args.set),
                      level=args.level, name=args.name)
    run = json.loads((out / "run.json").read_text())
    s = [f["stats"] for f in run["frames"]]
    lo = min(s, key=lambda x: x["sea_level_change_m"])
    print(f"{S.rel(out)}  [{run['meta']['generated_in_s']}s, {len(s)} frames]  "
          f"lowest sea level {lo['sea_level_change_m']:+.0f} m at {lo['t']:g} kyr "
          f"(ice {lo['ice_pct']}% of the surface); end {s[-1]['sea_level_change_m']:+.0f} m; "
          f"{len(run['events'])} glacial events")


def cmd_finish(args):
    from . import api, finish as F
    run = S.read_header(S.find_run(args.ref) / "run.json")
    if run.get("kind") == "timezoom":
        if args.at is not None:
            raise SystemExit("--at is for a run; for a time zoom give --kyr")
        path = F.finish_timezoom(args.ref, args.kyr, args.erosion, progress=lambda f, msg: print("  " + msg, flush=True))
    else:
        if args.at is None or args.kyr is not None:
            raise SystemExit("a run is finished at a time: give --at T (Myr, or 'auto'), not --kyr")
        try:
            path = api.slice_run(args.ref, _resolve_at(S.find_run(args.ref), args.at),
                                 lambda f, msg: print("  " + msg, flush=True))
        except api.BadRequest as e:
            raise SystemExit(f"ERROR: {e}")
    m = api.world_header(path)["meta"]
    extra = (f", time zoom {m['timezoom']} @ {m['timezoom_kyr']:g} kyr: sea level {m['sea_level_change_m']:+.0f} m"
             if m.get("timezoom") else "")
    print(f"{S.rel(path)}  ({m.get('source_run')} @ {m.get('t_myr'):g} Myr{extra}; global {m['global_temp_c']} C)"
          f"  view: http://127.0.0.1:8765/viewer/?world={path.name}")


def cmd_export(args):
    from . import export as X
    rng = tuple(args.height_range) if args.height_range else None
    out = X.export(args.ref, args.out, res=args.res, tile=args.tile, overlap=args.overlap, cube=args.cube,
                   raw=args.raw, height_range=rng, river_min=args.river_min, highlights=not args.no_highlights)
    print(out)


def cmd_report(args):
    print(S.rel(T.report(S.find_run(args.run))))


def cmd_list(args):
    runs, worlds, zooms = (S.update_index(k) for k in S.KINDS)
    print("runs:" if runs else "runs: none")
    for r in runs:
        span = (f"time zoom: {r['kyr']:g} kyr after {r['source_run']} @ {r['at_myr']:g} Myr"
                if r.get("kind") == "timezoom" else f"{r['myr']:g} Myr")
        print(f"  {r['id']}  {r['created']}  {r['name']}  ({span})")
    print("worlds:" if worlds else "worlds: none")
    for w in worlds:
        print(f"  {w['id']}  {w['created']}  {w['name']}")
    print("zooms:" if zooms else "zooms: none")
    for z in zooms:
        print(f"  {z['id']}  {z['created']}  {z['name']}")


def cmd_delete(args):
    """ids may say their kind (run:<id>, world:<id>, zoom:<id>); a bare id
    must belong to one kind only."""
    for ref in args.ids:
        kind, _, item_id = ref.rpartition(":")
        kinds = [kind] if kind else S.kinds_of(item_id)
        if kind and kind not in S.KINDS:
            print(f"{ref}: unknown kind {kind!r} (run, world or zoom)")
            continue
        if len(kinds) > 1:
            print(f"{ref}: there is a {' and a '.join(kinds)} with this id; say which, e.g. {kinds[0]}:{item_id}")
            continue
        gone = S.delete(kinds[0], item_id) if kinds else []
        print(f"{ref}: " + (", ".join(S.rel(p) for p in gone) if gone else "not found"))
    if args.orphans:
        gone = S.delete_orphans()
        print("orphans: " + (", ".join(S.rel(p) for p in gone) if gone else "none"))


def cmd_highlights(args):
    from . import api
    if S.exists("run", args.ref):
        run = json.loads((S.find_run(args.ref) / "run.json").read_text())
        at = run["frames"][-1]["t"] if args.at is None else _resolve_at(S.find_run(args.ref), args.at)
        req = {"run": args.ref, "t": at}
    else:
        req = {"world": args.ref}
    try:
        res = api.highlights(req, refresh=args.refresh)
    except api.BadRequest as e:
        raise SystemExit(f"ERROR: {e}")
    src = res["source"]
    where = f"run {src['run']} at {src['t']:g} Myr, " if "run" in src else ""
    print(f"{res['name']}  ({where}world {res['world']}; {len(res['features'])} highlights)")
    for f in res["features"]:
        print(f"{f['rank']:>3}. {f['title']}  ({f['lat']:.2f}, {f['lon']:.2f}; zoom {f['size_km']} km)"
              + (f"  [zoom {f['zoom']}]" if f["zoom"] else ""))
        print(f"     {f['blurb']}")
    if args.zoom:  # the world is sliced already (above): the zooms are independent, several at once
        picks = H.pick_zooms(res["features"], args.zoom)
        jobs = args.jobs or P.default_workers(len(picks))
        print(f"zooming {len(picks)} places, {min(jobs, len(picks))} at once: "
              + "; ".join(f"{f['title']} ({f['size_km']} km)" for f in picks), flush=True)
        P.run(api.zoom_job, [api.zoom_request(src, f) for f in picks], jobs, args.threads,
              on_done=lambda i, r: print(f"zoom {r['zoom']}  {picks[i]['title']}  "
                                         f"-> http://127.0.0.1:8765/viewer/zoom.html?id={r['zoom']}", flush=True))


def cmd_serve(args):
    from .server import serve
    serve(args.port, open_browser=not args.no_open, jobs=args.jobs, threads=args.threads)


def _jobs_args(p, help_jobs: str, default=None):
    p.add_argument("--jobs", "-j", type=int, default=default, metavar="J", help=help_jobs)
    p.add_argument("--threads", type=int, metavar="T",
                   help="numba threads per worker process (default: the cores shared out among them, at most 8)")


def main():
    ap = argparse.ArgumentParser(prog="planet")
    sub = ap.add_subparsers(required=True)

    g = sub.add_parser("generate", help="make a world")
    g.add_argument("--method", "-m", default="plates", choices=[*GENERATORS, "all"])
    g.add_argument("--seed", "-s", type=int, default=1)
    g.add_argument("--level", "-l", type=int, default=5,
                   help="grid detail: 4=2.5k cells, 5=10k, 6=41k, 7=164k (slow)")
    g.add_argument("--erosion", type=float, default=1.0, help="0 disables river erosion")
    g.add_argument("--name", "-n")
    g.add_argument("--set", nargs="*", metavar="KEY=VALUE",
                   help="generator params, e.g. --set n_plates=8 continental_fraction=0.5")
    g.set_defaults(func=cmd_generate)

    t = sub.add_parser("simulate", help="time-stepped plate tectonics -> runs/<id>/")
    t.add_argument("--seed", "-s", type=int, nargs="+", default=[1],
                   help="several seeds: one run each, --jobs at a time in worker processes")
    t.add_argument("--level", "-l", type=int, default=6,
                   help="grid detail: 5=10k cells, 6=41k (~3 min per 500 Myr), 7=164k (~30-40 min per Gyr), "
                        "8=655k (hours); rough times, they vary with load")
    t.add_argument("--myr", type=float, default=500, help="how long to simulate (million years)")
    t.add_argument("--dt", type=float, default=2, help="time step (million years)")
    t.add_argument("--every", type=float, default=4, help="keep a viewer keyframe every N Myr")
    t.add_argument("--checkpoint-every", type=float, default=T.CHECKPOINT_EVERY,
                   help="save the full simulation state every N Myr, so slicing replays from the nearest "
                        "one instead of t=0 (0: none; ~12 MB each at level 6)")
    t.add_argument("--name", "-n")
    t.add_argument("--set", nargs="*", metavar="KEY=VALUE",
                   help="tectonics params, e.g. --set n_plates=16 start=scattered")
    _jobs_args(t, "runs at once with several --seed (default: a quarter of the cores)")
    t.set_defaults(func=cmd_simulate)

    sl = sub.add_parser("slice", help="replay a run to one moment and build a full world there")
    sl.add_argument("run", help="run id, e.g. a3f9c2 (see `list`)")
    sl.add_argument("--at", type=_at, required=True,
                    help="time in Myr, or 'auto': the run's most typical moment after 300 Myr "
                         "(land %%, largest landmass and landmass count nearest their medians)")
    sl.add_argument("--erosion", type=float, default=0.3,
                    help="final valley-sharpening pass (erosion already ran during the simulation)")
    sl.add_argument("--force", action="store_true",
                    help="save the world even if the replay doesn't match the run's stored keyframe")
    sl.set_defaults(func=cmd_slice)

    z = sub.add_parser("zoom", help="refine a region of a sliced world to a few km -> zooms/<id>/; "
                                    "of a zoom: a fine zoom (25-100 m/px) of part of it")
    z.add_argument("world", help="world id, e.g. a3f9c2 (see `list`); or a zoom id (zoom:<id> if a world has it "
                                 "too): a fine zoom nested in that zoom, at most 20x finer")
    z.add_argument("--lat", type=float, required=True, help="centre latitude")
    z.add_argument("--lon", type=float, required=True, help="centre longitude")
    z.add_argument("--size-km", type=float, default=None,
                   help="side of the square region (default 1000; fine zooms: 50 in a zoom, 25 in a fine zoom)")
    z.add_argument("--res-km", type=float, default=None,
                   help="pixel size (default 2: 1000 km / 2 km = 500x500; fine zooms: 0.1 in a zoom, half the "
                        "parent's in a fine zoom; 0.025 with --size-km 25 for 1000 px)")
    z.add_argument("--seed", type=int, default=1, help="detail noise variant")
    z.add_argument("--iterations", type=int, default=15, help="drainage-network iterations of the landscape pass")
    z.set_defaults(func=cmd_zoom)

    sa = sub.add_parser("satellite", help="add or redo the satellite view of saved worlds and zooms (in place)")
    sa.add_argument("ids", nargs="+", help="world or zoom ids (kind:id when ambiguous)")
    sa.set_defaults(func=cmd_satellite)

    h = sub.add_parser("highlights", help="list a world's (or a run's, at --at) most interesting places")
    h.add_argument("ref", help="world id, or run id (then --at; default: the run's end)")
    h.add_argument("--at", type=_at, help="time in Myr for a run, or 'auto' (see slice --at)")
    h.add_argument("--zoom", type=int, default=0, metavar="N", help="also make regional zooms of the top N")
    h.add_argument("--refresh", action="store_true", help="recompute instead of using the cached list")
    _jobs_args(h, "zooms built at once, in worker processes (default: a quarter of the cores, at most N; "
                  "1: one after the other in this process)")
    h.set_defaults(func=cmd_highlights)

    tz = sub.add_parser("timezoom", help="glacial time zoom: ~1 Myr of ice ages from one moment of a run -> runs/<id>/")
    tz.add_argument("run", help="run id (see `list`), or 'earth' for today's Earth (ETOPO1)")
    tz.add_argument("--at", type=float, default=0.0, help="moment of the run, Myr (nearest keyframe)")
    tz.add_argument("--kyr", type=float, default=1000, help="how long to simulate (thousand years)")
    tz.add_argument("--step", type=float, default=0.5, help="time step (kyr)")
    tz.add_argument("--every", type=float, default=2.0, help="keep a viewer frame every N kyr")
    tz.add_argument("--level", "-l", type=int, default=6, help="grid level (earth only; runs use their own)")
    tz.add_argument("--name", "-n")
    tz.add_argument("--set", nargs="*", metavar="KEY=VALUE",
                    help="timezoom.TZParams knobs, e.g. --set insol_k=0.2 phases=zero")
    tz.set_defaults(func=cmd_timezoom)

    fi = sub.add_parser("finish", help="a finished world at one kyr of a glacial time zoom (or at a run time) -> worlds/<id>.json")
    fi.add_argument("ref", help="time zoom id (then --kyr, default its end), or a run id (then --at)")
    fi.add_argument("--kyr", type=float, help="the time zoom's moment, kyr since its start (nearest stored frame)")
    fi.add_argument("--at", type=_at, help="for a run: time in Myr (nearest keyframe), or 'auto'")
    fi.add_argument("--erosion", type=float, default=0.3, help="strength of the final river-carving pass")
    fi.set_defaults(func=cmd_finish)

    ex = sub.add_parser("export", help="export a world or zoom for game engines: 16-bit heightmap tiles, splat and "
                                       "class maps, GeoJSON features, manifest.json -> exports/<id>/")
    ex.add_argument("ref", help="world or zoom id (world:<id> / zoom:<id> when ambiguous)")
    ex.add_argument("--out", "-o", help="output directory (default: <data root>/exports/<id>)")
    ex.add_argument("--res", type=float, help="world: raster width in px (height = width / 2; default 2048); "
                                              "zoom: km per pixel (a multiple of the native one; default native)")
    ex.add_argument("--tile", type=int, default=1024, help="tile size in px (0: one file per layer; default 1024)")
    ex.add_argument("--overlap", type=int, default=0, help="px shared by neighbouring tiles (1 for 2^n+1 terrain tiles)")
    ex.add_argument("--cube", type=int, default=0, metavar="N", help="world: also N x N px on each of 6 cube faces")
    ex.add_argument("--raw", action="store_true", help="heights as raw little-endian .r16 instead of 16-bit PNG")
    ex.add_argument("--height-range", type=float, nargs=2, metavar=("LO", "HI"),
                    help="metres mapped to 0..65535 (default: the data's own range)")
    ex.add_argument("--river-min", type=float, metavar="M3S", help="smallest river kept as a line, m3/s")
    ex.add_argument("--no-highlights", action="store_true", help="leave out the world's highlights (worlds: skips computing them)")
    ex.set_defaults(func=cmd_export)

    rp = sub.add_parser("report", help="re-render runs/<name>/run.txt")
    rp.add_argument("run")
    rp.set_defaults(func=cmd_report)

    ls = sub.add_parser("list", help="list runs, worlds and zooms with their ids")
    ls.set_defaults(func=cmd_list)

    d = sub.add_parser("delete", help="delete runs, worlds or zooms by id (a world takes its zooms with it)")
    d.add_argument("ids", nargs="*", help="ids, or kind:id (run:a3f9c2, world:..., zoom:...) when ambiguous")
    d.add_argument("--orphans", action="store_true", help="also delete zooms and highlight caches of deleted worlds, and unfinished runs")
    d.set_defaults(func=cmd_delete)

    s = sub.add_parser("show", help="print an ASCII map of a saved world")
    s.add_argument("file")
    s.add_argument("--layer", default="biome", choices=list(W.LEGENDS))
    s.add_argument("--width", type=int, default=120)
    s.set_defaults(func=cmd_show)

    v = sub.add_parser("serve", help="open the 3D viewer in a browser")
    v.add_argument("--port", type=int, default=8765)
    v.add_argument("--no-open", action="store_true")
    from .server import JOBS
    _jobs_args(v, f"jobs (zooms, time zooms, finished worlds) run at once, each in a worker process "
                  f"(default {JOBS})", default=JOBS)
    v.set_defaults(func=cmd_serve)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
