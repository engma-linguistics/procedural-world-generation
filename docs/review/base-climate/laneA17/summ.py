"""The lane's bars side by side from tools.sh outputs.  usage: summ.py SUFFIX [SUFFIX ...]"""
import sys, os, re, ast
D = os.path.dirname(os.path.abspath(__file__))
def rd(n):
    p = os.path.join(D, n)
    return open(p).read() if os.path.exists(p) else ""
rows = {}
def put(k, s, v): rows.setdefault(k, {})[s] = v
for s in sys.argv[1:]:
    e = rd(f"earth_check_{s}.txt")
    m = re.search(r"log-rain correlation with GPCC, cell by cell \(log\(P \+ 10\)\): ([\d.]+)", e)
    put("rain log-r (>= 0.617)", s, m.group(1) if m else "?")
    m = re.search(r"exact code (\d+)%, main group (\d+)%", e)
    put("Koppen exact / group", s, f"{m.group(1)} / {m.group(2)}" if m else "?")
    m = re.search(r"Point check: (\d+)/78 exact, (\d+)/78 group only, (\d+)/78 wrong", e)
    put("cities exact / group / wrong", s, "/".join(m.groups()) if m else "?")
    p = rd(f"p3_{s}.txt")
    m = re.search(r"contin: (\[.*\])", p)
    if m:
        c = ast.literal_eval(m.group(1))
        sh = [x for x in c if x[0] == "S"]
        put("SH coastal range 0-150 (<= 12.5)", s, f"{sh[0][2]:.1f}")
        put("SH land 150-400 / 400-800 range bias", s, f"{sh[1][4]:+.1f} / {sh[2][4]:+.1f}")
    m = re.search(r"rows: (\{.*\})", p)
    if m:
        r = ast.literal_eval(m.group(1))
        put("Fennoscandia warm / cold", s, "%+.1f / %+.1f" % r["Fennoscandia"])
        put("Iceland / Patagonia warmest", s, "%+.1f / %+.1f" % (r["Iceland"][0], r["Patagonia"][0]))
        put("Labrador warmest", s, "%+.1f" % r["Labrador / Quebec N"][0])
    m = re.search(r"sea Tw: (.*)", p)
    if m:
        for k in ("NE Atl 45-55N", "Bay Biscay-N Sea", "S Atl off Pat", "Tasman", "Labrador Sea"):
            mm = re.search(re.escape(k) + r" [\d.-]+\(([+-][\d.]+)\)", m.group(1))
            put(f"sea warmest bias {k}", s, mm.group(1) if mm else "?")
    m = re.search(r"sea swing within 1.5x \(20-65\): nearN (\d+)% .*nearS (\d+)% .*openN (\d+)% .*openS (\d+)%", p)
    put("sea swing in 1.5x nearN/nearS/openN/openS", s, "/".join(m.groups()) if m else "?")
    m = re.search(r"sea half-swing mod/obs: (.*)", p)
    if m:
        put("half-swing NEAtl/Pat/Tasman/Agulhas", s, " ".join(re.findall(r"(?:NE Atl|Pat|Tasman|Agulhas) ([\d.]+)/", m.group(1))))
    for k in ("W Europe", "Pampas", "E Australia", "SE USA"):
        mm = re.search(re.escape(k) + r" [\d.]+\(([+-][\d.]+)\) rng [\d./]+ Ps (\d+)/(\d+)", p)
        if mm: put(f"warmest bias, summer rain mod/obs: {k}", s, f"{mm.group(1)}, {mm.group(2)}/{mm.group(3)}")
    w = rd(f"wind_{s}.txt")
    for k in ("NE Atl 45-55N", "NE Pac 40-50", "S Atl off Pat", "Tasman", "Agulhas"):
        mm = re.search(r"^\s*" + re.escape(k) + r":\s+([\d.]+)", w, re.M)
        put(f"summer wind {k}", s, mm.group(1) if mm else "?")
    mm = re.search(r"N 40-55 summer\s+([\d.]+).*\n\s*S 40-55 summer\s+([\d.]+)", w)
    put("summer wind 40-55 N / S", s, "/".join(mm.groups()) if mm else "?")
    b = rd(f"wbc_{s}.txt")
    for k in ("Tasman 35-45S", "Agulhas 30-40S", "Brazil 25-35S", "S Atl off Pat", "Gulf Str 35-45N"):
        mm = re.search(r"^\s*" + re.escape(k) + r":.*?\|\s+[\d.]+\s+[\d.]+\s*([+-][\d.]+)\s*\|\s+[\d.]+\s+[\d.]+\s*([+-][\d.]+)", b, re.M)
        put(f"sea air bias annual / warmest {k}", s, "/".join(mm.groups()) if mm else "?")
    mm = re.search(r"Tasman 35-45S:\s+[\d.]+\s*[+-][\d.]+\s*[+-][\d.]+\s+([\d.]+)", b)
    put("Tasman 35-45S SST (NCEP air 15.2)", s, mm.group(1) if mm else "?")
    o = rd(f"overturning_{s}.txt")
    for blk in re.split(r"=== overturning: ", o)[1:]:
        name = blk.split(" L6")[0].replace("world ", "")
        n = re.search(r"NH sinking\s+([\d.]+) Sv.*?:\s+(\d+)%", blk); sh = re.search(r"SH sinking\s+([\d.]+) Sv", blk)
        put(f"MOC {name} NH Sv (open%) / SH Sv", s, f"{n.group(1)} ({n.group(2)}) / {sh.group(1)}" if n and sh else "?")
        nw = re.search(r"Norwegian coast sea.*?open in winter (\d+)%.*?sea air ([\d.-]+) C", blk)
        if nw: put("Norwegian coast open % / winter sea air", s, f"{nw.group(1)} / {nw.group(2)}")
print("| bar | " + " | ".join(sys.argv[1:]) + " |")
print("|---|" + "---|" * len(sys.argv[1:]))
for k, v in rows.items():
    print(f"| {k} | " + " | ".join(v.get(s, "") for s in sys.argv[1:]) + " |")
