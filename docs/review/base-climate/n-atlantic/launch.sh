#!/bin/bash
# lane 142: launch.sh ROLL... -> both arms (main, cand) through paired.sh into $S/judge, MAXSIM shared (4 x 3 threads)
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l142
P=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aea1a151b68185efa/docs/review/base-climate/v1-finish-16/paired.sh
export MAXSIM=${MAXSIM:-4} THREADS=3
nohup bash "$P" "$S/code/main" "$S/judge" main "$@" >> "$S/launch_main.log" 2>&1 < /dev/null &
sleep 3
nohup bash "$P" "$S/code/cand" "$S/judge" cand "$@" >> "$S/launch_cand.log" 2>&1 < /dev/null &
wait
