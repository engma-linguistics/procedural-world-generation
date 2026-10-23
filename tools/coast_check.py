"""Coast form and coast-bound life (coastform.py, PW-097) on Earth: named
places against the coast classes, the seabird and seal scores and the reef
layer, as a plausibility anchor (never a target).

A place passes when any coastal land cell within RADIUS_KM has one of the
expected classes (or, for a score, reaches it); "not" places pass when none
does. The world's layers are computed in memory, the world is not written.

    uv run python tools/coast_check.py [world id, default: the newest Earth world]
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from planet import coastform as CF  # noqa: E402
from planet import store as S  # noqa: E402
from planet import world as W  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402

RADIUS_KM = 250.0
# name, lat, lon, expected classes (or ("score", layer, min)), True = should be there, False = should not
PLACES = [
    ("Outer Banks (N Carolina)", 35.5, -75.6, {"barrier"}, True),
    ("Texas Gulf coast (Padre)", 27.0, -97.3, {"barrier", "low"}, True),
    ("Wadden Sea (Frisian Is.)", 53.5, 6.5, {"barrier", "tidal"}, True),
    ("Florida Atlantic coast", 28.5, -80.6, {"barrier"}, True),
    ("Norway (Sognefjord)", 61.1, 5.0, {"fjord"}, True),
    ("Southern Chile", -47.0, -74.5, {"fjord", "ice"}, True),
    ("British Columbia", 52.0, -128.0, {"fjord"}, True),
    ("West Greenland", 66.0, -53.5, {"fjord", "ice"}, True),
    ("Fiordland (NZ)", -45.5, 167.0, {"fjord", "cliff"}, True),
    ("Cornwall", 50.1, -5.5, {"cliff", "rocky"}, True),
    ("Big Sur (California)", 36.0, -121.5, {"cliff", "rocky"}, True),
    ("Bunda Cliffs (Nullarbor)", -31.7, 130.5, {"cliff"}, True),
    ("Bay of Fundy", 45.0, -65.0, {"tidal"}, True),
    ("Korea west coast", 37.0, 126.3, {"tidal"}, True),
    ("Sundarbans", 21.8, 89.5, {"mangrove", "delta", "tidal"}, True),
    ("Para / Amapa (Amazon mouth)", -0.5, -49.0, {"mangrove", "delta", "tidal"}, True),
    ("Everglades", 25.3, -81.0, {"mangrove"}, True),
    ("Mississippi delta", 29.2, -89.4, {"delta"}, True),
    ("Nile delta", 31.4, 31.0, {"delta"}, True),
    ("Mekong delta", 9.8, 106.5, {"delta", "mangrove"}, True),
    ("Queensland (GBR coast)", -18.0, 146.2, {"coral"}, True),
    ("Belize", 17.3, -88.3, {"coral", "mangrove"}, True),
    ("Red Sea (Jeddah)", 21.5, 39.1, {"coral"}, True),
    ("Peru (Lima)", -12.0, -77.2, {"coral", "mangrove"}, False),
    ("Namibia (Walvis Bay)", -22.9, 14.5, {"coral", "mangrove"}, False),
    ("Antarctic Peninsula", -64.5, -62.0, {"ice", "fjord"}, True),
    ("Peru guano coast", -12.0, -77.2, ("score", "seabirds", 0.5), True),
    ("Namibia seabirds", -24.0, 14.5, ("score", "seabirds", 0.5), True),
    ("Orkney / N Scotland seabirds", 59.0, -3.0, ("score", "seabirds", 0.5), True),
    ("Cape Cross seals (Namibia)", -21.8, 14.0, ("score", "seals", 0.5), True),
    ("California sea lions", 36.6, -122.0, ("score", "seals", 0.5), True),
    ("Gulf of Guinea (no seals)", 5.0, 0.0, ("score", "seals", 0.3), False),
]


def near_sea(g, d, L):
    return np.flatnonzero((d <= RADIUS_KM) & (np.asarray(L["elevation"]) <= 0))


def main(ref=None):
    if ref is None:
        ws = [p for p in sorted(S.worlds_dir().glob("*.json"), key=lambda p: p.stat().st_mtime)
              if p.stem != "index" and S.read_header(p, ("meta",)).get("meta", {}).get("source_run") == "earth"]
        ref = ws[-1].stem
    w = W.load(S.find_world(ref))
    g, L = w["grid"], w["layers"]
    L.update(CF.world_layers(g, L, w["meta"]))
    ct = np.asarray(L["coast_type"])
    keys = {c[0]: c[1] for c in CF.CLASSES}
    ok = 0
    print(f"world {ref}: {w['name']}  (radius {RADIUS_KM:.0f} km)")
    for name, lat, lon, want, should in PLACES:
        p = xyz(np.radians(lat), np.radians(lon))
        d = R_KM * np.arccos(np.clip(g.centers @ p, -1, 1))
        near = np.flatnonzero((d <= RADIUS_KM) & (ct > 0))
        found = sorted({keys[int(ct[i])] for i in near})
        if isinstance(want, tuple):
            v = float(np.asarray(L[want[1]], float)[near].max()) if len(near) else 0.0
            hit = v >= want[2]
            got = f"{want[1]} max {v:.2f}"
        else:
            hit = bool(set(found) & want)
            got = ", ".join(found) or "no coast cell"
            if "coral" in want and len(near):
                got += f" (reef next to the coast: max {float(np.asarray(L['reef'], float)[near_sea(g, d, L)].max()):.1f}%)"
        good = hit == should
        ok += good
        print(f"  {'ok ' if good else 'MISS'} {name:<30} {'want' if should else 'not'} "
              f"{str(want[1:]) if isinstance(want, tuple) else '/'.join(sorted(want)):<28} got {got}")
    print(f"{ok}/{len(PLACES)} places right")
    s = CF.summary(g, L)
    print(CF.text_section(s))
    return ok


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
