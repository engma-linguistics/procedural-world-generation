import sys
p = sys.argv[1]
L = open(p).read().split("\n")
i = next(k for k, l in enumerate(L) if l.startswith("def ice_sheets("))
j = next(k for k in range(i + 1, len(L)) if L[k].startswith("def ")) - 1
for k in range(i, j):
    if L[k] == "    return ice":
        L[k] = "    return 0.0 * ice  # BREAK: no ice"
    elif L[k] == "            return new":
        L[k] = "            return 0.0 * new  # BREAK: no ice"
open(p, "w").write("\n".join(L))
