"""why.py FILE...: the finish moment's verdict and reasons for each draw."""
import sys
sys.path.insert(0, "docs/review/base-climate/v1-finish-16")
sys.argv = [sys.argv[0], "/nonexistent", "a", "b"] + sys.argv[1:]
files = sys.argv[4:]
sys.argv = sys.argv[:4]
import importlib.util
spec = importlib.util.spec_from_file_location("pj", "docs/review/base-climate/v1-finish-16/pjudge.py")
src = open("docs/review/base-climate/v1-finish-16/pjudge.py").read()
src = src.split("\ndef _ln_ref")[0]
g = {"__name__": "pj", "__file__": "docs/review/base-climate/v1-finish-16/pjudge.py"}
exec(compile(src, "pjudge.py", "exec"), g)
for f in files:
    r = g["load"](f)
    fm = r["fm"]
    print(f.split("judge/")[-1], "ok", r["ok"], {k: v for k, v in fm.items() if k not in ("stats",)})
