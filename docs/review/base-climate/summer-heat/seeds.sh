#!/bin/bash
# Lane 121: two L6 seeds, 1 Gyr, main vs the candidate arm, on scratch stores (in-process TUNE: simtune.py).
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l121
CAND="${CAND:-split_lw=1,split_bl_max=4}"
mkdir -p "$S/store_base" "$S/store_cand"
for seed in 1 2; do
  PLANET_DATA="$S/store_base" PYTHONPATH=. uv run python docs/review/base-climate/summer-heat/simtune.py "" \
    simulate --seed "$seed" --level 6 --myr 1000 --threads 4 --name "l121-base-s$seed" > "$S/sim_base_$seed.log" 2>&1 &
  PLANET_DATA="$S/store_cand" PYTHONPATH=. uv run python docs/review/base-climate/summer-heat/simtune.py "$CAND" \
    simulate --seed "$seed" --level 6 --myr 1000 --threads 4 --name "l121-cand-s$seed" > "$S/sim_cand_$seed.log" 2>&1 &
done
wait
