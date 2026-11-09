"""A synthetic L9 world for the viewer's size tests (PW-1209): an L8 world's layers upsampled onto the L9 grid.

    PLANET_DATA=<scratch data root> uv run python tools/synth_l9_world.py <path of an L8 world .json> [new id]

The icosphere nests: L9 cells 0..655361 are the L8 cells, and every new cell takes the values of an L8 neighbour.
It is the same size and shape as a real L9 world (the same layers, 2.6 M cells), not a real world: use it only to
measure loading. Writes grids/L9.json (if missing) and worlds/<id>.json + worlds/layers/<id>/ under PLANET_DATA.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from planet import store as S  # noqa: E402
from planet.grid import build_grid  # noqa: E402


def main():
    src = Path(sys.argv[1])
    wid = sys.argv[2] if len(sys.argv) > 2 else "l9synth"
    t = time.time()
    head = json.loads(src.read_text())
    if head["meta"]["level"] != 8:
        raise SystemExit("needs an L8 world")
    specs8 = head["layers"]
    base8 = src.parent  # (the specs' files are relative to the world's folder)
    g = build_grid(9)
    print(f"L9 grid: {g.n} cells [{time.time() - t:.0f}s]")
    if not S.grid_path(9).exists():
        S.write_grid(g)
        print(f"wrote {S.grid_path(9)} ({S.grid_path(9).stat().st_size / 1e6:.0f} MB) [{time.time() - t:.0f}s]")
    n8 = int(specs8["elevation"]["shape"][0])
    src_of = np.arange(g.n)
    for j in range(n8, g.n):  # (a new cell: its first L8 neighbour)
        src_of[j] = next(int(k) for k in g.nbr_idx[g.nbr_off[j]:g.nbr_off[j + 1]] if k < n8)
    layers = {}
    for k, s in specs8.items():
        a = S.world_layer_decode(S.read_layer(base8, s, mmap=False), s)
        layers[k] = a[src_of]
    out = S.write_world_layers(wid, layers)
    head.update(id=wid, name=f"synthetic L9 from {head.get('id')}", grid="../grids/L9.json", format="procgen-planet/3")
    head["meta"] = {**head["meta"], "level": 9, "cells": g.n}
    lines = [f"{json.dumps(k)}: {json.dumps(v)}" for k, v in head.items() if k != "layers"]
    lines.append('"layers": {\n' + ",\n".join(f"  {json.dumps(k)}: {json.dumps(v)}" for k, v in out.items()) + "\n}")
    S.write_atomic(S.path_of("world", wid), "{\n" + ",\n".join(lines) + "\n}\n")
    S.update_index("world")
    size = sum((S.worlds_dir() / s["file"]).stat().st_size for s in out.values())
    print(f"world {wid}: {len(out)} layers, {size / 1e6:.0f} MB of layer files [{time.time() - t:.0f}s]")


if __name__ == "__main__":
    main()
