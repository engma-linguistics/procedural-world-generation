"""One-off (PW-1394): relabel the peoples runs made before they had a kind of their own.

They were stored as kind 'timezoom' with meta.phase 'lineages'; they are now kind 'peoples' (planet/lineages/output.py).
Changes only the kind (top level and meta.kind) and drops meta.phase in each such run's own runs/<id>/run.json. Nothing else is
touched (not runs/index.json: pass --reindex to rebuild it, or let the server do it at its next job).

  uv run python tools/relabel_peoples_runs.py --backup DIR            # dry run: lists the runs
  uv run python tools/relabel_peoples_runs.py --backup DIR --apply    # copies each run.json to DIR/<id>.run.json, rewrites atomically,
                                                                      # then loads every run through the new code (store header, index entry)
Delete this script once it has been run: planet/ has no code path for the old labels.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from planet import store as S  # noqa: E402

OLD_TOP = '"kind": "timezoom"'
OLD_META = '{"kind":"timezoom","phase":"lineages",'
NEW_META = '{"kind":"peoples",'


def find_old() -> list[Path]:
    out = []
    for p in sorted(S.runs_dir().glob("*/run.json")):
        h = S.read_header(p)
        if h.get("kind") == "timezoom" and (h.get("meta") or {}).get("phase") == "lineages":
            out.append(p)
    return out


def relabelled(text: str) -> str:
    """The run.json text with the kind/phase changed; the line layout is S.write_json's (one top-level key a line)."""
    lines = text.split("\n")
    n_top = n_meta = 0
    for i, ln in enumerate(lines[:12]):  # (the header keys come first)
        if ln.startswith(OLD_TOP + ","):
            lines[i] = '"kind": "peoples",' + ln[len(OLD_TOP) + 1:]
            n_top += 1
        elif ln.startswith('"meta": ' + OLD_META):
            lines[i] = '"meta": ' + NEW_META + ln[len('"meta": ' + OLD_META):]
            n_meta += 1
    if (n_top, n_meta) != (1, 1):
        raise ValueError(f"unexpected layout (kind line x{n_top}, meta line x{n_meta})")
    return "\n".join(lines)


def check(p_old: dict, p_new: dict) -> None:
    """Only kind (top level and meta) changed and meta.phase went."""
    a, b = json.loads(json.dumps(p_old)), json.loads(json.dumps(p_new))
    a["kind"] = b["kind"] = "x"
    a["meta"]["kind"] = b["meta"]["kind"] = "x"
    a["meta"].pop("phase")
    assert a == b, "more than kind/phase changed"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backup", required=True, type=Path, help="directory the original run.json files are copied to first")
    ap.add_argument("--apply", action="store_true", help="do it (default: only list)")
    ap.add_argument("--reindex", action="store_true", help="afterwards rebuild runs/index.json (a derived file)")
    a = ap.parse_args()
    todo = find_old()
    print(f"{len(todo)} peoples runs with the old label under {S.runs_dir()}:")
    for p in todo:
        print("  " + p.parent.name)
    if not a.apply:
        return
    a.backup.mkdir(parents=True, exist_ok=True)
    for p in todo:
        shutil.copy2(p, a.backup / f"{p.parent.name}.run.json")
    for p in todo:
        text = p.read_text()
        new = relabelled(text)
        check(json.loads(text), json.loads(new))
        S.write_atomic(p, new)  # (a temp file in the folder, then a rename)
    bad = []
    for p in todo:  # loads through the new code: the header, the index entry, the family tree
        h = S.read_header(p)
        it = S._run_item(p)
        if h["kind"] != "peoples" or it["kind"] != "peoples" or "phase" in h["meta"]:
            bad.append(p.parent.name)
    if a.reindex:
        S.update_index("run")
    if bad:
        sys.exit(f"STILL WRONG: {bad}")
    print(f"relabelled {len(todo)} runs; originals in {a.backup}")


if __name__ == "__main__":
    main()
