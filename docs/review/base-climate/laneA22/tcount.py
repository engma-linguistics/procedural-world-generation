"""usage (from a tree root, PYTHONPATH=.:tests): tcount.py SRC.pkl [forest,endings]
The tests' own per-seed cases (test_timezoom._forest_case, test_timezoom_cycle._endings_case) on a cached set
of L4 sources (fdiag.py's CACHE.pkl), with seeds.check_rate's table."""
import os
import pickle
import sys

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa: F401
import seeds


def main():
    src = pickle.loads(open(sys.argv[1], "rb").read())
    which = (sys.argv[2] if len(sys.argv) > 2 else "forest,endings").split(",")
    import test_timezoom as A
    import test_timezoom_cycle as B
    for name, case in (("forest", A._forest_case), ("endings", B._endings_case)):
        if name not in which:
            continue
        rows = seeds.run_case(case, src)
        try:
            seeds.check_rate(name, rows)
        except AssertionError:
            print("  -> BAR FAILS")
        print(f"COUNT {name} {sum(p for _, p, _ in rows)} / {len(rows)}", flush=True)


if __name__ == "__main__":
    main()
