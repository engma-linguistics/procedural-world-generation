#!/bin/bash
# usage: launch.sh -> v1-finish-9's sweep (PW-806 plants + PW-791 star thermostat on), through tools/ice_diag.py, and
# the two L7 Earth-like makes. Outputs in the session scratchpad pw806/<tag>/seed<N>_L<l>.json.gz.
# At most 6 L6 and 2 L7 jobs at once (two queues).
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/pw806
cd $W
job() {  # level tag seed myr offset
  mkdir -p $V/$2
  NUMBA_NUM_THREADS=5 uv run python tools/ice_diag.py --seed $3 --myr $4 --level $1 --out $V/$2 \
    --set star_thermostat=1 climate_offset=$5 > $V/$2/log_$3.txt 2>&1
}
mk() {  # seed
  mkdir -p $V/make
  NUMBA_NUM_THREADS=5 uv run python -m planet make --preset earthlike --level 7 --seed $1 --zooms 0 \
    --name "v1f9 earthlike seed $1 L7" > $V/make/log_$1.txt 2>&1
}
export -f job mk; export W V
{
  for s in 957317 619496 583167 639472; do echo "6 l6fix $s 1000 0"; done
  for s in 53669 733847 819014 958504; do echo "6 l6c_0 $s 1000 0"; done
  for s in 53669 958504; do echo "6 l6c_m $s 1000 -0.001"; done
  for s in 53669 583167 619496 639472 733847 819014 957317 958504; do echo "6 l6c_p $s 1000 0.001"; done
  for o in 0 0.001 -0.001; do echo "6 g2_eb_$o 12 2000 $o"; done
  for s in 957317 619496 583167 639472; do echo "6 g2_sc0 $s 2000 0"; done
  for s in 11 21; do echo "6 g2_new0 $s 2000 0"; done
  for s in 583167 619496 639472 957317; do echo "6 g2_newp $s 2000 0.001"; done
} | xargs -P 6 -L 1 bash -c 'job "$@"' _ &
L6=$!
{
  echo "mk 11"; echo "mk 21"
  for s in 957317 619496 583167 639472; do echo "job 7 l7_d1 $s 1000 0"; done
  for s in 957317 619496 583167 639472; do echo "job 7 l7_d2 $s 1000 0.001"; done
} | xargs -P 2 -L 1 bash -c '"$@"' _ &
L7=$!
wait $L6 $L7
