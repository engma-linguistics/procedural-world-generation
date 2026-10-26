#!/bin/bash
# usage: launch.sh PREFIX -> v1-finish-16's pass-rate set (PW-866): L7 1 Gyr (8 draws) then L6 1 Gyr (18 draws),
# v1-finish-12's seed-draws, through tools/ice_diag.py. Outputs in the session scratchpad v1f16/<PREFIX>_<tag>/.
# Machine-wide cap: a draw starts only while fewer than MAXSIM (default 3) ice_diag/simulate pythons run (any lane).
# A seed-draw whose result file already exists is skipped.
PRE=$1; MAX=${MAXSIM:-3}
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a13c4fec92800aeaf
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f16
cd $W
nsim() { ps -eo args | grep -E "python3? (tools/ice_diag.py|-m planet simulate)" | grep -v -E "^(/home/daniel/.local/bin/)?uv " | grep -v grep | wc -l; }
{
  for s in 957317 619496 583167 639472; do echo "7 l7_d1 $s 0"; done
  for s in 957317 619496 583167 639472; do echo "7 l7_d2 $s 0.001"; done
  for s in 957317 619496 583167 639472; do echo "6 l6fix $s 0"; done
  for s in 53669 733847 819014 958504; do echo "6 l6c_0 $s 0"; done
  for s in 53669 958504; do echo "6 l6c_m $s -0.001"; done
  for s in 53669 583167 619496 639472 733847 819014 957317 958504; do echo "6 l6c_p $s 0.001"; done
} | while read L TAG S OFF; do
  mkdir -p $V/${PRE}_$TAG
  [ -e $V/${PRE}_$TAG/seed${S}_L$L.json.gz ] && continue
  while [ $(nsim) -ge $MAX ]; do sleep 30; done
  echo "$(date +%H:%M) start L$L $TAG $S"
  NUMBA_NUM_THREADS=5 nohup uv run python tools/ice_diag.py --seed $S --myr 1000 --level $L --out $V/${PRE}_$TAG \
    --set star_brightening=1.0 climate_offset=$OFF > $V/${PRE}_$TAG/log_$S.txt 2>&1 &
  sleep 60
done
wait
echo "$(date +%H:%M) all done"
