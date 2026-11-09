"""Round 16 (lane 241): round14/measure.py on runs whose polities_live.json is format /1 (made before PW-1575, e.g. lane 234's L7
runs), which polities.derive now refuses. For such a run the "readout" is the live map itself (as derive draws it since PW-1575);
every other run is measured as measure.py does. Read-only. Same argv as measure.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "round14"))
import measure as M  # noqa: E402

_derive = M.PO.derive


def derive(d, *a, **k):
    lp = Path(d) / "polities_live.json"
    if lp.exists():
        L = json.loads(lp.read_text())
        if L.get("format") != "procgen-polities-live/2":
            recs = [{**r, "peoples": [[r["founded_kyr"], r["people"]]], "capital": {"cell": r["cell"]}} for r in L["polities"]]
            return {"polities": recs, "steps": L["steps"], "maps": L["maps"]}
    return _derive(d, *a, **k)


M.PO.derive = derive
if __name__ == "__main__":
    M.main(sys.argv[1:])
