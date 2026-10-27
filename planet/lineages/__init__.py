"""Lineages: peoples placed, split and spread across the three time scales.

- recent.py: the recent pass, the last ~30 kyr of a glacial time zoom at century steps
- spec.py: the input (a tree of lines with split times, niches, traits, and soft wishes)
- spread.py: the range dynamics (numba); gridops.py: neighbour reductions and distances on the grid, shared
- history/: a package (PW-901), `History` assembled from one mixin per concern: habitat (carrying capacity per line), origins
  (+ portals, groups), competition, dispersal (spread, crossings, refuge), contact (hybrids), peoples, frame, events, steps;
  summary and tries (best of N) at the end. Its __init__ lists the modules.
- output.py: the stored result (a run of kind timezoom, meta.phase 'lineages') and its report

Design and decisions: docs/proposals/lineages.md.
"""
