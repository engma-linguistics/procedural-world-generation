"""Command line entry point.  Run `uv run python -m planet --help`."""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import socketserver
import webbrowser

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


def cmd_serve(args):
    W.update_index()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(W.ROOT))
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

    g = sub.add_parser("generate", help="make a world (or all three methods with --method all)")
    g.add_argument("--method", "-m", default="all", choices=[*GENERATORS, "all"])
    g.add_argument("--seed", "-s", type=int, default=1)
    g.add_argument("--level", "-l", type=int, default=5,
                   help="grid detail: 4=2.5k cells, 5=10k, 6=41k, 7=164k (slow)")
    g.add_argument("--erosion", type=float, default=1.0, help="0 disables river erosion")
    g.add_argument("--name", "-n")
    g.add_argument("--set", nargs="*", metavar="KEY=VALUE",
                   help="generator params, e.g. --set n_plates=8 ocean_fraction=0.5")
    g.set_defaults(func=cmd_generate)

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
