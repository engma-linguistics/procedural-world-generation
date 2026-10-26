#!/bin/bash
# usage: launch.sh QUEUE RATE PREFIX -> v1-finish-12 sweeps (PW-865 option C), through tools/ice_diag.py.
# QUEUE: l6 (the 18 L6 1 Gyr seed-draws), l7 (the 8 L7 1 Gyr seed-draws), g2 (the 13 L6 2 Gyr seed-draws).
# RATE: star_brightening. Outputs in the session scratchpad v1f12/<PREFIX>_<tag>/seed<N>_L<l>.json.gz.
# EXTRA (env): more KEY=VALUE params. P6 (env): L6 jobs at once (default 4); L7 runs 2 at once.
# A seed-draw whose result file already exists is skipped (v1-finish-11's thermostat-off draws are copied in).
Q=$1; RATE=$2; PRE=$3
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a509febb63d5ebd7d
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f12
cd $W
job() {  # level tag seed myr offset
  mkdir -p $V/${PRE}_$2
  [ -e $V/${PRE}_$2/seed$3_L$1.json.gz ] && return 0
  NUMBA_NUM_THREADS=5 uv run python tools/ice_diag.py --seed $3 --myr $4 --level $1 --out $V/${PRE}_$2 \
    --set star_brightening=$RATE climate_offset=$5 $EXTRA > $V/${PRE}_$2/log_$3.txt 2>&1
}
export -f job; export W V RATE PRE EXTRA
case $Q in
l6) {
  for s in 957317 619496 583167 639472; do echo "6 l6fix $s 1000 0"; done
  for s in 53669 733847 819014 958504; do echo "6 l6c_0 $s 1000 0"; done
  for s in 53669 958504; do echo "6 l6c_m $s 1000 -0.001"; done
  for s in 53669 583167 619496 639472 733847 819014 957317 958504; do echo "6 l6c_p $s 1000 0.001"; done
} | xargs -P ${P6:-4} -L 1 bash -c 'job "$@"' _ ;;
l7) {
  for s in 957317 619496 583167 639472; do echo "7 l7_d1 $s 1000 0"; done
  for s in 957317 619496 583167 639472; do echo "7 l7_d2 $s 1000 0.001"; done
} | xargs -P 2 -L 1 bash -c 'job "$@"' _ ;;
g2) {
  for o in 0 0.001 -0.001; do echo "6 g2_eb_$o 12 2000 $o"; done
  for s in 957317 619496 583167 639472; do echo "6 g2_sc0 $s 2000 0"; done
  for s in 11 21; do echo "6 g2_new0 $s 2000 0"; done
  for s in 583167 619496 639472 957317; do echo "6 g2_newp $s 2000 0.001"; done
} | xargs -P ${P6:-4} -L 1 bash -c 'job "$@"' _ ;;
esac
