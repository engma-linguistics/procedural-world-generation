#!/bin/bash
# usage: sweeps.sh TAG "SEEDS" TREE... -- health --quick on SEEDS in each tree in turn (8 workers x 3 threads: the
# lane's 24-core cap), reports in $T/h_<tree>_<TAG>/. Trees are directories under $T or absolute paths.
T=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/t1024
tag=$1; seeds=$2; shift 2
for tree in "$@"; do
  name=$(basename $tree)
  case $tree in /*) dir=$tree ;; *) dir=$T/$tree ;; esac
  cd $dir && uv run python tools/health.py --quick --no-determinism --l6 $seeds --workers ${W:-8} --threads ${TH:-3} \
    --out $T/h_${name}_$tag > $T/h_${name}_$tag.log 2>&1
done
