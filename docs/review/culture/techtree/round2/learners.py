import json, sys, numpy as np
from pathlib import Path
from planet.lineages import techtree as TT
RUN=Path(sys.argv[1]); m=json.loads((RUN/"run.json").read_text())["meta"]
pp=m["presence_present"]; present=np.frombuffer((RUN/pp["file"]).read_bytes(),np.uint8).reshape(pp["shape"])/100.0
lm=TT.landmass_of(RUN,m); print("landmasses", int(lm.max())+1, "cells per top 12", np.bincount(lm[lm>=0])[:12])
lines=TT.with_generations(m["lineages"], m.get("tree"))
idx={}; 
for k,l in enumerate([l for l in lines if not l.get("overlay")]): pass
pres_ids=m.get("present_ids") or [l["id"] for l in lines]
print(list(m.keys())[:60])
idx={l["id"]: l.get("index", k) for k, l in enumerate(lines)}
alive={l["id"] for l in lines if l.get("ended_kyr") in (None, 0, 0.0) and not l.get("overlay") and not l.get("group_of")}
for ms in (0.1, 0.2, 0.3):
    rs=TT.region_shares(present, lm, {i: idx[i] for i in alive}, ms)
    n=[len(v) for v in rs.values()]
    print("min_share", ms, "peoples", len(rs), "learners", sum(n), "max", max(n), sorted(n, reverse=True)[:15])
