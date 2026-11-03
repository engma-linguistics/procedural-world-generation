"""usage: pjudge.py OUT_ROOT ARM_A ARM_B [...] -- moved to tools/judge.py (PW-1393); this is a pointer.
The command line is `uv run python tools/judge.py paired OUT_ROOT ARM_A ARM_B [--rolls R ...] [--late T0 T1] [--json FILE]
[--level N] [--table]`; the rules are in tools/judge.py's docstring."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools.judge import load, paired_main  # noqa: E402,F401

if __name__ == "__main__":
    paired_main(sys.argv[1:])
