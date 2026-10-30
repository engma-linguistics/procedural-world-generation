#!/bin/sh
# sweep.sh: the paired sweep, main (git 29c38f8b) against lane 50 (a copy of the worktree's planet/ and docs/review/megafauna), 6 worlds x
# rolls 7000-7001, at most 6 at a time, 2 numba threads each. Each run saves RUN.npz / ERAS.npz / SERIES.json under ARM/W_R/.
WT=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a37c9a85cd934eafb
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l50
mkdir -p $S/main/src $S/lane/src
[ -d $S/main/src/planet ] || git -C $WT archive 29c38f8b planet docs/review/megafauna | tar -x -C $S/main/src
[ -d $S/lane/src/planet ] || (cd $WT && tar -c planet docs/review/megafauna --exclude=__pycache__ | tar -x -C $S/lane/src)
for arm in ${ARMS:-main lane}; do for w in 2a7385 1df1c3 e71172 6909cb a12762 067778; do for r in 7000 7001; do echo $arm $w $r; done; done; done |
  xargs -P ${PAR:-6} -n 3 sh -c 'cd '$S'/$0/src && PLANET_DATA=/data/personal/repos/procedural-world-generation PYTHONPATH=. NUMBA_NUM_THREADS=2 '$WT'/.venv/bin/python docs/review/megafauna/probe.py $1 $2 '$S'/$0/$1_$2.json --eras 25,10,0 --save '$S'/$0/$1_$2 > '$S'/$0/$1_$2.log 2>&1; echo done $0 $1 $2'
echo sweep finished
