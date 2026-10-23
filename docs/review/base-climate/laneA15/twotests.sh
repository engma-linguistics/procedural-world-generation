#!/bin/bash
# usage: twotests.sh TREE   (the endings test and the cold-moment test in another tree; prints their numbers)
cd "$1"
uv run pytest -q -s tests/test_timezoom_cycle.py::test_glacials_grow_ice_and_endings_melt_it_fast \
  tests/test_timezoom_consistency.py::test_cold_moment_has_sheets 2>&1 | grep -E "glacial extra|^E  .*assert|passed|failed"
