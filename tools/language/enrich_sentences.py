"""Add (or redo) the sample sentences and grammar notes of every living lect in a languages.json, without re-running the
pass (planet/language/sentences.py on each lect's record; the pass itself does the same in output.document).

    uv run python tools/language/enrich_sentences.py IN.json OUT.json

Writes OUT.json only; IN.json is never changed (a run's file stays as the pass wrote it)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from planet.language import sentences as SN  # noqa: E402


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if len(a) != 2 or Path(a[0]).resolve() == Path(a[1]).resolve():
        print(__doc__, file=sys.stderr)
        return 2
    doc = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    n = 0
    for l in doc["lects"]:
        if l.get("died_kyr") is None and l.get("deme") is not None:
            SN.enrich(l)
            n += 1
    Path(a[1]).write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{n} living lects enriched -> {a[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
