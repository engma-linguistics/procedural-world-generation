#!/bin/bash
# usage: earth.sh <tree> <outdir>  -- Earth L6 bars: earth_check, climate_bias, overturning --earth, lane A18's seabox
set -u
cd "$1"; o=$2; mkdir -p $o
uv run python tools/earth_check.py > $o/earth_check.txt 2>&1 &
uv run python tools/climate_bias.py > $o/climate_bias.txt 2>&1 &
PYTHONPATH=. uv run python tools/overturning_report.py --earth > $o/overturning.txt 2>&1 &
WT="$1" uv run python docs/review/base-climate/laneA18/seabox.py > $o/seabox.txt 2>&1 &
wait
echo "== $o"
grep -h "log-rain correlation" $o/earth_check.txt | sed 's/;.*//'
grep -h "^W Europe  " $o/earth_check.txt | head -1
awk '/^2. Continentality/{f=1} f && /^S +0-150/{print "SH coastal 0-150:", $0; exit}' $o/climate_bias.txt
grep -h "North Sea 51-58" $o/seabox.txt | head -1
grep -h "NH sinking\|Norwegian coast" $o/overturning.txt | head -2
grep -h "^Earth\|^ *W Europe\|warmest bias, summer\|W Europe" $o/climate_bias.txt | head -3
