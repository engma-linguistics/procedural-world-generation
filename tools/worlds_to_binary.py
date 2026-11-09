"""One-off (PW-1209): rewrite worlds saved as one JSON text (format procgen-planet/2) in the binary layer format
(procgen-planet/3: a JSON header plus worlds/layers/<id>/<name>.bin), keeping their ids, so their zooms, names,
highlights and peoples runs stay attached. Lossless: every layer is read back and compared with the JSON's values.

    PLANET_DATA=<data root> uv run python tools/worlds_to_binary.py [world ids...]   (default: every v2 world)

Each world's header is rewritten last (atomically), so a world being converted is never half one format. The planet
package itself reads only the new format; this tool is the one place the old one is read, and can go once the
stored worlds are converted.
"""
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from planet import store as S  # noqa: E402


def convert(path) -> tuple[int, int]:
    """Converts one world file in place; returns (bytes before, bytes after)."""
    head, layers, before = [], {}, path.stat().st_size
    with open(path) as fh:
        if fh.readline().strip() != "{":
            raise ValueError(f"{path.name}: not one key per line")
        in_layers = False
        for line in fh:
            if not in_layers:
                if line.startswith('"layers": {'):
                    in_layers = True
                    continue
                head.append(line.rstrip("\n").rstrip(","))
                continue
            m = re.match(r'  "(\w+)": ', line)
            if m:
                layers[m.group(1)] = np.array(json.loads(line[m.end():].rstrip().rstrip(",")))
    parts = [h for h in head if h.strip()]
    hd = json.loads("{" + ",".join(parts) + "}")
    if hd.get("format") != "procgen-planet/2":
        raise ValueError(f"{path.name}: format {hd.get('format')!r}")
    wid = path.stem
    specs = S.write_world_layers(wid, layers)
    back = S.read_world_layers(specs)
    for k, v in layers.items():
        if not np.array_equal(back[k], v) or back[k].dtype.kind != (v.dtype.kind if v.dtype.kind != "u" else "i"):
            raise ValueError(f"{path.name}: layer {k} does not read back the same")
    hd["format"] = "procgen-planet/3"
    lines = [f"{json.dumps(k)}: {json.dumps(v)}" for k, v in hd.items()]
    lines.append('"layers": {\n' + ",\n".join(f"  {json.dumps(k)}: {json.dumps(v)}" for k, v in specs.items()) + "\n}")
    S.write_atomic(path, "{\n" + ",\n".join(lines) + "\n}\n")
    after = path.stat().st_size + sum((S.worlds_dir() / s["file"]).stat().st_size for s in specs.values())
    return before, after


def main():
    ids = sys.argv[1:]
    paths = [S.path_of("world", i) for i in ids] if ids else [
        p for p in sorted(S.worlds_dir().glob("*.json")) if p.name != "index.json"
        and S.read_header(p, ("format",)).get("format") == "procgen-planet/2"]
    for p in paths:
        t = time.time()
        b, a = convert(p)
        print(f"{p.stem}: {b / 1e6:.1f} MB -> {a / 1e6:.1f} MB [{time.time() - t:.1f}s]")
    S.update_index("world")


if __name__ == "__main__":
    main()
