"""Count the output slips of PW-1739 in a languages.json (the names block's template slips, names.slips, plus a few
shares a reader meets on the first page).

    uv run python -I tools/language/slips.py runs/a24559/languages.json [--examples 3] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from planet.language import names as NM  # noqa: E402


def measure(doc: dict) -> dict:
    names = doc.get("names") or {}
    out = {k: len(v) for k, v in NM.slips(names).items()}
    places = [x for e in (names.get("demes") or {}).values() for x in (e.get("places") or []) + (e.get("settlements") or [])
              if x.get("roman")]
    out["places"] = len(places)
    out["rr_share_places"] = round(sum(1 for x in places if "rr" in x["roman"].lower()) / max(len(places), 1), 3)
    pn = names.get("personal") or {}
    out["given_per_lect"] = round(sum(len(x.get("given") or []) for x in pn.values()) / max(len(pn), 1), 2)
    out["full_names_per_lect"] = round(sum(len(x.get("bynames") or []) for x in pn.values()) / max(len(pn), 1), 2)
    full = [len(b["roman"].replace(" ", "")) for x in pn.values() for b in x.get("bynames") or [] if b.get("roman")]
    out["full_name_max_letters"] = max(full) if full else 0
    lm = [x.get("roman") or "" for x in (names.get("landmasses") or {}).values()]
    out["landmass_max_letters"] = max((len(x) for x in lm), default=0)
    fam = doc.get("families") or {}
    langs = fam.get("languages") or []
    out["languages_unnamed"] = sum(1 for x in langs if re.match(r"^(speech of|lang\d)", x.get("name") or ""))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file")
    ap.add_argument("--examples", type=int, default=0)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    doc = json.loads(Path(a.file).read_text())
    m = measure(doc)
    for k, v in m.items():
        print(f"{k:24s} {v}")
    if a.examples:
        for k, v in NM.slips(doc.get("names") or {}).items():
            for x in v[: a.examples]:
                print(f"  {k}: {x[:120]}")
    if a.json:
        Path(a.json).write_text(json.dumps(m, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
