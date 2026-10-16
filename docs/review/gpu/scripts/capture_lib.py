import pickle, time
import numpy as np
from planet import climate, timezoom_kernels as TK

saved = set()


def install(outdir, lvl):
    def cap(name, fn):
        def w(*a):
            a_in = [x.copy() if isinstance(x, np.ndarray) else x for x in a]
            t0 = time.perf_counter()
            r = fn(*a)
            dt = time.perf_counter() - t0
            if name not in saved:
                saved.add(name)
                out = r if r is not None else list(a)
                with open(f"{outdir}/{name}_L{lvl}.pkl", "wb") as f:
                    pickle.dump({"args": a_in, "out": out, "cpu_s": dt}, f)
                print("captured", name, round(dt, 3), "s", flush=True)
            return r
        return w
    climate._rain = cap("rain", climate._rain)
    TK.climate_step = cap("climate_step", TK.climate_step)
