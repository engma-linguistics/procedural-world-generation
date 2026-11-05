"""A peoples run (scratch data root via PLANET_DATA), polities in the history on or off, with the round's invasion rows in the
history (polity_live.INVASIONS). argv: tree seed on|off rows|- tag. Run with PYTHONPATH pointing at the code under test."""
import os, sys, time
import planet
print("planet from", planet.__file__, flush=True)
from planet.lineages.history import params as HP
from planet.lineages.history import polity_live as PL
from planet.lineages import run as LR

S = lambda i, a, b, f, t: {"id": i, "who": {"people": a}, "whom": {"people": b}, "from_kyr": f, "to_kyr": t, "strength": "strong"}  # noqa: E731
ROWS = {  # (strong rows: round 7's two first, then four more pairs of large peoples per tree)
    "dnd": [S("orc_human", "orc", "human", 2.0, 0.3), S("hob_elf", "hobgoblin", "elf", 1.5, 0.5),
            S("dwarf_hob", "dwarf", "hobgoblin", 2.0, 0.3), S("leonin_human", "leonin", "human", 2.0, 0.3),
            S("human_kenku", "human", "kenku", 1.5, 0.3), S("elf_orc", "elf", "orc", 2.0, 0.3)],
    "seven_meals": [S("ant_human", "antelope_folk", "human", 2.0, 0.3), S("hob_dwarf", "hobgoblin", "dwarf", 1.5, 0.5),
                    S("dwarf_hob", "dwarf", "hobgoblin", 2.0, 0.3), S("halforc_human", "half_orc", "human", 2.0, 0.3),
                    S("human_tabaxi", "human", "tabaxi", 1.5, 0.3), S("elf_orc", "elf", "orc", 2.0, 0.3)],
}

tree_name, seed, sw, rows, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
HP.POLITIES_LIVE = sw == "on"
if rows != "-":
    PL.INVASIONS = ROWS[tree_name]
if os.environ.get("CAMPAIGN_KM"):  # (a test arm of PW-1478's open range, D56's lean B: one constant both paths read)
    from planet.lineages import invasions as IV
    IV.CAMPAIGN_KM = float(os.environ["CAMPAIGN_KM"])
    print("CAMPAIGN_KM", IV.CAMPAIGN_KM, flush=True)
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(os.environ.get("WORLD", "899985"), tree, 1, None, 30.0, f"l201-{tag}", progress=lambda f, msg: None)
print("run", out.name, round(time.time() - t0, 1), "s", flush=True)
