import json
import sys

SC = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l123"
tags = sys.argv[1:] or ["base", "rl2", "eps125", "rl2eps125", "rl3eps125"]
D = {t: json.load(open(f"{SC}/v_{t}.json")) for t in tags}
for t in tags:
    print(t, {k: D[t][k] for k in ("npp_pg", "agreement", "forest_mkm2", "savanna_mkm2", "desert_mkm2", "burned", "vegc")})
print("by climate (model g C):", "  ".join(tags), " | miami mod17")
for k in D[tags[0]]["by_climate"]:
    r = D[tags[0]]["by_climate"][k]
    print(f"{k:22}", " ".join(f"{D[t]['by_climate'][k]['model']:5d}" for t in tags), f"| {r['miami']:5d} {r['mod17']:5d}")
print("Africa herb ANPP g dry / herds t/km2")
for k in D[tags[0]]["africa_warm_grassy"]:
    r = D[tags[0]]["africa_warm_grassy"][k]
    print(f"{k:9}", " ".join(f"{D[t]['africa_warm_grassy'][k]['herb_anpp_dry']:4d}/{D[t]['africa_warm_grassy'][k]['herds_t_km2']:.1f}" for t in tags),
          f"| D {r['deshmukh']} Y {r['yang']} R {r['rosenzweig_coe']}")
print("grassland above-ground (all NPP x above) g dry vs Yang")
for k in D[tags[0]]["grassland_world"]:
    r = D[tags[0]]["grassland_world"][k]
    print(f"{k:9} MAT {r['mat']}", " ".join(f"{D[t]['grassland_world'][k]['above_dry']:4d}" for t in tags), f"| Y {r['yang']}")
for g in D[tags[0]]["by_potveg_group"]:
    r = D[tags[0]]["by_potveg_group"][g]
    print(f"{g:16}", " ".join(f"{D[t]['by_potveg_group'][g]['model']:4d}" for t in tags), f"| miami {r['miami']} mod17 {r['mod17']}")
for t in tags:
    print(t, D[t]["groups"])
