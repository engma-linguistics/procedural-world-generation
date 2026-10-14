"""Command line entry point.  Run `uv run python -m planet --help`."""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import re
import socketserver
import webbrowser
from pathlib import Path

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
        print(f"{path.relative_to(W.ROOT)}  [{w['meta']['generated_in_s']}s]  "
              f"land {s['land_pct']}%  landmasses {lm}  peak {s['highest_m']['elevation']} m")


def cmd_show(args):
    w = W.load(args.file)
    print(W.LEGENDS[args.layer])
    print(W.ascii_map(w, args.layer, args.width))


def cmd_simulate(args):
    params = T.make_params(_parse_set(args.set))
    name = args.name or f"seed {args.seed}, level {args.level}"
    out = T.simulate(args.seed, args.level, args.myr, args.dt, args.every, name, params)
    run = json.loads((out / "run.json").read_text())
    kinds = {}
    for e in run["events"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    last = run["frames"][-1]["stats"]
    print(f"{out.relative_to(W.ROOT)}  [{run['meta']['generated_in_s']}s, {len(run['frames'])} keyframes]  "
          f"events {kinds}  final: {last['plates']} plates, land {last['land_pct']}%")


def cmd_slice(args):
    try:
        path = T.slice_world(T.find_run(args.run), args.at, args.erosion, force=args.force)
    except T.ReplayMismatch as e:
        raise SystemExit(f"ERROR: {e}")
    print(path.relative_to(W.ROOT))


def cmd_zoom(args):
    from . import zoom as Z
    out = Z.zoom(args.world, args.lat, args.lon, args.size_km, args.res_km, args.seed, args.iterations)
    m = json.loads((out / "zoom.json").read_text())
    s = m["stats"]
    print(f"{out.relative_to(W.ROOT)}/  [{m['generated_in_s']}s, {m['nx']}x{m['ny']} px @ {m['res_km']:g} km]")
    print(f"  land {s['land_pct']}% (coarse {s['coarse_land_pct']}%, land/sea agreement {s['land_sea_agreement_pct']}%)"
          f"  elevation {s['min_m']:.0f}..{s['max_m']:.0f} m, mean {s['mean_elev_m']:.0f} m"
          f" (coarse {s['coarse_mean_elev_m']:.0f} m)")
    print(f"  biggest river {s['max_discharge_m3s']:.0f} m3/s, {s['lakes']} lakes;"
          f" view: http://127.0.0.1:8765/viewer/zoom.html?id={m['id']}")


def cmd_report(args):
    print(T.report(T.find_run(args.run)).relative_to(W.ROOT))


def cmd_list(args):
    T.update_index()
    W.update_index()
    runs = json.loads((T.RUNS / "index.json").read_text())
    worlds = json.loads((W.WORLDS / "index.json").read_text())
    print("runs:" if runs else "runs: none")
    for r in runs:
        print(f"  {r['id']}  {r['created']}  {r['name']}  ({r['myr']:g} Myr)")
    print("worlds:" if worlds else "worlds: none")
    for w in worlds:
        print(f"  {w['id']}  {w['created']}  {w['name']}")


def cmd_delete(args):
    for ref in args.ids:
        gone = T.delete(ref)
        print(f"{ref}: " + (", ".join(str(p.relative_to(W.ROOT)) for p in gone) if gone else "not found"))


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static files, never cached (runs get regenerated in place), plus
    DELETE /runs/<id> or /worlds/<id> for the viewer's delete button."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_DELETE(self):
        m = re.fullmatch(r"/(runs|worlds)/([0-9a-zA-Z_-]+)", self.path)
        if not m:
            self.send_error(400, "expected /runs/<id> or /worlds/<id>")
            return
        gone = T.delete(m.group(2))
        self.send_response(204 if gone else 404)
        self.end_headers()

    def log_message(self, *a):
        pass


def cmd_serve(args):
    W.update_index()
    T.update_index()
    handler = functools.partial(Handler, directory=str(W.ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://127.0.0.1:{args.port}/viewer/"
        print(f"Viewer at {url}   (Ctrl-C to stop)")
        if not args.no_open:
            webbrowser.open(url)
        httpd.serve_forever()


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
    t.add_argument("--seed", "-s", type=int, default=1)
    t.add_argument("--level", "-l", type=int, default=6,
                   help="grid detail: 5=10k cells (~8 s), 6=41k (~35 s), 7=164k (~4 min)")
    t.add_argument("--myr", type=float, default=500, help="how long to simulate (million years)")
    t.add_argument("--dt", type=float, default=2, help="time step (million years)")
    t.add_argument("--every", type=float, default=4, help="keep a viewer keyframe every N Myr")
    t.add_argument("--name", "-n")
    t.add_argument("--set", nargs="*", metavar="KEY=VALUE",
                   help="tectonics params, e.g. --set n_plates=16 start=scattered")
    t.set_defaults(func=cmd_simulate)

    sl = sub.add_parser("slice", help="replay a run to one moment and build a full world there")
    sl.add_argument("run", help="run id, e.g. a3f9c2 (see `list`)")
    sl.add_argument("--at", type=float, required=True, help="time in Myr")
    sl.add_argument("--erosion", type=float, default=0.3,
                    help="final valley-sharpening pass (erosion already ran during the simulation)")
    sl.add_argument("--force", action="store_true",
                    help="save the world even if the replay doesn't match the run's stored keyframe")
    sl.set_defaults(func=cmd_slice)

    z = sub.add_parser("zoom", help="refine a region of a sliced world to a few km -> zooms/<id>/")
    z.add_argument("world", help="world id, e.g. a3f9c2 (see `list`)")
    z.add_argument("--lat", type=float, required=True, help="centre latitude")
    z.add_argument("--lon", type=float, required=True, help="centre longitude")
    z.add_argument("--size-km", type=float, default=1000, help="side of the square region")
    z.add_argument("--res-km", type=float, default=2, help="pixel size (1000 km / 2 km = 500x500)")
    z.add_argument("--seed", type=int, default=1, help="detail noise variant")
    z.add_argument("--iterations", type=int, default=15, help="drainage-network iterations of the landscape pass")
    z.set_defaults(func=cmd_zoom)

    rp = sub.add_parser("report", help="re-render runs/<name>/run.txt")
    rp.add_argument("run")
    rp.set_defaults(func=cmd_report)

    ls = sub.add_parser("list", help="list runs and worlds with their ids")
    ls.set_defaults(func=cmd_list)

    d = sub.add_parser("delete", help="delete runs or worlds by id")
    d.add_argument("ids", nargs="+")
    d.set_defaults(func=cmd_delete)

    s = sub.add_parser("show", help="print an ASCII map of a saved world")
    s.add_argument("file")
    s.add_argument("--layer", default="biome", choices=list(W.LEGENDS))
    s.add_argument("--width", type=int, default=120)
    s.set_defaults(func=cmd_show)

    v = sub.add_parser("serve", help="open the 3D viewer in a browser")
    v.add_argument("--port", type=int, default=8765)
    v.add_argument("--no-open", action="store_true")
    v.set_defaults(func=cmd_serve)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
