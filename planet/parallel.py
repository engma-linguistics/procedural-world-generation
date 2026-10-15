"""Concurrency from separate processes, not threads in one process.

A run, a zoom or a slice is dominated by serial Python/numpy work: one L6
100 Myr run takes 45.7 s at NUMBA_NUM_THREADS=4 and 39-40 s at 16-48
(Threadripper 9960X, 24C/48T), but 16 of them as separate processes at 2
threads each finish in 69 s (~9x the throughput). So independent jobs (the
zooms of `highlights --zoom`, the server's job queue, scorecard seeds, a
multi-seed sweep) run in a pool of worker processes, each with its thread
pools capped:

    run(fn, items, workers=J)       fn(item, progress) for each item, J at a time;
                                    results in the order of items
    Pool(workers, threads)          a long-lived pool (the server's): .call(fn, *args, progress=cb)
    simulate_many(specs, workers)   several `planet simulate` runs at once (multi-seed sweeps)

fn must be a module-level function (it is pickled by reference), taking the
item and a progress(fraction, message) callback; progress messages come
back to the parent through a queue. Workers are started with "spawn" (a
fresh interpreter: never fork a process whose numba/TBB threads are
running), with NUMBA_NUM_THREADS, OPENBLAS_NUM_THREADS and OMP_NUM_THREADS
set before they import numpy or numba, and with the parent's data root.
One worker (workers=1) runs in this process, one job after the other.

Thread defaults for a single process (set_default_threads, applied when
`planet` is first imported, unless the variables are set already): numba
min(16, cores) threads (more gains nothing here), BLAS 1 thread (numpy's
OpenBLAS starts one thread per core by default; nothing in the model is
BLAS-heavy). The numba threading layer is pinned: tbb when it loads (TBB
runs parallel kernels launched from several threads at once), else
workqueue (which aborts on that: api.COMPUTE keeps one computation at a
time per process).
"""

from __future__ import annotations

import contextlib
import itertools
import multiprocessing as mp
import os
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool

BLAS_VARS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
THREAD_VARS = ("NUMBA_NUM_THREADS", *BLAS_VARS)
SINGLE_THREADS = 16  # numba threads for one process on its own (flat beyond ~8-16)
MAX_WORKER_THREADS = 8


def cpus() -> int:
    f = getattr(os, "process_cpu_count", None) or os.cpu_count  # (process_cpu_count: 3.13+, honours affinity)
    return max(1, f() or 1)


def set_default_threads() -> None:
    """Thread caps for this process, where not set already. Only has an
    effect before numpy and numba are imported (planet/__init__.py)."""
    os.environ.setdefault("NUMBA_NUM_THREADS", str(min(SINGLE_THREADS, cpus())))
    for v in BLAS_VARS:
        os.environ.setdefault(v, "1")


def pin_threading_layer() -> str:
    """numba's threading layer: $NUMBA_THREADING_LAYER if set, else tbb when
    its library loads (and is new enough), else workqueue. Call before the
    first parallel kernel runs (the layer is chosen then)."""
    import numba
    if os.environ.get("NUMBA_THREADING_LAYER"):
        return numba.config.THREADING_LAYER
    try:
        from numba.np.ufunc.parallel import _check_tbb_version_compatible
        _check_tbb_version_compatible()
        from numba.np.ufunc import tbbpool  # noqa: F401  (loads libtbb)
        layer = "tbb"
    except (ImportError, OSError):
        layer = "workqueue"
    numba.config.THREADING_LAYER = layer
    return layer


def default_workers(n_jobs: int | None = None) -> int:
    """Worker processes for a batch: a quarter of the cores (12 on a 48-thread
    Threadripper, 2 on an 8-core Mac), at most n_jobs."""
    w = max(1, cpus() // 4)
    return max(1, min(w, n_jobs)) if n_jobs else w


def worker_threads(workers: int) -> int:
    """Numba threads per worker: the cores shared out, 1..8 (in-process
    scaling is nearly flat beyond that)."""
    return max(1, min(MAX_WORKER_THREADS, cpus() // max(1, workers)))


_env_lock = threading.Lock()


@contextlib.contextmanager
def _thread_caps(threads: int):
    """os.environ with the workers' caps while they are spawned (a spawned
    child gets this process's environment). This process's own numpy and
    numba are loaded already (Pool imports them first), so it isn't affected."""
    with _env_lock:
        old = {v: os.environ.get(v) for v in THREAD_VARS}
        os.environ.update({"NUMBA_NUM_THREADS": str(threads), **{v: "1" for v in BLAS_VARS}})
        try:
            yield
        finally:
            for v, x in old.items():
                if x is None:
                    os.environ.pop(v, None)
                else:
                    os.environ[v] = x


# --- in the worker processes -------------------------------------------------
_queue = None


def _init(q):
    global _queue
    _queue = q
    pin_threading_layer()


def _call(token, fn, args, root):
    from . import store as S
    S.set_root(root)
    return fn(*args, lambda f, msg: _queue.put((token, float(f), str(msg))))


# --- in the parent -----------------------------------------------------------
class Pool:
    """Worker processes that run fn(*args, progress) calls, `workers` at a
    time, each worker with `threads` numba threads. A worker that dies (out
    of memory, a crash) fails its call; the pool is then started afresh."""

    def __init__(self, workers: int | None = None, threads: int | None = None):
        import numba  # noqa: F401  (this process's own thread pools are sized before _thread_caps)
        import numpy  # noqa: F401
        self.workers = max(1, workers or default_workers())
        self.threads = threads or worker_threads(self.workers)
        self._ctx = mp.get_context("spawn")
        self._q = self._ctx.Queue()
        self._cbs: dict[int, object] = {}
        self._ids = itertools.count()
        self._lock = threading.Lock()
        self._ex = self._executor()
        self._listener = threading.Thread(target=self._listen, daemon=True)
        self._listener.start()

    def _executor(self):
        return ProcessPoolExecutor(self.workers, mp_context=self._ctx, initializer=_init, initargs=(self._q,))

    def _listen(self):
        while True:
            item = self._q.get()
            if item is None:
                return
            token, f, msg = item
            with self._lock:  # (call() drops the callback under this lock: none fires after it returns)
                cb = self._cbs.get(token)
                if cb is not None:
                    try:
                        cb(f, msg)
                    except Exception:
                        pass

    def submit(self, fn, *args, progress=None):
        """A Future of fn(*args, progress) in a worker."""
        from . import store as S
        token = next(self._ids)
        with self._lock:
            if progress is not None:
                self._cbs[token] = progress
            ex = self._ex
        try:
            with _thread_caps(self.threads):  # (workers are spawned in submit, as needed)
                fut = ex.submit(_call, token, fn, args, str(S.root()))
        except BrokenProcessPool:
            self._restart(ex)
            with _thread_caps(self.threads):
                fut = self._ex.submit(_call, token, fn, args, str(S.root()))
        fut.token, fut.executor = token, self._ex
        fut.add_done_callback(lambda _: self._forget(token))
        return fut

    def _forget(self, token):
        with self._lock:
            self._cbs.pop(token, None)

    def _restart(self, broken):
        with self._lock:
            if self._ex is broken:
                broken.shutdown(wait=False, cancel_futures=True)
                self._ex = self._executor()

    def result(self, fut):
        """fut's result, raising what fn raised; no progress callback fires
        after this returns."""
        try:
            return fut.result()
        except BrokenProcessPool:
            self._restart(fut.executor)
            raise RuntimeError("the worker process died (out of memory or a crash)") from None
        finally:
            self._forget(fut.token)

    def call(self, fn, *args, progress=None):
        """fn(*args, progress) in a worker, waiting for it."""
        return self.result(self.submit(fn, *args, progress=progress))

    def caller(self, fn):
        """fn as a (req, progress) -> result function that runs in a worker
        (api.Jobs takes one)."""
        return lambda req, progress=lambda f, msg: None: self.call(fn, req, progress=progress)

    def close(self, kill: bool = False):
        """Stops the workers: after their current calls, or at once (kill)."""
        if kill and hasattr(self._ex, "terminate_workers"):  # (3.14+)
            try:
                self._ex.terminate_workers()
            except Exception:
                pass
        self._ex.shutdown(wait=not kill, cancel_futures=True)
        self._q.put(None)

    def __enter__(self):
        return self

    def __exit__(self, et, e, tb):
        self.close(kill=et is not None)


def run(fn, items, workers: int | None = None, threads: int | None = None,
        progress=None, on_done=None) -> list:
    """[fn(item, progress) for item in items], `workers` at a time in worker
    processes (default default_workers(len(items))); workers=1 runs them
    here, one after the other. progress(i, fraction, message) and
    on_done(i, result) are called in this process (on_done as each item
    finishes). Every item runs; then the first failure, if any, is raised."""
    items = list(items)
    if not items:
        return []
    workers = min(workers or default_workers(len(items)), len(items))
    results, errors = [None] * len(items), []

    def bind(i):
        return (lambda f, msg: progress(i, f, msg)) if progress else (lambda f, msg: None)

    def finish(i, get):
        try:
            results[i] = get()
        except (Exception, SystemExit) as e:  # (zoom and slice raise SystemExit for bad input)
            errors.append((i, e))
            return
        if on_done:
            on_done(i, results[i])

    if workers <= 1:
        for i, it in enumerate(items):
            finish(i, lambda: fn(it, bind(i)))
    else:
        with Pool(workers, threads) as pool:
            futs = {pool.submit(fn, it, progress=bind(i)): i for i, it in enumerate(items)}
            for fut in as_completed(futs):
                finish(futs[fut], lambda: pool.result(fut))
    if errors:
        raise min(errors, key=lambda x: x[0])[1]
    return results


# --- several runs at once (multi-seed sweeps, PW-246) --------------------------
def _simulate(spec: dict, progress) -> str:
    from . import timeline as T
    s = {"level": 6, "myr": 500.0, "dt": 2.0, "every": 4.0, **spec}
    params = T.make_params(s.get("set") or {})
    name = s.get("name") or f"seed {s['seed']}, level {s['level']}"
    out = T.simulate(s["seed"], s["level"], s["myr"], s["dt"], s["every"], name, params,
                     checkpoint_every=s.get("checkpoint_every", T.CHECKPOINT_EVERY))
    progress(1.0, f"run {out.name} done")
    return out.name


def simulate_many(specs: list[dict], workers: int | None = None, threads: int | None = None,
                  progress=None, on_done=None) -> list[str]:
    """`planet simulate` for each spec ({"seed", and optionally "level" (6),
    "myr" (500), "dt", "every", "name", "set": {param: value},
    "checkpoint_every"}), several at once; returns the run ids in spec order.
    (~8 L6 seeds at 2-4 threads each finish in little more than one run's time.)"""
    return run(_simulate, specs, workers, threads, progress, on_done)
