#!/bin/bash
# usage: paired.sh CODE_DIR PREFIX ROLL... -> v1-finish-16's 18 L6 1 Gyr draws (seeds x climate_offset), each offset
# plus ROLL (e.g. 0.0005 0.001), from the code in CODE_DIR, through tools/ice_diag.py, into the session scratchpad
# l23/judge/<PREFIX>_r<ROLL>_<tag>/. Tally with docs/review/base-climate/v1-finish-16/fmtally.py.
# Starts a draw only while fewer than MAXSIM (default 8) sims run machine-wide (simulate, ice_diag, riftdiag) and
# free -g shows at least MINFREE (default 40) GB available. Waits for every draw it started.
W=$1; PRE=$2; shift 2; MAX=${MAXSIM:-8}; MINFREE=${MINFREE:-40}
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l23/judge
cd $W; mkdir -p $V
nsim() { ps -eo args | grep -E "python3? (tools/ice_diag.py|-m planet simulate|\S*riftdiag.py|\S*crustdiag.py|\S*diag.py|\S*/wl.py)" | grep -v -E "^(/home/daniel/.local/bin/)?uv " | grep -v grep | wc -l; }
pids=()
for R in "$@"; do
  {
    for s in 957317 619496 583167 639472; do echo "l6fix $s 0"; done
    for s in 53669 733847 819014 958504; do echo "l6c_0 $s 0"; done
    for s in 53669 958504; do echo "l6c_m $s -0.001"; done
    for s in 53669 583167 619496 639472 733847 819014 957317 958504; do echo "l6c_p $s 0.001"; done
  } > $V.queue.$PRE.$R
  while read TAG S OFF; do
    O=$V/${PRE}_r${R}_$TAG; mkdir -p $O
    [ -e $O/seed${S}_L6.json.gz ] || [ -e $O/log_$S.txt ] && continue
    while [ $(nsim) -ge $MAX ] || [ $(free -g | awk "/^Mem/{print \$7}") -lt $MINFREE ]; do sleep 30; done
    OO=$(python3 -c "print(round($OFF + $R, 6))")
    echo "$(date +%H:%M) start $PRE r$R $TAG $S offset $OO"
    NUMBA_NUM_THREADS=5 nohup uv run python /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l23/crustdiag.py --seed $S --myr 1000 --level 6 --out $O \
      --set star_brightening=1.0 climate_offset=$OO > $O/log_$S.txt 2>&1 < /dev/null &
    pids+=($!)
    sleep 45
  done < $V.queue.$PRE.$R
done
for p in "${pids[@]}"; do wait $p; done
echo "$(date +%H:%M) $PRE all done"
