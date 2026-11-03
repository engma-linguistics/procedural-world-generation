"""why.py FILE...: the finish moment's verdict and reasons for each draw (run from the repo root; judge: tools/judge.py)."""
import sys
sys.path.insert(0, ".")
from tools.judge import load
for f in sys.argv[1:]:
    r = load(f)
    fm = r["fm"]
    print(f.split("judge/")[-1], "ok", r["ok"], {k: v for k, v in fm.items() if k not in ("stats",)})
