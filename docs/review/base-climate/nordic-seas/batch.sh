#!/bin/bash
# Lane 150: batch.sh FILE -> each line "TAG k=v ..." through sc.sh, all in parallel; prints the results.
D="$(cd "$(dirname "$0")" && pwd)"
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l150
date
tags=()
while read -r tag rest; do
  [ -z "$tag" ] && continue
  tags+=("$tag")
  # shellcheck disable=SC2086
  bash "$D/sc.sh" "$tag" $rest &
done < "$1"
wait
for t in "${tags[@]}"; do
  echo "== $t"
  grep -v "^warn\|^ *If\|Using" "$S/sc_$t.txt"
done
