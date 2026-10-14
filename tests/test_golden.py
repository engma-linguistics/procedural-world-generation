"""Golden outputs: hashes of what the current code computes for a fixed,
small case. Refactors must leave them unchanged (bit-identical outputs).

A commit that is *meant* to change outputs regenerates them, and the diff of
tests/golden/*.json shows it did:

    uv run pytest tests/test_golden.py --update-golden

Note: the simulation runs the climate model inside its loop, so a climate
change moves both goldens, not only test_golden_climate.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from planet import climate
from planet.grid import build_grid

from conftest import run_sim

GOLDEN = Path(__file__).parent / "golden"


def _h(a) -> str:
    a = np.ascontiguousarray(a)
    return f"{a.dtype.str}{list(a.shape)}:" + hashlib.sha256(a.tobytes()).hexdigest()[:20]


def _hj(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:20]


def _check(request, name: str, got: dict):
    path = GOLDEN / f"{name}.json"
    if request.config.getoption("--update-golden"):
        path.write_text(json.dumps(got, indent=1) + "\n")
        pytest.skip(f"rewrote {path.name}")
    if not path.exists():
        pytest.fail(f"no {path.name}; create it with: uv run pytest tests/test_golden.py --update-golden")
    want = json.loads(path.read_text())
    diff = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
    assert not diff, (f"outputs changed: {diff}. If intended, regenerate with "
                      f"`uv run pytest tests/test_golden.py --update-golden` and commit the json.")


def sim_digest(sim) -> dict:
    snap = sim.snapshot()
    out = {k: _h(getattr(sim, k)) for k in
           ("w_elev", "w_thick", "w_age", "w_cover", "w_rock", "w_cont", "w_extra", "owner", "idx",
            "precip", "temp", "ice", "flow", "down")}
    out.update({f"snap_{k}": _h(getattr(snap, k)) for k in ("elevation", "boundary", "surface", "koppen")})
    out["events"] = _hj([e.as_dict() for e in sim.events])
    out["budget"] = _hj(sim.budget)
    out["scalars"] = _hj([sim.dT, sim.sea_level, sim.drift, sim.co2, int(sim.alive.sum())])
    return out


def test_golden_sim(request):
    """Level 4, seed 1, 60 Myr of tectonics + surface + climate."""
    _check(request, "sim_L4_s1_60myr", sim_digest(run_sim(level=4, seed=1, myr=60)))


def test_golden_climate(request):
    """One climate.compute on a fixed level-4 planet. Expected to move with
    climate-model changes: regenerate with
    `uv run pytest tests/test_golden.py --update-golden`."""
    g = build_grid(4)
    rng = np.random.default_rng(0)
    elev = np.where(rng.random(g.n) < 0.3, rng.uniform(0, 3000, g.n), -3000.0)
    ice = np.where((elev > 0) & (np.abs(g.lat) > 60), 1000.0, 0.0)
    c = climate.compute(g, elev, dT=1.0, tilt=23.4, ice=ice)
    _check(request, "climate_L4", {k: _h(v) for k, v in sorted(c.items()) if isinstance(v, np.ndarray)})
