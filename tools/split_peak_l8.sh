#!/bin/bash
# PW-1691 (lane 305): the full L8 measurement of the split peoples run on a 2 Myr time zoom, for an overnight run on a quiet machine.
# December A (run 0b3439) -> 2 Myr time zoom -> finish at the interglacial -> refine to L8 -> `planet lineages <L8> --tree dnd --tries 1`,
# as lane 280 did (docs/review/timezoom/two-myr.md section 2), with /usr/bin/time -v for wall and peak RSS.
#   tools/split_peak_l8.sh <scratch data root>    (the root needs runs/0b3439 and grids/ copied in; never the main checkout's runs/)
# Needs ~48 GB free for the peoples run and ~2 h for the zoom (NUMBA_NUM_THREADS=4).
set -eu
ROOT=${1:?scratch data root}
export PLANET_DATA=$ROOT NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-4}
cap() { systemd-run --user --scope -q -p MemoryMax=$1G -p MemorySwapMax=0 "${@:2}"; }
L=$ROOT/logs; mkdir -p "$L"
cap 16 /usr/bin/time -v uv run python -m planet timezoom 0b3439 --at 1000 --kyr 2000 --name pw1691-tz2000 > "$L/tz.log" 2>&1
tz=$(grep -oE "runs/[0-9a-f]{6}" "$L/tz.log" | tail -1 | cut -d/ -f2)
cap 16 uv run python -m planet finish "$tz" --now interglacial > "$L/finish.log" 2>&1
w=$(grep -oE "worlds/[0-9a-f]{6}" "$L/finish.log" | tail -1 | cut -d/ -f2)
cap 24 /usr/bin/time -v uv run python -m planet refine "$w" --level 8 > "$L/refine.log" 2>&1
r=$(grep -oE "worlds/[0-9a-f]{6}" "$L/refine.log" | tail -1 | cut -d/ -f2)
echo "zoom $tz world $w refined $r"
cap 48 /usr/bin/time -v uv run python -m planet lineages "$r" --tree dnd --tries 1 > "$L/peoples.log" 2>&1
grep -E "Elapsed|Maximum resident|Exit status" "$L/peoples.log"
