"""usage (from a tree root, PYTHONPATH=.:tests:laneA22): fearth.py [level]
fdiag.case (the forest test's numbers, F taken apart) on Earth (timezoom.source_earth), the plausibility anchor."""
import json
import sys

import planet  # noqa: F401
import fdiag
from planet import timezoom as Z

r = fdiag.case(Z.source_earth(int(sys.argv[1]) if len(sys.argv) > 1 else 4))
print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, indent=1))
