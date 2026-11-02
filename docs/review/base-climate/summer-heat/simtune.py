"""Lane 121: `planet simulate` in this process with climate.TUNE overrides (worker processes are spawned and
would not see them): simtune.py key=val[,key=val] simulate args..."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
from planet import climate  # noqa: E402

for kv in filter(None, sys.argv[1].split(",")):
    k, v = kv.split("=")
    assert k in climate.TUNE, k
    climate.TUNE[k] = float(v)
    print("TUNE", k, "=", climate.TUNE[k], flush=True)
from planet.__main__ import main  # noqa: E402

sys.argv = ["planet"] + sys.argv[2:]
main()
