"""usage: scan.py l4 1-12 | l5 25-50   (from a tree root, PYTHONPATH=.:tests)"""
import os, sys, time
os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa
import seeds
def main():
    kind, rng = sys.argv[1], sys.argv[2]
    a, b = map(int, rng.split("-")); S = list(range(a, b + 1))
    t0 = time.time()
    def show(name, rows):
        try: seeds.check_rate(name, rows)
        except AssertionError: print("  -> BAR FAILS")
    if kind == "l4":
        import test_timezoom as A, test_timezoom_cycle as B
        src = list(zip(S, seeds.pool_map(seeds.source4, S))); print("built", time.time() - t0, flush=True)
        show("forest", seeds.run_case(A._forest_case, src)); print("t", time.time() - t0, flush=True)
        show("endings", seeds.run_case(B._endings_case, src)); print("t", time.time() - t0, flush=True)
    else:
        import test_timezoom_consistency as C
        import pickle, pathlib
        cache = pathlib.Path(os.environ.get("SCAN_CACHE", "/nonexistent"))
        if cache.exists():
            ms = pickle.loads(cache.read_bytes())
        else:
            ms = list(zip(S, seeds.pool_map(C._moment, S)))
            if cache.parent.exists(): cache.write_bytes(pickle.dumps(ms))
        print("built", time.time() - t0, flush=True)
        print("plausible:", [s for s, m in ms if m is not None])
        ms = [(s, m) for s, m in ms if m is not None]
        for n, f in (("sheets", C._sheets_case), ("speeds", C._speeds_case), ("index0", C._index_zero_case)):
            show(n, C._rows(f, ms))

if __name__ == "__main__":
    main()
