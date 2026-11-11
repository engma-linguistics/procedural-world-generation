"""Round 25 (lane 281b): states standing at every step from 3,000 years ago, the live polities against the read-out on the same
switch-on history (derive with the live map hidden), and optionally a switch-off run's read-out. Read-only.
argv: on_run_dir [off_run_dir]."""
import sys
from pathlib import Path

from planet.lineages import polities as PO


def counts(D):
    return {round(float(s["ago"]), 3): sum(e[1] in (1, 2) for e in m) for s, m in zip(D["steps"], D["maps"])}


def main(argv):
    on = Path(argv[0])
    live = counts(PO.derive(on))
    off = counts(PO.derive(Path(argv[1]))) if len(argv) > 1 else {}
    _f = PO._from_live
    PO._from_live = None
    _ex = Path.exists
    Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    ro = counts(PO.derive(on))
    Path.exists, PO._from_live = _ex, _f
    agos = [a for a in sorted(live, reverse=True) if a <= 3.0 + 1e-9]
    print("ago   live  readout-on-history  " + ("off" if off else ""))
    tot = {"frame": [0, 0, 0], "between": [0, 0, 0]}
    for a in agos:
        kind = "frame" if round(a * 10) % 5 == 0 else "between"
        t = tot[kind]
        t[0] += live[a]
        t[1] += ro.get(a, 0)
        t[2] += 1
        print(f"{a * 1000:5,.0f} {live[a]:5d} {ro.get(a, 0):5d} {off.get(a, '') if off else ''}  {'(frame step)' if kind == 'frame' else ''}")
    for k, (l, r, n) in tot.items():
        print(f"{k} steps ({n}): live / read-out-on-history {l / max(r, 1):.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
