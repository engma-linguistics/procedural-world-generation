"""Print source/sink means in windows from ice_diag json.gz files."""
import gzip, json, sys
import numpy as np
for f in sys.argv[1:]:
    d = json.load(gzip.open(f))
    st = d.get("steps") or d.get("temperature") or d
    if isinstance(st, dict):
        keys = [k for k, v in st.items() if isinstance(v, list)]
        st = st[keys[0]] if keys else st
    t = np.array([r["t"] for r in st]); src = np.array([r["source_raw"] for r in st])
    sink = np.array([r["sink_raw"] for r in st]); dT = np.array([r["dT"] for r in st])
    print(f.split("/")[-2])
    for a in [50, 100, 300, 500, 700, 1000, 1500, 1900]:
        m = (t >= a - 50) & (t < a + 50)
        if m.any():
            print(f"  {a:5d}  src {src[m].mean():7.0f}  sink {sink[m].mean():6.1f}  dT {dT[m].mean():+5.1f}")
