"""Paths at which two JSON files differ (after the run ids and code paths are swapped for placeholders). argv: a b"""
import json, re, sys
def load(p, rid):
    s = re.sub(r"l\d+-off\w+", "<ID>", open(p).read().replace(rid, "<ID>"))  # (the runs' names: l196-offold, l201-offmain, ...)
    s = re.sub(r'/[^"\' ]*?/planet/', "<CODE>/planet/", s)
    return json.loads(s)
a = load(sys.argv[1], sys.argv[1].split("/")[-2]); b = load(sys.argv[2], sys.argv[2].split("/")[-2])
out = []
def walk(x, y, path):
    if type(x) != type(y):
        out.append((path, str(x)[:80], str(y)[:80])); return
    if isinstance(x, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y:
                out.append((path + "/" + k, "missing" if k not in x else "", "missing" if k not in y else "")); continue
            walk(x[k], y[k], path + "/" + k)
    elif isinstance(x, list):
        if len(x) != len(y):
            out.append((path, f"len {len(x)}", f"len {len(y)}")); return
        for i, (u, v) in enumerate(zip(x, y)):
            walk(u, v, f"{path}[{i}]")
    elif x != y:
        out.append((path, x, y))
walk(a, b, "")
for r in out[:20]:
    print(r)
print("differing paths:", len(out))
