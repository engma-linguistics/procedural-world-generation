"""usage: uv run python tools/yardstick.py FILE_OR_DIR [...] -> the carbon cycle's learnt yardstick and the constant to
re-fit earth.YARDSTICK to (PW-1424 A).

Every run still learns its references over the spin-up (earth.global_temperature, until earth.REF_FREEZE); after it the
sink's reference is the source's over exp(YARDSTICK[level]) instead of the learnt one. The learnt ratio
y = ln(source reference / sink reference) is what YARDSTICK is the mean of: re-fit it, on the paired judge's draws
(docs/review/base-climate/v1-finish-16/paired.sh, 36 L6 runs), whenever a change moves the weathering's or the
outgassing's size (the weathering's factors, the plants' cover, the outgassing's yields). Changes that move only the
climate after the spin-up don't move it.

Reads tools/ice_diag.py outputs (seed*_L*.json.gz; a paired.sh root's arm folders) and fork.py spins (*_at300.json.gz,
which carry the references), and prints per run its level and learnt y, then per level the mean, sd and the current
YARDSTICK. The learnt y comes from the diag record of the step at REF_FREEZE (references(sim) is still the learnt pair
there): ln(source_raw / src) - ln(sink_raw / sink).
Harness only."""
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planet.tectonics import earth  # noqa: E402


def learnt_y(raw: dict) -> float | None:
    """The run's learnt ln(source reference / sink reference), or None (no record at REF_FREEZE)."""
    refs = raw.get("refs") or (raw.get("fork") or {}).get("refs")
    if refs and refs.get("y") is not None:
        return float(refs["y"])
    for r in raw.get("steps", []):
        if abs(r["t"] - earth.REF_FREEZE) < 1e-9 and r.get("src") and r.get("sink"):
            return math.log(r["source_raw"] / r["src"]) - math.log(r["sink_raw"] / r["sink"])
    return None


def files(args) -> list[Path]:
    out = []
    for a in map(Path, args):
        out += sorted(a.rglob("seed*_L*.json.gz")) if a.is_dir() else [a]
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    by = {}
    for p in files(sys.argv[1:]):
        raw = json.loads(gzip.open(p, "rt").read())
        y = learnt_y(raw)
        if y is None:
            continue
        lvl = int(raw["level"])
        by.setdefault(lvl, []).append(y)
        print(f"{p.parent.name}/{p.name}  L{lvl}  y {y:.4f}")
    for lvl, ys in sorted(by.items()):
        ys = np.array(ys)
        sd = float(ys.std(ddof=1)) if len(ys) > 1 else float("nan")
        print(f"L{lvl}: {len(ys)} runs, learnt y mean {ys.mean():.4f} (sd {sd:.4f}, standard error "
              f"{sd / math.sqrt(len(ys)):.4f}); YARDSTICK now {earth.yardstick(lvl):.4f}")


if __name__ == "__main__":
    main()
