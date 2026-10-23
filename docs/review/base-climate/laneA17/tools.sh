#!/bin/bash
# usage: tools.sh SUFFIX   (Earth L6: earth_check, climate_bias, lane A15's stage-3 probe p3 and wind table wdiag,
# the boundary-current probe wbc; the overturning on Earth + the 9 stored worlds). 6 processes at once.
cd "$(dirname "$0")/../../../.."
o=docs/review/base-climate/laneA17
uv run python tools/earth_check.py > $o/earth_check_$1.txt 2>&1 &
uv run python tools/climate_bias.py > $o/climate_bias_$1.txt 2>&1 &
uv run python $o/p3.py > $o/p3_$1.txt 2>&1 &
uv run python $o/wdiag.py > $o/wind_$1.txt 2>&1 &
uv run python $o/wbc.py > $o/wbc_$1.txt 2>&1 &
PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation PYTHONPATH=. uv run python tools/overturning_report.py \
  --earth --world 119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf > $o/overturning_$1.txt 2>&1 &
wait
