"""usage: passrate4.py DIAG_DIR [...] -- moved to tools/judge.py (PW-1393); this is a pointer.
`import passrate4 as P` still gives P.judge, P.flags, P.line and the finish constants; the command line is
`uv run python tools/judge.py bar DIAG_DIR [...]`. The bar's rules are in tools/judge.py's docstring."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools.judge import *  # noqa: E402,F401,F403
from tools.judge import HUMAN_RANGE, PREIND_T, passrate_main  # noqa: E402,F401

if __name__ == "__main__":
    passrate_main(sys.argv[1:])
