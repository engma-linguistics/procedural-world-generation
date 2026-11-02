#!/bin/bash
# lane 134: launch.sh ONLY ROLL... -> both arms (main, cand) through paired.sh into $S/judge, MAXSIM shared
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l134
P=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a3b436e989c5d461a/docs/review/base-climate/v1-finish-16/paired.sh
ONLY=$1; shift
export MAXSIM=${MAXSIM:-5} THREADS=3 ONLY
nohup bash "$P" "$S/code/main" "$S/judge" main "$@" >> "$S/launch_main.log" 2>&1 < /dev/null &
sleep 3
nohup bash "$P" "$S/code/cand" "$S/judge" cand "$@" >> "$S/launch_cand.log" 2>&1 < /dev/null &
wait
