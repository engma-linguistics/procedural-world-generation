#!/bin/bash
# scratch data root of symlinks (read-only) + copied caches; arg: root dir
set -eu
O=/home/daniel/personal/repos/procedural-world-generation
D=$1
mkdir -p "$D/runs" "$D/worlds/goods" "$D/worlds/history" "$D/worlds/names" "$D/.godscache" "$D/zooms"
for r in 1e97dd 3e0eb4 07c755 a24559; do [ -e "$D/runs/$r" ] || ln -s "$O/runs/$r" "$D/runs/$r"; done
for w in 899985 dba204 e9463e; do
  for x in json txt; do [ -e "$D/worlds/$w.$x" ] || ln -s "$O/worlds/$w.$x" "$D/worlds/$w.$x"; done
  [ -e "$D/worlds/history/$w.npz" ] || ln -s "$O/worlds/history/$w.npz" "$D/worlds/history/$w.npz"
  if [ -e "$O/worlds/names/$w.json" ]; then [ -e "$D/worlds/names/$w.json" ] || ln -s "$O/worlds/names/$w.json" "$D/worlds/names/$w.json"; fi
  [ -e "$D/worlds/goods/$w.npz" ] || cp "$O/worlds/goods/$w.npz" "$D/worlds/goods/$w.npz"
done
[ -e "$D/worlds/layers" ] || ln -s "$O/worlds/layers" "$D/worlds/layers"
for f in "$O"/.godscache/gods-*.json "$O"/.godscache/polities-*.json "$O"/.godscache/taboos-*.json; do
  b=$(basename "$f"); [ -e "$D/.godscache/$b" ] || cp "$f" "$D/.godscache/$b"
done
ls -la "$D/runs"
