#!/bin/bash
# usage: paired.sh CODE_DIR PREFIX ROLL... -> v1-finish-16's 18 L6 1 Gyr draws (seeds x climate_offset), each offset
# plus ROLL, from the code in CODE_DIR, through CODE_DIR/tools/ice_diag.py, into l24/judge/<PREFIX>_r<ROLL>_<tag>/.
# Lane 24's own cap: at most MAXSIM (default 12) of its sims at once (counted by out dir), and free -g >= 40 GB.
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a593a386fec489ab4
L=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l24
V=$L/judge; C=$1; PRE=$2; shift 2; MAX=${MAXSIM:-12}
export PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation
cd $W; mkdir -p $V
nsim() { ps -eo args | grep "ice_diag.py" | grep "$L/judge" | grep -v -E "^(\S*/)?uv " | grep -v grep | wc -l; }
pids=()
for R in "$@"; do
  {
    for s in 957317 619496 583167 639472; do echo "l6fix $s 0"; done
    for s in 53669 733847 819014 958504; do echo "l6c_0 $s 0"; done
    for s in 53669 958504; do echo "l6c_m $s -0.001"; done
    for s in 53669 583167 619496 639472 733847 819014 957317 958504; do echo "l6c_p $s 0.001"; done
  } > $V/queue.$PRE.$R
  while read TAG S OFF; do
    O=$V/${PRE}_r${R}_$TAG; mkdir -p $O
    [ -e $O/seed${S}_L6.json.gz ] || [ -e $O/log_$S.txt ] && continue
    while [ $(nsim) -ge $MAX ] || [ $(free -g | awk "/^Mem/{print \$7}") -lt 40 ]; do sleep 20; done
    OO=$(python3 -c "print(round($OFF + $R, 6))")
    echo "$(date +%H:%M) start $PRE r$R $TAG $S offset $OO"
    NUMBA_NUM_THREADS=4 nohup uv run python $C/tools/ice_diag.py --seed $S --myr 1000 --level 6 --out $O \
      --set star_brightening=1.0 climate_offset=$OO > $O/log_$S.txt 2>&1 < /dev/null &
    pids+=($!)
    sleep 8
  done < $V/queue.$PRE.$R
done
for p in "${pids[@]}"; do wait $p; done
echo "$(date +%H:%M) $PRE all done"
