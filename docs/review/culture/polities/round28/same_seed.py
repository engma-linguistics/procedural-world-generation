"""Round 28 (lane 281e): two peoples runs of the same seed, JSON files compared with run ids, timings and dates taken out. Read-only.
argv: run_a run_b. Prints each differing file and the first differing paths (after dropping keys that are timings or ids)."""
import json
import sys
from pathlib import Path

DROP = {"made_s", "tech_s", "secs", "generated_in_s", "created", "id", "dir", "name", "run", "run_id", "elapsed_s", "seconds", "time_s",
        "source"}


def norm(x, a, b):
    if isinstance(x, dict):
        return {k: norm(v, a, b) for k, v in x.items() if k not in DROP and not k.endswith("_s")}
    if isinstance(x, list):
        return [norm(v, a, b) for v in x]
    if isinstance(x, str):
        return x.replace(b, a)
    return x


def diff(x, y, path="", out=None):
    out = [] if out is None else out
    if len(out) > 8:
        return out
    if type(x) is not type(y):
        out.append(path)
    elif isinstance(x, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y:
                out.append(f"{path}.{k}")
            else:
                diff(x[k], y[k], f"{path}.{k}", out)
    elif isinstance(x, list):
        if len(x) != len(y):
            out.append(f"{path}[len]")
        for i, (u, v) in enumerate(zip(x, y)):
            diff(u, v, f"{path}[{i}]", out)
    elif x != y:
        out.append(f"{path}: {str(x)[:60]} / {str(y)[:60]}")
    return out


def main(a, b):
    A, B = Path(a), Path(b)
    for f in sorted(p.name for p in A.iterdir() if p.suffix == ".json"):
        x, y = norm(json.loads((A / f).read_text()), A.name, B.name), norm(json.loads((B / f).read_text()), A.name, B.name)
        d = diff(x, y)
        print(f, "same" if not d else "DIFFERS", *d[:8], sep="\n  " if d else " ")


if __name__ == "__main__":
    main(*sys.argv[1:3])
