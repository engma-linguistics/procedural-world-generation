import json, sys, math, numpy as np
from pathlib import Path
from planet.lineages import techtree as TT
RUN=Path(sys.argv[1]); m=json.loads((RUN/"run.json").read_text())["meta"]
pp=m["presence_present"]; present=np.frombuffer((RUN/pp["file"]).read_bytes(),np.uint8).reshape(pp["shape"])/100.0
lm=TT.landmass_of(RUN,m); ck=m["cell_size_km"]**2
lines=m["lineages"]; idx={l["id"]: l.get("index", k) for k, l in enumerate(lines)}
alive=[l["id"] for l in lines if l.get("ended_kyr") in (None,0,0.0) and not l.get("overlay") and not l.get("group_of")]
rs=TT.region_shares(present, lm, {i: idx[i] for i in alive}, 0.1)
tot={}
for lid, rg in rs.items():
    p=present[idx[lid]]; a=float((p>=0.05).sum())*ck/1e6
    for A in (2,5,10,20):
        tot[A]=tot.get(A,0)+sum(max(1,math.ceil(w*a/A)) for _,w in rg)
    if lid=="human" or a>20: print(lid, round(a,1),"Mkm2", len(rg), [round(w,2) for _,w in rg])
print("cell km2", round(ck), "learners by A Mkm2", tot, "landmass learners", sum(len(v) for v in rs.values()))
