"""`planet languages RUN [--out DIR] [--seed N] [--workers N]` (PW-986): the language pass over a stored peoples run, writing
languages.json (and meta.languages, in place) like `planet religion`. Read-only on the run's other files."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .. import store as S

FILE = "languages.json"
THIN_BYTES = 60_000_000


def write(run_dir, out_dir=None, seed: int | None = None, workers: int | None = None, report: bool = False, progress=None) -> dict:
    """Run the pass and write languages.json and its sidecars (output.save: languages-etym.json, languages-snapshots.json)
    into the run (and meta.languages), or into out_dir leaving the run untouched. Returns the summary.
    progress(fraction, message), if given: through the intervals, then the write-up (planet make, PW-1634)."""
    from . import history as HI, output as OU
    t = time.perf_counter()
    if workers is not None:
        HI.WORKERS = int(workers)
    run_dir = Path(run_dir)
    res = HI.generate(run_dir, seed=seed, progress=progress)
    if progress is not None:
        progress(0.9, "languages: writing languages.json")
    t2 = time.perf_counter()
    doc = OU.document(res)
    doc["timing"]["document_s"] = round(time.perf_counter() - t2, 1)
    if len(OU.dumps(doc)) > THIN_BYTES:  # (owner: past ~60 MB unpacked, dead lects keep every 4th snapshot)
        OU.thin_dead(doc, res, 4)
    secs = round(time.perf_counter() - t, 1)
    sm = OU.summary(doc, FILE, secs)
    dest = Path(out_dir) if out_dir else run_dir
    dest.mkdir(parents=True, exist_ok=True)
    doc["timing"]["total_s"] = secs
    files = OU.save(doc, dest / FILE)
    sm["format"] = OU.FORMAT2
    sm["files"] = files
    sm["bytes"] = sum(files.values())
    if out_dir is None:
        S.update_meta(run_dir, lambda m: m.__setitem__("languages", sm))
        if report:
            with open(run_dir / "run.txt", "a") as f:
                f.write("\n".join(lines_for_report(sm)) + "\n")
    return sm


def lines_for_report(sm: dict) -> list[str]:
    ch = ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in (sm.get("checks") or {}).items())
    return [f"languages (PW-986): {sm['lects']} lects ({sm['living']} living, {sm['protos']} proto-languages), "
            f"{sm['languages']} languages, {sm['shifts']} language shifts, {sm['food_routes']} food-word routes; "
            f"scholars' horizon {sm.get('horizon_human_kyr')} kyr (human lects), {sm.get('horizon_kyr')} kyr (all); "
            f"{sm.get('generated_in_s')} s", f"  checks: {ch}"]
