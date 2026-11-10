"""Summarise an 'everyone' peoples run: born, alive, extinct (when, why), biggest, events. Usage: analyse.py RUN_DIR [CONTROL_RUN_DIR]"""
import json, sys, collections
from pathlib import Path


def load(d):
    r = json.loads((Path(d) / "run.json").read_text())
    return r["meta"], r["events"]


def table(d):
    m, ev = load(d)
    L = {l["id"]: l for l in m["lineages"]}
    pres = m["present"]["lines"]
    out = {}
    unborn = {lid for lid, l in L.items() for e in ev if e.get("kind") == "unborn" and e["text"].startswith(f"no {l['name']}:")}
    for lid, l in L.items():
        if l.get("overlay") or not l.get("leaf"):
            continue
        if l.get("megafauna"):
            pass
        tr = l.get("track") or []
        peak = max(tr, key=lambda x: x[4]) if tr else None
        p = pres.get(lid)
        st = "unborn" if l.get("started_kyr") is None or lid in unborn else ("alive" if p and p.get("area_mkm2", 0) > 0 else "extinct")
        out[lid] = dict(name=l["name"][:60], started=l.get("started_kyr"), ended=l.get("ended_kyr"), status=st,
                        pop=(p or {}).get("population", 0), area=(p or {}).get("area_mkm2", 0), patches=(p or {}).get("patches", 0),
                        peak_pop=peak[4] if peak else 0, peak_kyr=peak[0] if peak else None, peak_area=peak[3] if peak else 0,
                        neigh=list((p or {}).get("neighbours", {}).keys())[:4], origin=l["origin"], parent=(l.get("parents") or [""])[0],
                        mega=bool(m["tree"]["lines"][lid].get("megafauna")) if isinstance(m.get("tree"), dict) and "lines" in m["tree"] else None,
                        faded=l.get("faded_patches"))
    return m, ev, out


def main():
    d = sys.argv[1]
    m, ev, T = table(d)
    kinds = collections.Counter(e.get("kind") for e in ev)
    print("# run", d, "| generated_in_s", m.get("generated_in_s"), "| events", dict(kinds))
    born = [k for k, v in T.items() if v["status"] != "unborn"]
    alive = [k for k, v in T.items() if v["status"] == "alive"]
    print(f"leaves (non-overlay): {len(T)}; born {len(born)}; alive {len(alive)}; extinct {len(born) - len(alive)}; unborn {len(T) - len(born)}")
    ext = sorted([(v["ended"] or 0, k) for k, v in T.items() if v["status"] == "extinct"], reverse=True)
    print("\n## extinct (ended kyr ago, peak pop at kyr, peak area)")
    for t, k in ext:
        v = T[k]
        print(f"  {k:16} ended {t:>8} kyr  started {v['started']}  peak {v['peak_pop']:,} at {v['peak_kyr']} kyr ({v['peak_area']} Mkm2)  faded {v['faded']}")
    for e in ev:
        if e.get("kind") in ("extinct", "unborn", "refuge"):
            print(f"  [{e['kind']}] {-e['t']:.1f} kyr: {e['text'][:140]} @ {e.get('lat')},{e.get('lon')}")
    print("\n## alive, by population")
    for k in sorted(alive, key=lambda k: -T[k]["pop"]):
        v = T[k]
        print(f"  {k:16} {v['pop']:>14,}  {v['area']:>6} Mkm2 in {v['patches']:>3} patches  neighbours {', '.join(v['neigh'])}")
    if len(sys.argv) > 2:
        _, _, C = table(sys.argv[2])
        print("\n## vs control (status, pop control -> experiment)")
        for k in sorted(T, key=lambda k: -C.get(k, {}).get("pop", 0)):
            c = C.get(k, {})
            if c.get("status") != T[k]["status"] or True:
                print(f"  {k:16} {c.get('status', '?'):8} {c.get('pop', 0):>14,} -> {T[k]['status']:8} {T[k]['pop']:>14,}")
    json.dump(T, open(Path(d).name + ".summary.json", "w"), indent=1)


main()
