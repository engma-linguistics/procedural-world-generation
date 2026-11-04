"""planet.language.profiles and the spec `voice` hook (not slow)."""
import math
import tomllib
from pathlib import Path

import pytest

from planet.language import profiles as PR
from planet.language.percepts import from_ipa
from planet.lineages import spec as SP

DND = Path(__file__).resolve().parent.parent / "planet" / "lineages" / "samples" / "dnd.toml"


def one(s):
    (seg,) = from_ipa(s)
    return seg


@pytest.fixture(scope="module")
def tree():
    return SP.parse(tomllib.loads(DND.read_text(encoding="utf-8")))


def test_data_file_valid_and_keyed_by_dnd_ids(tree):
    data = PR.load_profiles()
    assert {"avian", "aarakocra", "kenku", "reptilian", "saurian", "tortle", "lizardfolk", "troglodyte", "kobold",
            "dragonborn", "chromatic_dragon", "metallic_dragon", "feline", "tabaxi", "leonin", "goblinoid", "giantkin",
            "dwarf", "halfling", "elf", "orc", "human", "gnome"} <= set(data)
    assert set(data) <= set(tree.lines), set(data) - set(tree.lines)


def test_human_cost_from_phoible():
    assert PR.human_freq()[1] in ("phoible_segments.tsv", "builtin")
    assert PR.human_cost(one("m")) == pytest.approx(PR.COST_MIN)  # in 97% of languages: clamped
    assert PR.human_cost(one("p")) < PR.human_cost(one("pʼ")) < PR.human_cost(one("ʘ"))
    assert PR.human_cost(one("ʛ")) <= PR.COST_MAX
    assert math.isinf(PR.human_cost(one("aᴖ"))) and math.isinf(PR.human_cost(one("a˯"))) and math.isinf(PR.human_cost(one("ʞ")))
    assert PR.human_cost(one("a˦")) > PR.human_cost(one("a"))


def test_keys_of():
    assert PR.keys_of(one("p")) == {"labial", "stop"}
    assert {"labial", "velar", "double", "approximant"} <= PR.keys_of(one("w"))
    assert {"velar", "stop", "ejective", "labialized"} <= PR.keys_of(one("kʷʼ"))
    assert {"round_vowel", "back_vowel", "high_vowel", "long", "tone"} <= PR.keys_of(one("uː˦"))
    assert {"sub_register"} <= PR.keys_of(one("a˯")) and {"source2"} <= PR.keys_of(one("aᴖ"))
    assert set().union(*(PR.keys_of(r.seg) for r in __import__("planet.language.percepts", fromlist=["x"]).symbols())) <= set(PR.PERCEPT_KEYS)


def test_species_cost_equals_human_for_human():
    for s in ("p", "kʷʼ", "ã", "a˯", "ʞ"):
        a, b = PR.species_cost(PR.HUMAN, one(s)), PR.human_cost(one(s))
        assert a == b or (math.isinf(a) and math.isinf(b))


def test_inheritance_stem_kind_and_flags(tree):
    aar = PR.profile_for(tree, "aarakocra")
    assert aar.source == "data_file" and [c[0] for c in aar.chain] == ["avian", "aarakocra"]
    assert aar.make_cost["labial"] == 3.0  # the kind overrides the stem's 2.5
    assert aar.make_cost["source2"] == PR.load_profiles()["avian"]["make_cost"]["source2"]  # the stem's key survives
    assert "syrinx" in aar.articulators and "lips" not in aar.articulators
    tortle = PR.profile_for(tree, "tortle")
    assert "beak" in tortle.articulators and "teeth" not in tortle.articulators  # +/- edits of the stem's list
    assert tortle.hear["sibilant"] < PR.profile_for(tree, "lizardfolk").hear["sibilant"]
    assert PR.profile_for(tree, "mammalian").source == "human_default"  # not yet profiled
    assert PR.profile_for(tree, "human").source == "data_file"  # judged human, on purpose
    assert PR.species_cost(aar, one("p")) > PR.human_cost(one("p"))
    assert math.isfinite(PR.species_cost(aar, one("aᴖ")))
    assert math.isinf(PR.species_cost(PR.profile_for(tree, "elf"), one("aᴖ")))
    red = PR.profile_for(tree, "red_dragon")
    assert red.register < 0 and red.hears(one("a˯")) and math.isfinite(PR.species_cost(red, one("a˯")))
    assert not PR.profile_for(tree, "kobold").hears(one("a˯"))  # size effects sit on the dragon families, not the stem


def test_spec_voice_overrides_data_file():
    data = PR.load_profiles()
    raw = {"meta": {}, "lineage": [
        {"id": "avian", "origin": "root", "at": "6 Myr"},
        {"id": "aarakocra", "parents": ["avian"], "at": "900 kyr",
         "voice": {"make_cost": {"labial": 5, "tone": "inf"}, "notes": ["spec says so"]}},
        {"id": "hawkfolk", "parents": ["aarakocra"], "at": "100 kyr"}]}
    t = SP.parse(raw)
    assert t.lines["aarakocra"].voice_given["make_cost"]["tone"] == "inf"
    assert t.lines["hawkfolk"].voice == t.lines["aarakocra"].voice and not t.lines["hawkfolk"].voice_given
    p = PR.profile_for(t, "hawkfolk", data)
    assert p.source == "spec" and p.make_cost["labial"] == 5.0 and math.isinf(p.make_cost["tone"])
    assert p.make_cost["nasal"] == data["avian"]["make_cost"]["nasal"]
    assert ("aarakocra", "spec") in p.chain and ("aarakocra", "data_file") in p.chain
    back = SP.to_raw(t)
    rows = {r["id"]: r for r in back["lineage"]} if isinstance(back, dict) else {r["id"]: r for r in back}
    assert rows["aarakocra"]["voice"] == raw["lineage"][1]["voice"] and "voice" not in rows["hawkfolk"]
    with pytest.raises(ValueError):
        SP.parse({"meta": {}, "lineage": [{"id": "x", "origin": "root", "at": "1 Myr", "voice": {"make_cost": {"lips": 2}}}]})
    with pytest.raises(ValueError):
        SP.parse({"meta": {}, "lineage": [{"id": "x", "origin": "root", "at": "1 Myr", "voice": {"loud": 2}}]})


def test_dnd_tree_has_no_spec_voice_yet(tree):
    assert all(not l.voice_given for l in tree.lines.values())


def test_hear_word_drops_sub_bass_for_humans():
    word = tuple(from_ipa("ka˯ŋ˯a"))
    inv = [one(x) for x in ("k", "ŋ", "a", "m", "i")]
    out = PR.hear_word(word, PR.HUMAN, inv)
    assert out == (one("k"), one("a"))
    dragon_ear = PR.VoiceProfile(id="d", source="spec", hear={"sub": 1.0})
    assert len(PR.hear_word(word, dragon_ear, inv)) == 4


def test_hear_word_maps_labial_to_grave_for_beaked_listener(tree):
    aar = PR.profile_for(tree, "aarakocra")
    inv = [one(x) for x in ("t", "k", "s", "n", "ŋ", "a", "i", "u")]  # a beaked lect without labials
    out = PR.hear_word(tuple(from_ipa("pama")), aar, inv)
    assert out == (one("k"), one("a"), one("ŋ"), one("a"))
    # nothing near enough is dropped
    assert PR.hear_word(tuple(from_ipa("ǂa")), aar, [one("a")], drop_distance=4.0) == (one("a"),)


def test_validate_voice_errors():
    with pytest.raises(ValueError):
        PR.validate_voice({"make_cost": {"labial": 0}}, "x")
    with pytest.raises(ValueError):
        PR.validate_voice({"hear": {"pitch": 1}}, "x")
    with pytest.raises(ValueError):
        PR.validate_voice({"articulators": ["tentacle"]}, "x")
    assert PR.validate_voice({"make_cost": {"labial": "inf"}}, "x")["make_cost"]["labial"] == math.inf
