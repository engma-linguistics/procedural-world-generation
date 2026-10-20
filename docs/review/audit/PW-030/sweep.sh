#!/bin/bash
# usage: sweep.sh KYR "TAG:SRC:k=v ..." ...   SRC: earth | s400 | s580 | s680 | <run_dir>@<myr>; token DT=x shifts dT
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/pw030
R=$S/data/runs
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a805425e08b0cef6d
KYR=$1; shift
export NUMBA_NUM_THREADS=${THREADS:-6}
for job in "$@"; do
  IFS=: read -r tag src args <<< "$job"
  case $src in s400) src=$R/82fc14@400;; s580) src=$R/27ea70@580;; s680) src=$R/82fc14@680;; s300) src=$R/82fc14@280;; esac
  dt=""; rest=""
  for a in $args; do case $a in DT=*) dt=${a#DT=};; *) rest="$rest $a";; esac; done
  DT_SHIFT=$dt uv run python $S/tz_eval.py $tag $src $KYR $rest > $S/out/$tag.log 2>&1 &
done
wait
for job in "$@"; do
  tag=${job%%:*}
  tail -1 $S/out/$tag.log | python3 -c "
import json,sys
d=json.loads(sys.stdin.read())
print('$tag', 'lake %.0f calv %.0f' % (d.get('lake_m',0), d.get('calved_m',0)), 'min %.0f max %.0f swing %.0f mean %.0f' % (d['min'], d['max'], d['swing'], d['mean']), 'at', {k: round(v) for k, v in d['sl_at'].items()},
      'iceland', [round(x,1) for x in d['ice_land_pct_min_max']], 'IG', d['interglacial_ice_land_pct'], 'G', d['glacial_ice_land_pct'],
      'builds', d['builds_kyr'], 'terms', d['terms_kyr'], 'sw', d['cycle_swings_m'], 'P', d['spectrum_top_periods_kyr'][:3], d['power_share'])
" 2>&1 || tail -3 $S/out/$tag.log
done
