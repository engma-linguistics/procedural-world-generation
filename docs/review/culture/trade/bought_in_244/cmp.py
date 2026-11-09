import json, sys
D = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l244/out"
tags = sys.argv[1:]


def tail(kmw, k):
    t = sum(w for _, w in kmw) or 1e-9
    return round(100 * sum(w for km, w in kmw if km > k) / t, 1)


for r in ["3e0eb4", "a24559", "1e97dd", "07c755"]:
    for e in ["0.0", "5.0"]:
        for t in tags:
            try:
                s = json.load(open(f"{D}/st-{t}-{r}.json"))[e]
            except FileNotFoundError:
                continue
            f = s["foods"]
            g = f.get("grain", {}); d = f.get("dried_fish", {})
            kw = s.get("kmw")
            tl = f">3k {tail(kw['grain'], 3000)}% >5k {tail(kw['grain'], 5000)}%" if kw else ""
            print(f"{r} {e:4} {t:8} food {s['with_food']:3}/{s['trading']:3} grain n{g.get('takers')} {g.get('med')}/{g.get('p90')}/max {g.get('max')} {tl}"
                  f" | fish n{d.get('takers', 0)} {d.get('med')}/{d.get('p90')}/max {d.get('max')} {d.get('roads')} | herders {s['herders']}")
print()
for r in ["3e0eb4", "a24559", "1e97dd", "07c755"]:
    try:
        A = {t: json.load(open(f"{D}/st-{t}-{r}.json"))["all_flows"] for t in tags}
    except FileNotFoundError:
        continue
    goods = sorted(set().union(*A.values()))
    print(r, " ".join(f"{g}:" + "/".join(str(A[t].get(g, [0, 0])[1]) for t in tags) for g in goods))
