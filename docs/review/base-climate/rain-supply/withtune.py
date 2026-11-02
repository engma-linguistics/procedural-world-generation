"""Run a tools/ script with climate.TUNE overrides: withtune.py key=val[,key=val] tools/x.py args..."""
import runpy
import sys

sys.path.insert(0, ".")
import planet  # noqa: F401
from planet import climate

for kv in sys.argv[1].split(","):
    if kv:
        k, v = kv.split("=")
        assert k in climate.TUNE, k
        climate.TUNE[k] = float(v)
        print("TUNE", k, "=", climate.TUNE[k], flush=True)
script = sys.argv[2]
sys.argv = [script] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
