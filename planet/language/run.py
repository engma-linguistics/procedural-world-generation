"""`planet languages RUN [--out DIR] [--seed N] [--workers N]` (PW-986): the language pass over a stored peoples run, writing
languages.json (and meta.languages, in place) like `planet religion`. Read-only on the run's other files."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .. import store as S

FILE = "languages.json"
THIN_BYTES = 60_000_000


def write(run_dir, out_dir=None, seed: int | None = None, workers: int | None = None, report: bool = False) -> dict:
    """Run the pass and write languages.json into the run (and meta.languages), or into out_dir leaving the run untouched.
    Returns the summary."""
    from . import history as HI, output as OU
    t = time.perf_counter()
    if workers is not None:
        HI.WORKERS = int(workers)
    run_dir = Path(run_dir)
    res = HI.generate(run_dir, seed=seed)
    doc = OU.document(res)
    text = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
    if len(text) > THIN_BYTES:  # (owner: past ~60 MB, dead lects keep every 4th snapshot)
        doc = OU.document(res, thin_dead=4)
        text = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
    secs = round(time.perf_counter() - t, 1)
    sm = OU.summary(doc, FILE, secs)
    dest = Path(out_dir) if out_dir else run_dir
    dest.mkdir(parents=True, exist_ok=True)
    doc["timing"]["total_s"] = secs
    S.write_atomic(dest / FILE, json.dumps(doc, separators=(",", ":"), ensure_ascii=False))
    sm["bytes"] = (dest / FILE).stat().st_size
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
