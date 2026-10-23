import re
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
N = {"forest to tundra": "forest", "glacial endings": "endings", "cold moments with sheets": "sheets",
     "ice speeds plausible": "speeds", "ice at index zero": "index0"}


def parse(path):
    out, cur = {}, None
    for l in open(path):
        m = re.match(r"^(forest to tundra|glacial endings|cold moments with sheets|ice speeds plausible|ice at index zero"
                     r"|forest|endings|sheets|speeds|index0): ", l)
        if m:
            cur = N.get(m.group(1), m.group(1))
            out.setdefault(cur, {})
            continue
        m = re.match(r"^\s+seed\s+(\d+): (pass|FAIL|sheets|none)\s+(.*)$", l)
        if m and cur and not l.startswith("E "):
            out[cur][int(m.group(1))] = (m.group(2), m.group(3))
        else:
            cur = None
    return out


def num(s, key):
    m = re.search(key + r"=([-\d.e+na]+)", s) or re.search("'" + key + r"': ([-\d.e]+)", s)
    return m.group(1) if m else ""


def short(st, v, cols):
    mark = " **x**" if st in ("FAIL", "none") else ""
    vals = []
    for c in cols:
        x = num(v, c)
        vals.append(f"{float(x):.3g}" if x not in ("", "nan") else x)
    return " / ".join(vals) + mark


main = parse("main_l4.txt")
for k, v in parse("main_l4_13-36.txt").items():
    main[k].update(v)
main.update(parse("main_l5.txt"))
br = {"main": main, "step 2": parse("tz_s2.txt"), "A20": parse("tz_a20.txt")}
print("### L4 worlds (seeds 1-24)\n")
print("Forest: F_wm2 (asserted < 0, with lost >= 5 and cooling < -0.1). Endings: extra / left 15 kyr after the first"
      " ending, m (asserted extra > 10 and left < extra / 2). **x**: the seed fails.\n")
print("| seed | main run dT | main forest | main endings | step 2 forest | step 2 endings | A20 forest | A20 endings |")
print("|---|---|---|---|---|---|---|---|")
for s in range(1, 25):
    row = [str(s), f"{float(num(main['forest'][s][1], 'run_dT')):+.2f}"]
    for b in br:
        row += [short(*br[b]["forest"][s], ["F_wm2"]), short(*br[b]["endings"][s], ["extra_m", "left_m"])]
    print("| " + " | ".join(row) + " |")
print()
for b in br:
    f, e = br[b]["forest"], br[b]["endings"]
    print(f"- {b}: forest {sum(v[0] == 'pass' for v in f.values())}/24, endings {sum(v[0] == 'pass' for v in e.values())}/24")
print("\n### L5 cold moments (the plausible seeds of 25-50)\n")
for b in br:
    d = br[b]
    k = sum(v[0] in ("pass", "sheets") for v in d["sheets"].values())
    print(f"**{b}**: {len(d['sheets'])} plausible, {k} with sheets (need 5)\n")
    print("| seed | run dT | sheets % (> 1) | median speed m/yr (1-100) | p99 (< 5000) | median H m (500-3500) |"
          " sea level change m (abs < 25) |")
    print("|---|---|---|---|---|---|---|")
    for s in sorted(d["sheets"]):
        st, v = d["sheets"][s]
        r = [str(s), f"{float(num(v, 'run_dT')):+.2f}", short(st, v, ["sheets_pct"])]
        if s in d.get("speeds", {}):
            sp, ix = d["speeds"][s], d["index0"][s]
            r += [short(*sp, ["u_median"]), num(sp[1], "u_p99"), num(sp[1], "H_median"), short(*ix, ["sl_change_m"])]
        else:
            r += ["(no sheets: not a drift-test world)", "", "", ""]
        print("| " + " | ".join(r) + " |")
    print()
