"""Classify py-spy --native raw samples of the main thread by what the CPU was doing.
python spy.py pyspy.txt [rate_hz]"""
import sys, re
from collections import Counter, defaultdict

fn = sys.argv[1]
rate = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
cls = Counter()
by_py = defaultdict(Counter)
tot = 0
PYF = re.compile(r"^(\S+) \((planet/[^:]+|run_sim\.py|[^)]*\.py):\d+\)$")
for line in open(fn):
    st, n = line.rstrip("\n").rsplit(" ", 1)
    n = int(n)
    fr = st.split(";")[1:]
    libs = [f[f.rfind("(") + 1:-1] if f.endswith(")") else "" for f in fr]
    pyframes = [f for f in fr if PYF.match(f)]
    leaf_py = pyframes[-1] if pyframes else "?"
    leaf_py_fn = re.sub(r":\d+\)", ")", leaf_py)
    j = len(fr) - 1
    leaf = libs[j] if fr else ""
    if any("tbb" in l or "workqueue" in l or "omppool" in l or "gomp" in l for l in libs):
        c = "numba parallel kernel (main thread's share / waiting)"
    elif leaf == "?" or (leaf.startswith(("libm", "libc", "libgcc")) and len(libs) > 1 and libs[j - 1] == "?"):
        c = "numba compiled code (serial kernel or main thread of a parallel one)"
    elif any("_multiarray_umath" in l or "_umath" in l or "linalg" in l or "openblas" in l or "lapack" in l
             or "numpy" in l for l in libs[len(libs) - 12:]):
        c = "numpy (C code: ufuncs, indexing, reductions, copies)"
    elif any("libz" in l or "zlib" in l for l in libs) or any(k in leaf for k in ("write",)):
        c = "I/O and compression"
    elif "python3" in leaf or "libpython" in leaf or leaf.endswith(".py") or PYF.match(fr[-1] if fr else ""):
        c = "python interpreter"
    elif "libc" in leaf or "libm" in leaf or "ld-linux" in leaf:
        c = "libc (malloc/free/memcpy/page faults outside numpy)"
    else:
        c = "other: " + leaf
    cls[c] += n
    by_py[c][leaf_py_fn] += n
    tot += n
print(f"{fn}: {tot} samples = {tot / rate:.1f} s of the main thread")
for c, n in cls.most_common():
    print(f"  {c:<70s} {n / rate:7.1f}s {100 * n / tot:5.1f}%")
    for f, m in by_py[c].most_common(25):
        print(f"      {f:<80s} {m / rate:6.1f}s")
