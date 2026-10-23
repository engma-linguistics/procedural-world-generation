#!/bin/bash
# lane A22's multi-seed jobs on this tree: fdiag.py (F taken apart) then tcount.py (the forest and endings tests'
# own cases) on seeds 1-24, for the harness's worlds and two null draws (climate_offset +-0.001 C), 4 workers each.
# usage: jobs.sh SCRATCH
W=$(cd "$(dirname "$0")/../../../.." && pwd)
D=$W/docs/review/base-climate/laneA22
S=$1
for job in "0:a22" "0.001:a22_eps" "-0.001:a22_epsm"; do
  IFS=: read -r eps tag <<< "$job"
  (cd "$W" && PW_EPS=$eps PW_SEED_WORKERS=4 PYTHONPATH=.:tests:$D uv run python $D/fdiag.py $S/src_$tag.pkl \
     $D/fdiag_$tag.json > $S/fdiag_$tag.log 2>&1 && \
   PW_SEED_WORKERS=4 PYTHONPATH=.:tests:$D uv run python $D/tcount.py $S/src_$tag.pkl > $D/tcount_$tag.txt \
     2> $S/tcount_$tag.err) &
done
wait
grep -H COUNT $D/tcount_a22*.txt
