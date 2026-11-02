import numpy as np, numba as nb, math
@nb.njit(parallel=True, cache=False)
def k(x, c, e, s):
    for i in nb.prange(x.size):
        c[i] = math.cos(x[i]); e[i] = math.exp(x[i]); s[i] = math.sqrt(abs(x[i]))
rng = np.random.default_rng(1)
x = rng.uniform(-8, 8, 4_000_000)
c = np.empty_like(x); e = np.empty_like(x); s = np.empty_like(x)
k(x, c, e, s)
print("cos diff", (c != np.cos(x)).sum(), "exp diff", (e != np.exp(x)).sum(), "sqrt diff", (s != np.sqrt(abs(x))).sum())
xe = -0.5 * rng.uniform(0, 30, 4_000_000)
print("exp neg", (np.empty(1)).size)
k(xe, c, e, s)
print("exp small diff", (e != np.exp(xe)).sum())
