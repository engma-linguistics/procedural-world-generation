#!/bin/bash
# usage: lane.sh PREFIX -> the full thermostat-off set as one serial lane: L6 1 Gyr (18), L6 2 Gyr (13), L7 1 Gyr (8).
# Existing result files are skipped (launch.sh). Progress lines go to stdout.
D=$(dirname "$0")
echo "start $(date)"
"$D/launch.sh" l6 1.0 "$1"
echo "l6 done $(date)"
"$D/launch.sh" g2 1.0 "$1"
echo "g2 done $(date)"
"$D/launch.sh" l7 1.0 "$1"
echo "l7 done $(date)"
