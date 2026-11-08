"""planet.language.inputs: generation lengths from the current preset where the stored run predates a preset change (not
slow; reads only the preset, no run)."""
from pathlib import Path

from planet.language import inputs as I
from planet.lineages import spec as SP

PRESET = Path(I.__file__).resolve().parents[1] / "lineages" / "samples" / "dnd.toml"


def test_generation_override_from_current_preset():
    tree = SP.load(PRESET)
    cur = {lid: I.line_generation_yr(tree, l) for lid, l in tree.lines.items()}
    # a run built before the aarakocra change stored ~5.8 yr; humans and kenku as the preset gives them
    lines = {"aarakocra": {"generation_yr": 5.82}, "kenku": {"generation_yr": cur["kenku"]},
             "human": {"generation_yr": cur["human"]}, "red_dragon": {"generation_yr": cur["red_dragon"]}}
    ov = I.generation_overrides({"tree_file": str(PRESET)}, lines, tree)
    assert set(ov) == {"aarakocra"}
    a = ov["aarakocra"]
    assert a["stored_yr"] == 5.82 and abs(a["current_yr"] - cur["aarakocra"]) < 0.01
    assert 0.8 < a["current_yr"] / cur["kenku"] < 1.25  # (adult 12, lifespan 60, like kenku: owner 11-04)
    # a tree file that is not a preset of this checkout: no overrides, the stored lengths stand
    assert I.generation_overrides({"tree_file": "/nowhere/custom.toml"}, lines) == {}
    assert I.current_spec({"tree_file": str(PRESET)}) is not None
