"""Monkeypatching timers: wraps every planet Python function/method and every
top-level numba dispatcher (one not called from other jitted code) with a
stack-based perf_counter timer. Tree of inclusive times keyed by call path."""
import importlib, pkgutil, time, types, json, threading
from collections import defaultdict
from numba.core.registry import CPUDispatcher

TREE = defaultdict(lambda: [0.0, 0])   # path tuple -> [seconds, calls]
STACK = []
_pc = time.perf_counter


def _wrap(fn, label):
    def w(*a, **k):
        if threading.current_thread() is not threading.main_thread():
            return fn(*a, **k)   # the checkpoint writer thread would corrupt the shared stack
        STACK.append(label)
        t0 = _pc()
        try:
            return fn(*a, **k)
        finally:
            dt = _pc() - t0
            e = TREE[tuple(STACK)]
            e[0] += dt
            e[1] += 1
            STACK.pop()
    w.__wrapped__ = fn
    if hasattr(fn, "py_func"):
        w.py_func = fn.py_func
        w.targetoptions = fn.targetoptions
    w.__name__ = getattr(fn, "__name__", label)
    w.__qualname__ = getattr(fn, "__qualname__", label)
    w.__doc__ = getattr(fn, "__doc__", None)
    return w


SKIP_MODS = {"planet.server", "planet.__main__"}


def install():
    import planet
    mods = [planet]
    for m in pkgutil.walk_packages(planet.__path__, "planet."):
        if m.name in SKIP_MODS:
            continue
        mods.append(importlib.import_module(m.name))
    disp, nested = {}, set()
    for m in mods:
        for v in vars(m).values():
            if isinstance(v, CPUDispatcher):
                disp[id(v)] = v

    def names(code):
        out = set(code.co_names)
        for c in code.co_consts:
            if isinstance(c, types.CodeType):
                out |= names(c)
        return out
    for d in disp.values():
        g = d.py_func.__globals__
        for n in names(d.py_func.__code__):
            o = g.get(n)
            if isinstance(o, CPUDispatcher):
                nested.add(id(o))
    repl = {}
    for d in disp.values():
        if id(d) not in nested:
            repl[id(d)] = _wrap(d, "K:" + d.py_func.__module__.replace("planet.", "") + "." + d.py_func.__name__)
    seen_cls = set()
    for m in mods:
        for v in list(vars(m).values()):
            if isinstance(v, types.FunctionType) and (v.__module__ or "").startswith("planet"):
                if id(v) not in repl:
                    repl[id(v)] = _wrap(v, v.__module__.replace("planet.", "") + "." + v.__name__)
            elif isinstance(v, type) and v.__module__ == m.__name__ and id(v) not in seen_cls:
                seen_cls.add(id(v))
                for an, av in list(vars(v).items()):
                    if an.startswith("__") and an != "__post_init__":
                        continue
                    lab = v.__module__.replace("planet.", "") + "." + v.__name__ + "." + an
                    if isinstance(av, types.FunctionType):
                        setattr(v, an, _wrap(av, lab))
                    elif isinstance(av, staticmethod):
                        setattr(v, an, staticmethod(_wrap(av.__func__, lab)))
                    elif isinstance(av, classmethod):
                        setattr(v, an, classmethod(_wrap(av.__func__, lab)))
    for m in mods:
        for k, v in list(vars(m).items()):
            if isinstance(v, (types.FunctionType, CPUDispatcher)) and id(v) in repl:
                setattr(m, k, repl[id(v)])
    return len(repl), len(nested)


def reset():
    TREE.clear()


def dump(path, wall, extra=None):
    rows = [{"path": list(k), "s": v[0], "n": v[1]} for k, v in TREE.items()]
    with open(path, "w") as f:
        json.dump({"wall": wall, "rows": rows, **(extra or {})}, f)
