"""Add (or redo) the sample sentences and grammar notes of every living lect in a languages.json, without re-running the
pass (planet/language/sentences.py on each lect's record; the pass itself does the same in output.document).

    uv run python tools/language/enrich_sentences.py IN.json OUT.json

Writes OUT.json and its sidecars (OUT-etym.json, OUT-snapshots.json) only; IN.json is never changed (a run's file stays as the pass wrote it)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from planet.language import output as OU, sentences as SN  # noqa: E402


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if len(a) != 2 or Path(a[0]).resolve() == Path(a[1]).resolve():
        print(__doc__, file=sys.stderr)
        return 2
    doc = OU.load(a[0])
    n = 0
    for l in doc["lects"]:
        if l.get("died_kyr") is None and l.get("deme") is not None:
            SN.enrich(l)
            n += 1
    OU.save(doc, a[1])   # (format /2: the main file and its two sidecars beside it)
    print(f"{n} living lects enriched -> {a[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
