"""Two runs' files compared byte for byte, once each run's id, name and the code's path are swapped for placeholders; the lines that
still differ are listed (timings). argv: run_a run_b [name ...] (the two runs' names, swapped for <ID> too; default round 9's)"""
import re, sys
from pathlib import Path
a, b = Path(sys.argv[1]), Path(sys.argv[2])
NAMES = [n.encode() for n in sys.argv[3:]] or [b"l196-offold", b"l196-offnew"]
fa = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
fb = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
print("files", len(fa), len(fb), "same names", fa == fb)
def norm(p, d, other):
    s = p.read_bytes()
    for x in (d.name.encode(), *NAMES):
        s = s.replace(x, b"<ID>")
    s = re.sub(rb"/[^\"' ]*?/planet/", b"<CODE>/planet/", s)
    return s
same, diff = 0, []
for r in fa:
    if r not in fb:
        continue
    x, y = (a / r).read_bytes(), (b / r).read_bytes()
    if x == y:
        same += 1
        continue
    nx, ny = norm(a / r, a, b), norm(b / r, b, a)
    if nx == ny:
        same += 1
        continue
    diff.append(r)
    lx, ly = nx.split(b"\n"), ny.split(b"\n")
    print(f"--- {r}: differs ({len(lx)} vs {len(ly)} lines)")
    if len(lx) == len(ly):
        k = [i for i in range(len(lx)) if lx[i] != ly[i]]
        for i in k[:6]:
            print("   ", lx[i][:220], "\n   ", ly[i][:220])
        print("    lines differing:", len(k))
print("identical after ids/paths:", same, "differ:", len(diff))
