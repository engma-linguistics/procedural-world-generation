"""The same sheet (a variant's on-run ice at the ending, frame i) under each variant's climate rules: summer at the
sheet's margins (ice cells with a bare land neighbour; bare land next to ice), per hemisphere, at -4 C and I=0."""
import sys, os, numpy as np
WT = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44"
sys.path.insert(0, WT); sys.path.insert(0, WT + "/tests")
from helpers import run_sim
from planet import timezoom as Z, store as S, climate
from planet.timezoom.sim import LAYERS
OUT = os.path.dirname(os.path.abspath(__file__)) + "/out"
sim = run_sim(); src = Z.source_from_sim(sim); g = src["grid"]
dec = lambda a, k="ice": S.decode(a, LAYERS[k]).astype(float)
sheet_of = sys.argv[1] if len(sys.argv) > 1 else "all"
fr = sys.argv[2] if len(sys.argv) > 2 else "i"
d = np.load(f"{OUT}/end_{sheet_of}.npz")
k = int(d[fr])
H = dec(d["ice_on"][k]); elev = dec(d["elev_on"][k], "elevation")
land = elev > 0
iced = land & (H > 1)
bare = land & ~iced
nb = lambda m: np.bincount(g.nbr_src, weights=m[g.nbr_idx].astype(float), minlength=g.n) > 0
m_ice = iced & nb(bare)
m_bare = bare & nb(iced)
print(f"sheet of {sheet_of} at frame {fr} t={d['t'][k]}: iced {iced.sum()} margin-ice {m_ice.sum()} margin-bare {m_bare.sum()}")
VAR = {"main": dict(S3_REACH="0", S3_FETCH="0", S3_SPLIT="0", S3_MTN="0"), "all": {}, "nofetch": dict(S3_FETCH="0"),
       "nosplit": dict(S3_SPLIT="0"), "noreach": dict(S3_REACH="0"), "nomtn": dict(S3_MTN="0")}
for name, env in VAR.items():
    for kk in ("S3_REACH", "S3_FETCH", "S3_SPLIT", "S3_MTN"):
        os.environ[kk] = env.get(kk, "1")
    c = climate.compute(g, elev, src["dT"] - 4.0, src["tilt"], ice_air=np.where(iced, H, 0.0))
    tw, tc = c["t_warm"], c["t_cold"]
    ps = np.where(g.lat >= 0, c["p_jul"], c["p_jan"]); pw = np.where(g.lat >= 0, c["p_jan"], c["p_jul"])
    out = []
    for hs, hm in (("N", g.lat > 0), ("S", g.lat < 0)):
        for lab, m in (("ice-mrg", m_ice & hm), ("bare-mrg", m_bare & hm), ("ice-all", iced & hm)):
            out.append(f"{hs} {lab} tw {tw[m].mean():6.2f} tc {tc[m].mean():6.1f} p {ps[m].mean() + pw[m].mean():5.0f}")
    print(f"{name:8s} | " + " | ".join(out))
