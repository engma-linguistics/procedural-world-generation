#!/bin/bash
# Lane 126: several ec.sh arms at once: batch.sh TAG "TUNE" EC [TAG "TUNE" EC ...]
cd "$(dirname "$0")" || exit 1
while [ $# -ge 3 ]; do ./ec.sh "$1" "$2" "$3" & shift 3; done
wait
