"""Relative source/sink (against frozen refs) and implied refs, in windows, from ice_diag json.gz."""
import gzip, json, sys
import numpy as np
for f in sys.argv[1:]:
    st = json.load(gzip.open(f))["steps"]
    g = lambda k: np.array([r[k] for r in st], float)  # noqa: E731
    t, src, sink, rs, rk, dT, ct = g("t"), g("source_raw"), g("sink_raw"), g("src"), g("sink"), g("dT"), g("co2_term")
    print(f.split("/")[-2], f"ref_src {np.median((src / rs)[(t > 300) & (t < 400)]):.0f} ref_sink {np.median((sink / rk)[(t > 300) & (t < 400)]):.1f}")
    for a in [100, 200, 300, 400, 600, 1000, 1500, 1900]:
        m = (t >= a - 50) & (t < a + 50)
        if m.any():
            print(f"  {a:5d} src/ref {rs[m].mean():5.2f} sink/ref {rk[m].mean():5.2f} co2term {ct[m].mean():+6.1f} dT {dT[m].mean():+5.1f}")
