#!/bin/bash
# scratch data root: symlinks to the owner's runs and worlds (read-only), own .godscache and worlds/goods (copies)
set -eu
O=/home/daniel/personal/repos/procedural-world-generation
D=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l235/data
mkdir -p "$D/runs" "$D/worlds/goods" "$D/worlds/history" "$D/worlds/names" "$D/.godscache" "$D/zooms"
for r in 1e97dd 0141d1 3e0eb4 07c755 a24559; do
  [ -e "$D/runs/$r" ] || ln -s "$O/runs/$r" "$D/runs/$r"
done
for w in 899985 dba204 e9463e; do
  for x in json txt; do [ -e "$D/worlds/$w.$x" ] || ln -s "$O/worlds/$w.$x" "$D/worlds/$w.$x"; done
  [ -e "$D/worlds/history/$w.npz" ] || ln -s "$O/worlds/history/$w.npz" "$D/worlds/history/$w.npz"
  [ -e "$O/worlds/names/$w.json" ] && { [ -e "$D/worlds/names/$w.json" ] || ln -s "$O/worlds/names/$w.json" "$D/worlds/names/$w.json"; }
  [ -e "$D/worlds/goods/$w.npz" ] || cp "$O/worlds/goods/$w.npz" "$D/worlds/goods/$w.npz"
done
[ -e "$D/worlds/layers" ] || ln -s "$O/worlds/layers" "$D/worlds/layers"
for f in "$O"/.godscache/*.json; do b=$(basename "$f"); [ -e "$D/.godscache/$b" ] || cp "$f" "$D/.godscache/$b"; done
ls -la "$D" "$D/runs" "$D/.godscache"
