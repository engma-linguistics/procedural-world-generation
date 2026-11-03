#!/bin/bash
# usage: paired_fork.sh MAIN_CODE CAND_CODE OUT_ROOT ROLL... -> the forked paired judge (lane 144; optional, not
# adopted: docs/review/base-climate/fork-judge/round1.md). The same draws as paired.sh (v1-finish-16's 18 L6 1 Gyr
# seed-draws, each offset plus ROLL), but each draw's spin-up is run once, with MAIN_CODE, to FORK Myr (default 300 =
# earth.REF_FREEZE: the carbon cycle's references are frozen there), saved, and both arms continue from that same
# state to 1000 Myr: MAIN_ARM with MAIN_CODE, CAND_ARM with CAND_CODE (frozen copies, as paired.sh's). So the arms
# share the yardstick and differ by the change after the fork; the change's effect on the yardstick itself is not in
# it (CAND_SPIN=1 measures that apart). Outputs, in paired.sh's layout (pjudge.py and tools/hard_bar.py read them):
#   OUT_ROOT/<ARM>_r<ROLL>_<tag>/seed<S>_L<lvl>.json.gz (+ log_<S>.txt)
#   OUT_ROOT/fork/r<ROLL>_<tag>/seed<S>_L<lvl>_at<FORK>.ckpt + .json.gz  (main's spin-up; ~0.3 of a run)
#   OUT_ROOT/fork_cand/...  (CAND_SPIN=1: the candidate's own spin-up, for `fork.py yard`; ~0.3 of a run more)
# Judge with pjudge.py OUT_ROOT MAIN_ARM CAND_ARM, as for paired.sh.
# Env: MAIN_ARM (m), CAND_ARM (c); FORK (300); CAND_SET: k=v ... applied to the candidate arm after the fork only;
# CAND_DOFF: added to the candidate's climate_offset after the fork only (default 0; the null check uses 1e-5);
# MAXSIM (default 4): sims of this script at once (a draw takes 2, 3 with CAND_SPIN); MINFREE (40) GB before each
# draw; THREADS (3) numba threads per sim; LEVEL (6); ONLY: a regex on "r<ROLL>_<tag>_<seed>" (default all;
# e.g. ONLY=l6fix, or ONLY='^(r0.001_l6c_p_957317|r0.0005_l6c_0_819014)$'); PY as paired.sh.
# MAIN_FROM=<paired.sh root>/<arm>: take the main arm's result from that unforked paired.sh arm instead of running it
# (the forked main is bit-identical to it when MAIN_CODE and THREADS are the same: round1.md). A draw then runs only
# the candidate after its spin, while MAXSIM still counts 2 per draw: raise MAXSIM to use the idle slot.
# A finished arm (result or log present) or spin (.ckpt present) is skipped; delete a dead draw's logs to re-run it.
MC=$(realpath "$1"); CC=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
MAX=${MAXSIM:-4}; LEVEL=${LEVEL:-6}; ONLY=${ONLY:-.}; MINFREE=${MINFREE:-40}; THREADS=${THREADS:-3}
FORK=${FORK:-300}; MA=${MAIN_ARM:-m}; CA=${CAND_ARM:-c}; DOFF=${CAND_DOFF:-0}; CSPIN=${CAND_SPIN:-0}
HERE=$(cd "$(dirname "$0")" && pwd); PY=${PY:-$(cd "$HERE/../../../.." && pwd)/.venv/bin/python}
F=$HERE/fork.py
export PLANET_DATA=${PLANET_DATA:-/home/daniel/personal/repos/procedural-world-generation}
WIDTH=$((CSPIN ? 3 : 2))
mkdir -p "$OUT"

draw() {  # R TAG S OFF: spin (or reuse), then the two arms (and the candidate's own spin) at once
  local R=$1 TAG=$2 S=$3 OO=$4 D=r$1_$2
  local K=$OUT/fork/$D/seed${S}_L${LEVEL}_at${FORK} KC=$OUT/fork_cand/$D/seed${S}_L${LEVEL}_at${FORK}
  local OC; OC=$(python3 -c "print(round($OO + $DOFF, 9))")
  mkdir -p "$OUT/fork/$D"
  if [ ! -e "$K.ckpt" ]; then
    echo "$(date +%H:%M) spin $D $S offset $OO"
    (cd "$MC" && NUMBA_NUM_THREADS=$THREADS "$PY" "$F" spin "$MC" "$OUT/fork/$D/" --seed "$S" --fork "$FORK" \
       --myr 1000 --level "$LEVEL" --set star_brightening=1.0 climate_offset="$OO" > "$OUT/fork/$D/log_$S.txt" 2>&1 < /dev/null)
  fi
  [ -e "$K.ckpt" ] || { echo "$(date +%H:%M) spin FAILED $D $S (see $OUT/fork/$D/log_$S.txt)"; return; }
  local ps=()
  arm() {  # ARM CODE SETS...
    local A=$1 C=$2; shift 2; local O=$OUT/${A}_${D}
    mkdir -p "$O"
    { [ -e "$O/seed${S}_L${LEVEL}.json.gz" ] || [ -e "$O/log_$S.txt" ]; } && return
    echo "$(date +%H:%M) cont $A $D $S $*"
    (cd "$C" && NUMBA_NUM_THREADS=$THREADS "$PY" "$F" cont "$C" "$K" "$O/" --set "$@" > "$O/log_$S.txt" 2>&1 < /dev/null) &
    ps+=($!)
  }
  local MF=${MAIN_FROM:+${MAIN_FROM}_${D}/seed${S}_L${LEVEL}.json.gz}
  if [ -n "$MF" ] && [ -e "$MF" ] && [ ! -e "$OUT/${MA}_${D}/seed${S}_L${LEVEL}.json.gz" ]; then
    mkdir -p "$OUT/${MA}_${D}" && cp "$MF" "$OUT/${MA}_${D}/" && echo "$(date +%H:%M) main $D $S copied from $MF"
  fi
  arm "$MA" "$MC"
  # shellcheck disable=SC2086  (CAND_SET is a list of k=v words)
  arm "$CA" "$CC" climate_offset="$OC" $CAND_SET
  if [ "$CSPIN" = 1 ] && [ ! -e "$KC.ckpt" ]; then
    mkdir -p "$OUT/fork_cand/$D"
    (cd "$CC" && NUMBA_NUM_THREADS=$THREADS "$PY" "$F" spin "$CC" "$OUT/fork_cand/$D/" --seed "$S" --fork "$FORK" \
       --myr 1000 --level "$LEVEL" --set star_brightening=1.0 climate_offset="$OO" > "$OUT/fork_cand/$D/log_$S.txt" 2>&1 < /dev/null) &
    ps+=($!)
  fi
  for p in "${ps[@]}"; do wait "$p"; done
  echo "$(date +%H:%M) done $D $S"
}

for R in "$@"; do
  while read -r TAG S OFF; do
    [[ r${R}_${TAG}_${S} =~ $ONLY ]] || continue
    while [ $(( $(jobs -rp | wc -l) * WIDTH + WIDTH )) -gt "$MAX" ] && [ "$(jobs -rp | wc -l)" -gt 0 ] \
          || [ "$(free -g | awk '/^Mem/{print $7}')" -lt "$MINFREE" ]; do sleep 20; done
    OO=$(python3 -c "print(round($OFF + $R, 6))")
    draw "$R" "$TAG" "$S" "$OO" &
    sleep 5
  done < <(sed -n "/<<'EOF'/,/^EOF/p" "$HERE/paired.sh" | sed '1d;$d')  # (paired.sh's draws: one list)
done
wait
echo "$(date +%H:%M) $MA / $CA all done"
