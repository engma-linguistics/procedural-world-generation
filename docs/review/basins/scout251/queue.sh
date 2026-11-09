#!/bin/bash
# queue.sh JOBFILE PARALLEL: runs each line of JOBFILE as job.sh's arguments, PARALLEL at a time
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251
cd "${S:?}" || exit 1
xargs -P "$2" -L 1 "${S:?}/job.sh" < "$1"
echo "queue $1 done"
