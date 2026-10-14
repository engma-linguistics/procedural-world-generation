"""A Simulation's full state as a plain dict, for checkpoints.

    state = sim.get_state()     # every attribute except the constructor's
    sim.set_state(state)        # the sim takes the dict's arrays over (no copy)
    sim = restore(grid, seed, params, dt, state)   # a sim at the checkpoint, no set-up

A minimal stand-in until tectonics.Simulation has its own documented state
accessor: it introspects the instance (numpy arrays, scalars, the hotspot,
volcano and event lists, dicts), so it captures attributes added later
without a list to keep up to date. The RNG needs no state: step s draws
from default_rng([seed, s]). store.save_checkpoint / load_checkpoint write
the dict to disk; tests/test_store.py checks that resuming from one is
bit-identical to the straight run.
"""

from __future__ import annotations

import copy

from .tectonics import Simulation

# set by the constructor, not part of the evolving state
CONSTRUCTOR = ("grid", "seed", "params", "dt")


def get_state(sim: Simulation) -> dict:
    """A deep copy of everything that evolves (safe to keep while the sim runs on)."""
    return {k: copy.deepcopy(v) for k, v in vars(sim).items() if k not in CONSTRUCTOR}


def set_state(sim: Simulation, state: dict) -> None:
    """Replace the sim's evolving state with `state` (used as is, not copied)."""
    for k in [k for k in vars(sim) if k not in CONSTRUCTOR and k not in state]:
        delattr(sim, k)
    for k, v in state.items():
        setattr(sim, k, v)


def restore(grid, seed: int, params, dt: float, state: dict) -> Simulation:
    """A Simulation at the state's moment, without running the initial set-up."""
    sim = Simulation.__new__(Simulation)
    sim.grid, sim.seed, sim.params, sim.dt = grid, seed, params, dt
    sim.set_state(state)
    return sim


# the interface store.py / timeline.py use (tectonics.py may define its own later)
if not hasattr(Simulation, "get_state"):
    Simulation.get_state = get_state
if not hasattr(Simulation, "set_state"):
    Simulation.set_state = set_state
