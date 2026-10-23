"""Lineages: peoples placed, split and spread across the three time scales.

- recent.py: the recent pass, the last ~30 kyr of a glacial time zoom at century steps
- spec.py: the input (a tree of lines with split times, niches, traits, and soft wishes)
- habitat.py, spread.py: carrying capacity per line and the range dynamics (numba)
- history.py: origins, splits, spread through the run, the time zoom and the recent pass; late mixing
- output.py: the stored result (a run of kind timezoom, meta.phase 'lineages') and its report

Design and decisions: docs/proposals/lineages.md.
"""
