"""usage (from a tree root): lowlat_split.py [level] [dT]
lowlat.py's 'temp' case (the cooled temperatures, the start's rain, CO2 0) split in two by swapping the site's
potential evaporation (and what follows from it: the moisture index, the dry-air factor, fire weather):
  - temp_petref: the cooled temperatures but the start's PET (what the temperature does inside the plants:
    respiration's Q10, the growth curves, C3 grass's quantum yield, the envelopes)
  - pet_only:    the start's temperatures but the cooled PET (the evaporative demand alone)
Printed: tree area and F below 40 deg as lowlat.py."""
import sys

import planet  # noqa: F401
import numpy as np

sys.argv = sys.argv[:3] + ["0"]
from planet import vegetation as V

_site = V.site
SWAP = {}


def site(*a, **k):
    s = _site(*a, **k)
    if SWAP.get("pet") is not None:
        r = SWAP["pet"]
        for key in ("pet", "pet_y", "mi", "dryair", "fire_season"):
            s[key] = r[key]
    return s


V.site = site
import lowlat as L  # noqa: E402  (runs the six cases once more; cheap at L4)

s0 = V.site(L.g.lat, *(L.c0[k] for k in ("temp", "t_warm", "t_cold", "p_jul", "p_jan")), L.tilt,
            L.c0["cloud_jul"], L.c0["cloud_jan"], V.relief(L.g, L.surf))
s4 = V.site(L.g.lat, *(L.c4[k] for k in ("temp", "t_warm", "t_cold", "p_jul", "p_jan")), L.tilt,
            L.c4["cloud_jul"], L.c4["cloud_jan"], V.relief(L.g, L.surf))
for name, c, pet in (("temp_petref", L.mix(L.c4, L.c0), s0), ("pet_only", L.c0, s4)):
    SWAP["pet"] = pet
    v = L.grow(c, 0.0)
    SWAP["pet"] = None
    m = L.land & (L.al < 15)
    print(f"[{name}] tree 0-15 {float((v['sm']['tree'][m] * L.area[m]).sum() / 1e12):.2f} Mkm2; "
          f"15-40 {float((v['sm']['tree'] * L.area)[L.land & (L.al >= 15) & (L.al < 40)].sum() / 1e12):.2f}")
