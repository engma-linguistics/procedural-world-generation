"""Re-save old-format run checkpoints in the current format (PW-1408). A one-off tool: planet/ keeps no code for the old format.

Checkpoints written before PW-1390 (merge 3cf50fdd) hold the plates as one pickled Plates object; the current code reads a packed
form (store.pack_state) and so `timeline.replay` falls back to t=0 for them. This reads each old checkpoint with the OLD code
(a `git archive cfd7d1cf planet` export, imported in a subprocess), hands the state over as plain numpy arrays, packs it with the
NEW code and writes `<t>.ckpt.new`. Only then does it check that the new file reads back as the old code's shrink_state(old state),
entry by entry (dtype, shape, bytes), and rename the new file over the old one. A checkpoint that fails keeps its old file.

    mkdir OLD && git archive cfd7d1cf planet | tar -x -C OLD
    uv run python tools/resave_checkpoints.py --old-code OLD --scratch SCRATCH [--data-root DIR] [--dry-run] [RUN_ID ...]

Without run ids: every runs/<id>/ that has a state/ folder. A run is only touched when store.run_status says "done" and no process
mentions its folder. Writes only inside runs/<id>/state/ (`<t>.ckpt.new`, then the rename). The IPC file under SCRATCH is zlib'd
pickle of plain dicts and arrays (no planet classes); delete SCRATCH afterwards.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import pickle
import subprocess
import sys
import time
import zlib
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# -- the old-code side (a subprocess) --------------------------------------------------------------------------------------
def worker_old(old_code: str, ckpt: str, level: int, out: str):
    """Old code: read the checkpoint (its own unpack_idx included), shrink_state (a no-op on what it wrote), dump the state with the
    Plates as a plain {field: value} dict. Prints OLD or NEW if the file isn't an old-format one."""
    sys.path.insert(0, old_code)
    import planet  # noqa: F401
    from planet import store
    from planet.grid import build_grid
    assert Path(planet.__file__).resolve().is_relative_to(Path(old_code).resolve()), planet.__file__
    state = store.read_checkpoint(Path(ckpt), build_grid(level))
    state = store.shrink_state(state)
    pl = state["plates"]
    state["plates"] = {f.name: getattr(pl, f.name) for f in fields(pl)}
    Path(out).write_bytes(zlib.compress(pickle.dumps(state, protocol=5), 1))


# -- comparing -------------------------------------------------------------------------------------------------------------
def flatten(x, path="", out=None):
    """{path: ('array', dtype, shape, sha1 of the bytes) | ('obj', sha1 of its pickle)} over dicts, lists, tuples and arrays."""
    import numpy as np
    out = {} if out is None else out
    if isinstance(x, np.ndarray):
        out[path] = ("array", str(x.dtype), tuple(x.shape), hashlib.sha1(np.ascontiguousarray(x).tobytes()).hexdigest())
    elif isinstance(x, dict):
        out[path + "/#keys"] = ("obj", hashlib.sha1(pickle.dumps(sorted(map(repr, x)))).hexdigest())
        for k, v in x.items():
            flatten(v, f"{path}/{k!r}", out)
    elif isinstance(x, (list, tuple)):
        out[path + "/#len"] = ("obj", len(x))
        for i, v in enumerate(x):
            flatten(v, f"{path}[{i}]", out)
    else:
        out[path] = ("obj", hashlib.sha1(pickle.dumps(x, protocol=5)).hexdigest())
    return out


def plates_dict(state: dict) -> dict:
    """A copy of state with Plates as {field: value}, to compare against the old code's dump."""
    pl = state["plates"]
    return {**state, "plates": {f.name: getattr(pl, f.name) for f in fields(pl)}}


def differences(old: dict, new: dict) -> list[str]:
    a, b = flatten(old), flatten(new)
    bad = [f"only in old: {k}" for k in a.keys() - b.keys()] + [f"only in new: {k}" for k in b.keys() - a.keys()]
    bad += [f"{k}: {a[k]} != {b[k]}" if a[k][0] == "obj" else f"{k}: old {a[k][1:3]} new {b[k][1:3]}" if a[k][1:3] != b[k][1:3]
            else f"{k}: bytes differ" for k in a.keys() & b.keys() if a[k] != b[k]]
    return bad


# -- the new-code side -----------------------------------------------------------------------------------------------------
def peek(path: Path) -> tuple[bool, set]:
    """(is it an old-format file, the state names it holds). Unpickling an old file needs no old code (Plates has the same fields)."""
    state = pickle.loads(zlib.decompress(path.read_bytes()))
    return not (isinstance(state.get("plates"), dict) and "small" in state["plates"]), set(state)


def live_processes(run_id: str) -> list[int]:
    """Pids whose command line names the run folder (read from /proc; this process and its parents excluded)."""
    cur = os.getpid()
    me, out = {cur}, []
    while True:  # (this process and its ancestors: the shell that was given the run id on its command line)
        try:
            ppid = int(Path(f"/proc/{cur}/stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
        if ppid <= 1 or ppid in me:
            break
        me.add(cur := ppid)
    for p in Path("/proc").iterdir():
        if p.name.isdigit() and int(p.name) not in me:
            try:
                cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            except OSError:
                continue
            if "resave_checkpoints" not in cmd and (f"runs/{run_id}" in cmd or run_id in cmd.split()):
                out.append(int(p.name))
    return out


class Stale(RuntimeError):
    """The checkpoint predates a change to Simulation.STATE (not just to the plates' format): it cannot be resumed from at all."""


def convert(ckpt: Path, level: int, grid, args, log) -> str:
    """'converted' | 'already' | raises (the old file is then untouched). Returns what happened."""
    from planet import store
    from planet.tectonics.plates import Plates
    old_format, names = peek(ckpt)
    if not old_format:
        return "already"
    from planet.tectonics.simulation import Simulation
    lacks, extra = set(Simulation.STATE) - names, names - set(Simulation.STATE)
    if lacks or extra:  # (written before a later change to Simulation.STATE: no code of either version can resume from it)
        raise Stale(f"lacks state {sorted(lacks)}" + (f", has unknown {sorted(extra)}" if extra else ""))
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    dump = scratch / "old_state.pkl.z"
    r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "--worker-old", args.old_code, str(ckpt), str(level),
                        str(dump)], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"old code could not read it: {r.stderr.strip().splitlines()[-1:]}")
    old = pickle.loads(zlib.decompress(dump.read_bytes()))
    dump.unlink()
    state = {**old, "plates": Plates(**old["plates"])}
    tmp = ckpt.with_name(ckpt.name + ".new")  # (state/<t>.ckpt.new: not matched by checkpoints()' *.ckpt)
    store._write_checkpoint(tmp, store.pack_state(state), grid)
    try:
        bad = differences(old, plates_dict(store.read_checkpoint(tmp, grid)))
        if bad:
            raise RuntimeError(f"the new file does not read back as the old state ({len(bad)} entries): {bad[:3]}")
    except BaseException:
        tmp.unlink(missing_ok=True)  # (our own temp file; the old checkpoint stays)
        raise
    if not args.dry_run:
        os.replace(tmp, ckpt)
    else:
        tmp.unlink()
    return "converted"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--old-code", help="a directory holding planet/ as of cfd7d1cf (git archive)")
    ap.add_argument("--scratch")
    ap.add_argument("--data-root", help="PLANET_DATA (default: the environment's, else the repository)")
    ap.add_argument("--dry-run", action="store_true", help="convert and verify, then drop the new file instead of renaming it")
    ap.add_argument("--worker-old", nargs=4, metavar=("OLD", "CKPT", "LEVEL", "OUT"), help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker_old:
        old, ckpt, level, out = args.worker_old
        return worker_old(old, ckpt, int(level), out)
    if not (args.old_code and args.scratch):
        ap.error("--old-code and --scratch are required")
    if args.data_root:
        os.environ["PLANET_DATA"] = args.data_root
    sys.path.insert(0, str(ROOT))
    import planet  # noqa: F401
    from planet import store
    from planet.grid import build_grid
    runs_dir = store.runs_dir()
    ids = args.runs or sorted(p.parent.name for p in runs_dir.glob("*/state"))
    counts = {"converted": 0, "already": 0, "stale": 0, "failed": 0}
    skipped, failed, stale = [], [], []
    nrun = {"converted": 0, "skipped": 0, "failed": 0, "stale": 0, "already": 0}
    for rid in ids:
        rd = runs_dir / rid
        st = store.run_status(rd)
        pids = live_processes(rid)
        if st != "done" or pids:
            why = f"status {st}" + (f", live processes {pids}" if pids else "")
            skipped.append((rid, why))
            print(f"{rid}: SKIPPED ({why})", flush=True)
            nrun["skipped"] += 1
            continue
        level = store.read_header(rd / "run.json", ("meta",))["meta"]["level"]
        grid = build_grid(level)
        t0, res = time.time(), {"converted": 0, "already": 0, "stale": 0, "failed": 0}
        for ckpt in sorted((rd / "state").glob("*.ckpt")):
            try:
                res[convert(ckpt, level, grid, args, print)] += 1
            except Exception as e:  # (this checkpoint keeps its old file; the others go on)
                res["stale" if isinstance(e, Stale) else "failed"] += 1
                (stale if isinstance(e, Stale) else failed).append((rid, ckpt.name, f"{type(e).__name__}: {e}"))
                print(f"{rid}/{ckpt.name}: {'STALE' if isinstance(e, Stale) else 'FAILED'} {type(e).__name__}: {e}", flush=True)
        for k in counts:
            counts[k] += res[k]
        nrun["failed" if res["failed"] else "stale" if res["stale"] else "converted" if res["converted"] else "already"] += 1
        print(f"{rid} (L{level}): {res} in {time.time() - t0:.0f}s", flush=True)
    print(f"\ncheckpoints: {counts}\nruns: {nrun}\nskipped runs: {skipped}\nstale (state older than Simulation.STATE; left as they are): {len(stale)}\nfailed checkpoints: {failed}")


if __name__ == "__main__":
    main()
