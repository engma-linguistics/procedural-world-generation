#!/bin/bash
# usage: paired.sh CODE_DIR OUT_ROOT ARM ROLL... -> the paired judge's draws for one arm (PW-994): v1-finish-16's 18 L6
# 1 Gyr seed-draws (seed x climate_offset), each offset plus ROLL, run from the code in CODE_DIR (a frozen copy:
# `git archive <commit> | tar -x -C CODE_DIR`, so later edits don't leak in) through CODE_DIR/tools/ice_diag.py, into
# OUT_ROOT/<ARM>_r<ROLL>_<tag>/. Judge two arms with pjudge.py OUT_ROOT ARM_A ARM_B.
# Rolls: 2 (0.0005 0.001) normally; 4 (add 0.0015 0.002) only when the pass count decides the merge (README).
# Caps: at most MAXSIM (default 10) of this OUT_ROOT's sims at once, and free -g >= MINFREE (default 40) GB.
# A draw whose result or log exists is skipped (delete the log of a draw that died to re-run it).
# PY: the python to run (default: the venv of the checkout this script is in). LEVEL: grid level (default 6);
# ONLY: a regex of the draw tags to run (default all; e.g. ONLY=l6fix for an L7 set of 4 seeds, PW-247).
C=$(realpath "$1"); OUT=$(realpath -m "$2"); ARM=$3; shift 3
MAX=${MAXSIM:-10}; LEVEL=${LEVEL:-6}; ONLY=${ONLY:-.}; MINFREE=${MINFREE:-40}; THREADS=${THREADS:-3}
HERE=$(cd "$(dirname "$0")" && pwd); PY=${PY:-$(cd "$HERE/../../../.." && pwd)/.venv/bin/python}
export PLANET_DATA=${PLANET_DATA:-/home/daniel/personal/repos/procedural-world-generation}
mkdir -p "$OUT"
nsim() { ps -eo args | grep "ice_diag.py" | grep -F -- "--out $OUT/" | grep -v grep | wc -l; }
pids=()
for R in "$@"; do
  while read TAG S OFF; do
    [[ $TAG =~ $ONLY ]] || continue
    O=$OUT/${ARM}_r${R}_$TAG; mkdir -p "$O"
    { [ -e "$O/seed${S}_L${LEVEL}.json.gz" ] || [ -e "$O/log_$S.txt" ]; } && continue
    while [ "$(nsim)" -ge "$MAX" ] || [ "$(free -g | awk '/^Mem/{print $7}')" -lt "$MINFREE" ]; do sleep 20; done
    OO=$(python3 -c "print(round($OFF + $R, 6))")
    echo "$(date +%H:%M) start $ARM r$R $TAG $S offset $OO"
    (cd "$C" && NUMBA_NUM_THREADS=$THREADS nohup "$PY" tools/ice_diag.py --seed "$S" --myr 1000 --level $LEVEL --out "$O/" \
       --set star_brightening=1.0 climate_offset="$OO" > "$O/log_$S.txt" 2>&1 < /dev/null) &
    pids+=($!)
    sleep 5
  done <<'EOF'
l6fix 957317 0
l6fix 619496 0
l6fix 583167 0
l6fix 639472 0
l6c_0 53669 0
l6c_0 733847 0
l6c_0 819014 0
l6c_0 958504 0
l6c_m 53669 -0.001
l6c_m 958504 -0.001
l6c_p 53669 0.001
l6c_p 583167 0.001
l6c_p 619496 0.001
l6c_p 639472 0.001
l6c_p 733847 0.001
l6c_p 819014 0.001
l6c_p 957317 0.001
l6c_p 958504 0.001
EOF
done
for p in "${pids[@]}"; do wait "$p"; done
echo "$(date +%H:%M) $ARM all done"
