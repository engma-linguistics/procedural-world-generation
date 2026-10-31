"""Peoples through the three time scales: habitat, origins, spread, competition, late mixing.

Epochs: the source run's keyframes (deep, Myr), the glacial time zoom's frames (kyr),
the recent pass (centuries). Design: docs/proposals/lineages.md.

The package (PW-901; `History` is assembled from one mixin per concern):
  params     the tuning constants
  gridops    neighbour-reduction helpers on the grid
  tags       the place tags of an epoch
  habitat    a line's capacity K, its wishes and goods (HabitatMixin), niche overlap
  pressure   pure competition rules (momentum edge, expansive press, crowding)
  steps      the time steps (deep, glacial, recent)
  origins    where and how a line originates (the landmass draw, founders, splits, arrivals, hybrids)
  portals    the arrivals' portals
  groups     the ways of life within a people
  dispersal  spread, crossings, refuge, the viable-population fade (grid-level movement)
  contact    contact hybrids
  peoples    a people with its groups: whole / rollup / fold / population
  frame      the stored frame of a step
  events     the event log
  model      History: the constructor and the loop
  summary    the present's summary and the wishes' scores
  tries      best-of-N tries (simulate)
"""

from __future__ import annotations

from ...geo import R_KM, is_land  # noqa: F401 (re-exported)
from ..crossing import Crossings, corridor, modes, sea_gap, short_hop  # noqa: F401
from ..spread import EST, graph_dist, nearest_label, rings, rivals_load, spread  # noqa: F401 (re-exported)
from ..gridops import nbr_reduce  # noqa: F401
from .gridops import _csr_gather, _depth, _isin, _soft  # noqa: F401
from .habitat import WAYS, _land_view, capacity, hold_mask, marine_capacity, niche_overlap, same_way  # noqa: F401
from .model import History
from .params import *  # noqa: F401,F403
from .pressure import crowding, expanse_factor, surge, surge_q  # noqa: F401
from .steps import Step  # noqa: F401
from .summary import _niche_closeness, _within, people_rollup, present_summary, wish_scores  # noqa: F401
from .tags import _tags, needs_chains  # noqa: F401
from .tries import simulate  # noqa: F401
