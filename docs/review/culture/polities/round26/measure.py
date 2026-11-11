"""Round 26 (lane 281c, PW-1596): the flip check's measures for one or more peoples runs. Read-only.

argv: run_dir [run_dir ...]
Per run and source (the run's polities doc as derive gives it: the live map on a switch-on run, the read-out on a switch-off run; and
on a switch-on run also the read-out on that same history, derive with the live map hidden, as round25/counts.py):
- the first state (the oldest step with a state or empire);
- at 2,000 / 1,000 / 0 years ago: states and empires standing at that single step, and averaged over the five steps around it
  (2.2-1.8, 1.2-0.8, 0.4-0 kyr ago, as round25 section 3);
- standing confederations (a state record whose `confed` lists that step) and dragon realms, single step and five-step average;
- writing: the 12 largest peoples' median first writing (round14/measure.py's rule, the run's own calendar).
Prints one JSON line per source after the readable lines (for round26.md's table)."""
import json
import statistics as st
import sys
from pathlib import Path

from planet.lineages import polities as PO

DATES = (2.0, 1.0, 0.0)
WINDOWS = {2.0: (2.2, 2.1, 2.0, 1.9, 1.8), 1.0: (1.2, 1.1, 1.0, 0.9, 0.8), 0.0: (0.4, 0.3, 0.2, 0.1, 0.0)}


def series(D):
    """{ago: (states, confederations, dragon realms)} per step."""
    conf = {}
    for r in D["polities"]:
        for a, _ in r.get("confed") or []:
            conf.setdefault(round(float(a), 3), set()).add(r["id"])
    out = {}
    for s, m in zip(D["steps"], D["maps"]):
        a = round(float(s["ago"]), 3)
        ids = conf.get(a, set())
        out[a] = (sum(e[1] in (1, 2) for e in m), sum(e[1] in (1, 2) and e[0] in ids for e in m), sum(e[1] == 3 for e in m))
    return out


def first_state(D):
    return max((float(s["ago"]) for s, m in zip(D["steps"], D["maps"]) if any(e[1] in (1, 2) for e in m)), default=None)


def near(S, a):
    return S[min(S, key=lambda x: abs(x - a))]


def measure(D):
    S = series(D)
    row = {"first_state_ya": None if first_state(D) is None else round(first_state(D) * 1000)}
    for j, name in enumerate(("states", "confeds", "dragons")):
        row[name] = [near(S, t)[j] for t in DATES]
        row[name + "_avg5"] = [round(sum(near(S, a)[j] for a in WINDOWS[t]) / 5, 1) for t in DATES]
    return row


def writing(d: Path):
    m = json.loads((d / "run.json").read_text())["meta"]
    k = m["techtree"]["known"]
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
    top = sorted([p for p in k if p in pops], key=lambda p: -pops[p])[:12]
    w = [x for x in ((k[p].get("writing") or [None])[0] for p in top) if x is not None]
    return round(st.median(w) * 1000) if w else None


def main(argv):
    for d in [Path(a) for a in argv]:
        on = (d / "polities_live.json").exists()
        rows = {"live" if on else "off": measure(PO.derive(d))}
        if on:
            _f, _ex = PO._from_live, Path.exists
            PO._from_live = None
            Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
            try:
                rows["readout_on_history"] = measure(PO.derive(d))
            finally:
                Path.exists, PO._from_live = _ex, _f
        wr = writing(d)
        print(f"=== {d.name} switch {'on' if on else 'off'}; writing median (12 largest) {wr} ya")
        for src, r in rows.items():
            print(f"  {src:19s} first state {r['first_state_ya']} ya | states 2,000/1,000/0 ya {r['states']} avg5 {r['states_avg5']} | "
                  f"confeds {r['confeds']} avg5 {r['confeds_avg5']} | dragon realms {r['dragons']} avg5 {r['dragons_avg5']}")
            print("JSON " + json.dumps({"run": d.name, "src": src, "writing_ya": wr, **r}))


if __name__ == "__main__":
    main(sys.argv[1:])
