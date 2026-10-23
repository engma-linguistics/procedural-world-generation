"""usage (from a tree root, PYTHONPATH=.:tests:laneA22): l5scan.py [EPS]
The cold-moment tests' counts (test_timezoom_consistency: plausible seeds of 25-50, sheeted ones, the speeds and
index-zero cases) on this tree, with the L5 runs' climate_offset EPS C (0: the tests' own worlds; a tiny EPS is a
null perturbation: the same physics, another chaotic draw)."""
import os
import sys
import time

os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import planet  # noqa: F401
import seeds


def moment(seed):
    import helpers
    import test_timezoom_consistency as C
    eps = float(os.environ.get("PW_EPS", "0") or 0)
    if eps:
        C.run_sim = lambda **kw: helpers.run_sim(climate_offset=eps, **kw)
    return C._moment(seed)


def main():
    if len(sys.argv) > 1:
        os.environ["PW_EPS"] = sys.argv[1]
    import test_timezoom_consistency as C
    t0 = time.time()
    ms = [(s, m) for s, m in zip(C.SEEDS, seeds.pool_map(moment, C.SEEDS)) if m is not None]
    print("built", round(time.time() - t0), "plausible", [s for s, _ in ms], flush=True)
    for name, case in (("sheets", C._sheets_case), ("speeds", C._speeds_case), ("index0", C._index_zero_case)):
        rows = C._rows(case, ms if name == "sheets" else [(s, m) for s, m in ms if (m[0]["ice"] > 1).mean() > 0.01])
        try:
            seeds.check_rate(name, rows)
        except AssertionError:
            print("  -> BAR FAILS")
        print(f"COUNT {name} {sum(p for _, p, _ in rows)} / {len(rows)}", flush=True)


if __name__ == "__main__":
    sys.modules.setdefault("l5scan", sys.modules["__main__"])
    main()
