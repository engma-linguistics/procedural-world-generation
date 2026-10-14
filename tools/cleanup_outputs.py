"""Delete runs, worlds and zooms that nothing needs any more.

    uv run python tools/cleanup_outputs.py           # list what would go
    uv run python tools/cleanup_outputs.py --yes     # delete it

An output is kept when:
- an open ticket in issue-tracking/tickets mentions its id;
- it is younger than --min-age hours (default 12: work in progress, fresh demos);
- it is the Earth reference world (tools/earth_world.py);
- it is listed with --keep;
- it is the world of a kept zoom, or the run of a kept world.
Everything else is out of step with the current code (no backward
compatibility) and goes, followed by `planet delete --orphans`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planet import store as S  # noqa: E402

TICKETS = ROOT / "issue-tracking" / "tickets"


def open_ticket_text() -> str:
    out = []
    for f in sorted(TICKETS.glob("*.md")):
        s = f.read_text()
        m = re.search(r"^status:\s*(\S+)", s, re.M)
        if m and m.group(1) not in ("done", "wontdo"):
            out.append(s)
    return "\n".join(out)


def inventory() -> dict:
    """{(kind, id): {'name', 'created', 'parent': (kind, id) | None}}"""
    items = {}
    for p, it in S.items("run"):
        items[("run", it["id"])] = dict(name=it["name"], created=it["created"], parent=None)
    for p, it in S.items("world"):
        src = it.get("source_run")
        items[("world", it["id"])] = dict(name=it["name"], created=it["created"],
                                          parent=("run", src) if src else None)
    for p, it in S.items("zoom"):
        items[("zoom", it["id"])] = dict(name=it["name"], created=it["created"], parent=("world", it["world"]))
    return items


def created_at(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(s)[:19], fmt)
        except ValueError:
            pass
    return None


def plan(min_age_h: float, keep_ids: set[str]) -> tuple[dict, dict]:
    items = inventory()
    text = open_ticket_text()
    now = datetime.now()
    why = {}
    for key, it in items.items():
        kid = key[1]
        if re.search(rf"(?<![0-9a-f]){kid}(?![0-9a-f])", text):
            why[key] = "open ticket"
        elif kid in keep_ids:
            why[key] = "--keep"
        elif key[0] == "world" and str(it["name"]).startswith("Earth (today"):
            why[key] = "Earth world"
        else:
            t = created_at(it["created"])
            if t is None or now - t < timedelta(hours=min_age_h):
                why[key] = "recent"
    # parents of kept items (zoom -> world -> run)
    for _ in range(2):
        for key in list(why):
            par = items[key]["parent"]
            if par in items and par not in why:
                why[par] = f"parent of {key[1]}"
    return items, why


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="delete (default: only list)")
    ap.add_argument("--min-age", type=float, default=12.0, help="hours; younger outputs are kept")
    ap.add_argument("--keep", nargs="*", default=[], help="ids to keep regardless")
    a = ap.parse_args()
    items, why = plan(a.min_age, set(a.keep))
    order = {"zoom": 0, "world": 1, "run": 2}
    doomed = sorted((k for k in items if k not in why), key=lambda k: order[k[0]])
    for k in sorted(why, key=lambda k: order[k[0]]):
        print(f"keep {k[0]:5} {k[1]}  ({why[k]})  {items[k]['name']}")
    for k in doomed:
        print(f"DEL  {k[0]:5} {k[1]}  {items[k]['name']}")
    print(f"{len(why)} kept, {len(doomed)} to delete")
    if not a.yes:
        print("(dry run; pass --yes to delete)")
        return
    for kind, kid in doomed:
        if S.exists(kind, kid):
            S.delete(kind, kid)
    gone = S.delete_orphans()
    print(f"deleted {len(doomed)} items and {len(gone)} orphans")


if __name__ == "__main__":
    main()
