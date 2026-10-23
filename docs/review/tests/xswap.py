"""Climate swap over the 24 L4 worlds. usage (from a tree root, PYTHONPATH=.:tests):
  xswap.py dump PKL     the tree's 24 sources -> PKL
  xswap.py run PKL      the forest and endings cases with this tree's climate on PKL's worlds"""
import os
import pickle
import sys

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa: F401
import seeds


def main():
    mode, pkl = sys.argv[1], sys.argv[2]
    if mode == "dump":
        src = list(zip(seeds.SEEDS4, seeds.pool_map(seeds.source4, seeds.SEEDS4)))
        open(pkl, "wb").write(pickle.dumps(src))
        return
    import test_timezoom as A
    import test_timezoom_cycle as B
    src = pickle.loads(open(pkl, "rb").read())
    for name, case in (("forest", A._forest_case), ("endings", B._endings_case)):
        rows = seeds.run_case(case, src)
        print(f"{name}: {sum(p for _, p, _ in rows)} of {len(rows)} pass; fails: {[s for s, p, _ in rows if not p]}", flush=True)


if __name__ == "__main__":
    main()
