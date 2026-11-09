#!/bin/bash
# run_all.sh: waits for the machine's 1-min load < 30, then runs l6c.jobs (2 at a time, 2 threads each) beside l7a.jobs
# (1 at a time, 4 threads); after l6c, l7b.jobs (1 at a time, 4 threads). At most 8 cores. Writes run_all.log.
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251
cd "${S:?}" || exit 1
until [ "$(cut -d. -f1 /proc/loadavg)" -lt 30 ]; do sleep 20; done
echo "start $(date +%T) load $(cut -d' ' -f1 /proc/loadavg)"
./queue.sh l7a.jobs 1 > logs/queue_l7a.log 2>&1 &
a=$!
./queue.sh l6c.jobs 2 > logs/queue_l6c.log 2>&1
echo "l6c done $(date +%T)"
until [ "$(cut -d. -f1 /proc/loadavg)" -lt 30 ]; do sleep 20; done
./queue.sh l7b.jobs 1 > logs/queue_l7b.log 2>&1
echo "l7b done $(date +%T)"
wait $a
echo "all done $(date +%T)"
