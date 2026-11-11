"""names.py (PW-972): endonym patterns, the people set through a class grammar, exonyms by direction and by relay, river
names kept through a language shift, the brief's plain-words summary, and the brief's languages section (not slow)."""
from __future__ import annotations

import json

import numpy as np

from planet.language import grammar as G
from planet.language import inventory as INV
from planet.language import lect as LC
from planet.language import lexicon as LX
from planet.language import names as NM
from planet.language import profiles as PR
from planet.language.percepts import from_ipa, word_ipa
from planet.lineages import brief as BR

FRAMES = [2.0, 1.5, 1.0, 0.5, 0.0]


def _mk(lid, people, deme, seed, inv=None, parent=None, how="proto", born=2.0, died=None):
    rng = np.random.default_rng(seed)
    inv = inv or INV.draw_inventory(rng, PR.HUMAN)
    lex = LX.proto_lexicon(rng, inv, LX.concepts(None), born, lid)
    g = G.proto_grammar(rng, inv, lex, kyr=born)
    return LC.Lect(id=lid, deme=deme, people=people, parent=parent, how=how, born_kyr=born, died_kyr=died, inventory=inv,
                   lexicon=lex, grammar=g, profile=PR.HUMAN, population=1000.0)


class FakeRun:
    """The few Run methods names.py asks: deme landscape, contacts, reputation rows, lines."""

    def __init__(self, demes, lines, rows=None, landscape=None, contacts=None):
        self.frames_kyr = list(FRAMES)
        self.demes = demes
        self.lines = lines
        self.meta = {"present": {"reputation": {"rows": rows or {}}, "landmasses": []}}
        self._ls = landscape or {}
        self._c = contacts or {}
        self.dir = None
        self.taboos_doc = {}
        self.seed = 3

    def people_of(self, d):
        return self.demes[d]["people"]

    def frame_of(self, kyr):
        return int(min(max(round((2.0 - kyr) / 0.5), 0), len(FRAMES) - 1))

    def deme_landscape(self, d, i):
        return dict(self._ls.get(d, {}))

    def contacts_of(self, d, i):
        return dict(self._c.get(d, {}))

    def mixed_cities(self, i):
        return []


def _line(pid, **kw):
    return {"id": pid, "parents": [], "traits": [], "way": None, "body": {"teeth": "grinding", "display": "none"}, **kw}


def _deme(i, people):
    return {"id": i, "people": people, "place": "the west of Testa"}


def _world(rows=None):
    ls = [_mk("d0", "human", 0, 1), _mk("d1", "orc", 1, 2), _mk("d2", "elf", 2, 3)]
    run = FakeRun([_deme(0, "human"), _deme(1, "orc"), _deme(2, "elf")],
                  {p: _line(p) for p in ("human", "orc", "elf")}, rows=rows, contacts={0: {1: 0.5}, 1: {0: 0.5}})
    return {"lects": ls, "shifts": [], "seed": 11}, run


# ---------------------------------------------------------------------------------------------- endonyms
def test_pattern_choice_deterministic():
    res, run = _world()
    a = NM.build_names(res, run)
    b = NM.build_names(*_world())
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    for p, v in a["peoples"].items():
        assert v["endonym"]["pattern"] in NM.PATTERNS and v["endonym"]["roman"][0].isupper()
        assert v["endonym"]["etym"][-1][2].startswith("name:")
    pats = {NM._Pass(res, run, s, None).endonym_pattern("human")[0] for s in range(40)}
    assert {"people", "real"} <= pats  # (the commonest variants turn up over seeds)
    assert {NM.VARIANT_CODE[v] for v in pats} <= set(NM.PATTERNS)


def test_pattern_codes_follow_the_owners_taxonomy():
    """Codes mean what the owner's doc says (rev 7): E4 free/noble, E6 land or river, E9 trait or custom, X7 observed
    appearance or dwelling; the river people are E6, the totem people E9, a relayed exonym X4, the scholars' name 'scholarly'."""
    assert "free" in NM.PATTERNS["E4"] and "river" in NM.PATTERNS["E6"] and "trait" in NM.PATTERNS["E9"]
    assert "dynasty" in NM.PATTERNS["X6"] and "misattributed" in NM.PATTERNS["X9"]
    V = NM.VARIANT_CODE
    assert V["river_people"] == V["river_name"] == "E6" and V["totem"] == "E9" and V["body"] == "E9" and V["relay"] == "X4"
    assert V["by_dwelling"] == "X7" and V["original"] == "E2" and V["many"] == "E11"
    assert set(V.values()) <= set(NM.PATTERNS)


def test_five_class_grammar_gives_four_forms_on_one_root():
    l = _mk("d0", "human", 0, 9)
    g = l.grammar
    rng = np.random.default_rng(9)
    g.class_system = G.ClassSystem("classes")
    g.grams = [x for x in g.grams if not x.function.startswith("CLASS") and x.function != "PL"]

    class Inv:
        consonants, vowels, tones = from_ipa("ptkmnslwb"), from_ipa("aiu"), []
    for grp, f in {"person": "mu", "people": "ba", "manner": "lu", "abstract": "bu", "plant": "mi"}.items():
        nc = G.add_class(g, rng, Inv(), l.lexicon, 1.0, group=grp, level=G.AFFIX)
        g.by_id(nc.gram_id).form = tuple(from_ipa(f))
    real = l.lexicon["REAL"]
    n = NM._people_name(l, [real], "the real people", "E2")
    forms = {k: v["ipa"] for k, v in n["set"].items()}
    assert len(set(forms.values())) == 4
    root = word_ipa(n["root"])
    assert all(root in v for v in forms.values())
    assert "people class" in n["plain"] and "'real'" in n["plain"]


# ---------------------------------------------------------------------------------------------- exonyms
def test_exonym_by_direction_uses_observers_word():
    rows = {"human": {"orc": {"valence": "exotic", "category": "strangers", "basis": "some contact", "since_kyr": 1.0,
                              "strength": 0.5, "from_dir": "north"}}}
    res, run = _world(rows)
    obs = res["lects"][0]
    obs.lexicon.words.pop("STRANGER", None)  # (only the direction is left to name them by)
    names = NM.build_names(res, run)
    x = names["peoples"]["orc"]["exonyms"][0]
    assert x["pattern"] == "X8" and x["by_people"] == "human" and x["by_lect"] == "d0"
    assert "NORTH" in x["parts"] and x["basis"] == "some contact" and x["era_kyr"] == 1.0
    north = word_ipa(obs.lexicon["NORTH"].form)
    assert any(st[3] == north for st in x["etym"])  # (the observer's own word for north, not the subject's)
    assert x["gloss"] == "the northerners"


def test_relayed_exonym_differs_from_direct():
    res, run = _world()
    tiny = INV.Inventory(consonants=list(from_ipa("pk")), vowels=list(from_ipa("a")), shapes={"CV": 1.0})
    relay = _mk("d3", "kobold", 3, 4, inv=tiny)
    res["lects"].append(relay)
    run.demes.append(_deme(3, "kobold"))
    run.lines["kobold"] = _line("kobold")
    row = {"valence": "neighbour", "basis": "neighbours", "since_kyr": 0.5, "strength": 0.9}
    run.meta["present"]["reputation"]["rows"] = {"human": {"orc": dict(row)}}
    direct = NM.build_names(res, run)["peoples"]["orc"]["exonyms"][0]
    run.meta["present"]["reputation"]["rows"] = {"human": {"orc": dict(row, borrowed_from="kobold")}}
    relayed = NM.build_names(res, run)["peoples"]["orc"]["exonyms"][0]
    assert direct["pattern"] == "X1" and relayed["pattern"] == "X4" and relayed["relay"] == ["d3"]
    assert relayed["ipa"] != direct["ipa"]  # (squeezed through the relay's three sounds on the way)


def test_speakers_call_others_mutes():
    rows = {"human": {"orc": {"valence": "exotic", "basis": "x", "since_kyr": 1.0, "strength": 0.5, "from_dir": "north"}}}
    res, run = _world(rows)
    P = NM._Pass(res, run, 11, None)
    P.patterns["human"] = "speakers"
    P.endonyms = {}
    x = P.exonym("human", "orc", rows["human"]["orc"])
    assert x["pattern"] == "X3" and "MUTE" in x["parts"]


# ---------------------------------------------------------------------------------------------- places
def test_river_named_before_a_shift_keeps_its_form():
    inv = INV.draw_inventory(np.random.default_rng(5), PR.HUMAN)
    old = _mk("d1", "human", 1, 6, inv=inv, born=2.0, died=1.0)
    ruler = _mk("d2", "orc", 2, 7, inv=inv, born=2.0)
    new = ruler.copy("d1.1", 1, 1.0, "shift")
    new.people, new.substrate = "human", "d1"
    res = {"lects": [old, ruler, new], "seed": 2,
           "shifts": [{"deme": 1, "kyr": 1.0, "from_lect": "d1", "to_lect": "d1.1", "ruler_lect": "d2"}]}
    run = FakeRun([_deme(0, "x"), _deme(1, "human"), _deme(2, "orc")], {p: _line(p) for p in ("human", "orc")},
                  landscape={1: {"river": 7, "river_flow": 500.0}, 2: {}})
    landscape = {"rivers": {"7": {"demes": [[1, 2.0], [2, 0.5]]}}, "lakes": {}}
    names = NM.build_names(res, run, landscape=landscape)
    riv = next(p for p in names["demes"]["1"]["places"] if p["kind"] == "river")
    P = NM._Pass(res, run, 2, landscape)
    base = P._base_name(old, "river", 7)
    assert riv["named_by"] == "d1" and riv["substrate_of"] == "d1" and riv["pattern"] == "P2" and riv["kyr"] == 2.0
    assert riv["ipa"] == word_ipa(base["form"])  # (same inventory: heard unchanged)
    fresh = P._base_name(new, "river", 7)
    assert word_ipa(fresh["form"]) != riv["ipa"]  # (the newcomers' own words would have made another name)
    assert "shifted" in riv["plain"]


# ---------------------------------------------------------------------------------------------- brief
def test_names_for_brief_plain_words():
    rows = {"human": {"orc": {"valence": "feared", "basis": "incursion: orcs settled among humans", "since_kyr": 1.0, "strength": 0.8}},
            "elf": {"orc": {"valence": "exotic", "basis": "some contact", "since_kyr": 1.0, "strength": 0.4, "from_dir": "east"}}}
    res, run = _world(rows)
    names = NM.build_names(res, run)
    nb = NM.names_for_brief(names, "orc")
    assert nb["headword"] == names["peoples"]["orc"]["endonym"]["roman"]
    assert len(nb["exonyms"]) == 2 and nb["exonyms"][0]["said_by"] == "human" and nb["exonyms"][0]["pattern"] == "X5"
    assert len(nb["etymologies"]) == 3 and all(isinstance(e, str) and "'" in e for e in nb["etymologies"])
    assert nb["etymologies"][0].startswith(nb["headword"]) and "from " in nb["etymologies"][0]
    assert NM.names_for_brief(names, "nobody") is None


def _tiny_doc():
    return {"names": {"peoples": {"human": {
        "endonym": {"ipa": "kalima", "roman": "Kalima", "gloss": "the real people", "pattern": "E2",
                    "plain": "Kalima, 'the real people': from kali 'real' + -ma, the people class"},
        "glossonym": {"ipa": "kalilu", "roman": "Kalilu", "gloss": "the speech of the real people", "pattern": "class manner"},
        "exonyms": [{"roman": "Tokala", "by_people": "orc", "gloss": "the northerners", "pattern": "X8", "basis": "some contact",
                     "strength": 0.5, "relay": [], "plain": "Tokala, 'the northerners': from to 'north' + kala 'people'"}]}},
        "demes": {}},
        "lects": [{"id": "d0", "people": "orc", "deme": 0, "died_kyr": None, "population": 10.0, "lexicon": {"crop:wheat": {"ipa": "pura", "roman": "pura"}}},
                  {"id": "d1", "people": "human", "deme": 1, "died_kyr": None, "population": 10.0, "lexicon": {"crop:wheat": {"ipa": "bula", "roman": "bula"}}}],
        "food_routes": [{"concept": "crop:wheat", "origin_lect": "d0", "origin_deme": 0, "kyr": 3.0, "ipa": "pura", "roman": "pura",
                         "origin": "tamed here", "hops": [{"deme": 1, "lect": "d1", "kyr": 2.5, "ipa": "bula", "roman": "bula",
                                                           "from_deme": 0, "from_lect": "d0", "from_ipa": "pura", "changes": []}]}]}


def test_brief_languages_section_renders_and_degrades():
    sec = BR.languages_section(_tiny_doc(), ["human"], ["wheat"], [])
    h = sec["by_people"]["human"]
    assert h["headword"] == "Kalima" and h["exonyms"][0]["said_by"] == "orc"
    fw = h["food_words"][0]
    assert fw["concept"] == "crop:wheat" and fw["from_people"] == "orc" and "about 2.5 kyr ago" in fw["text"]
    md = BR.languages_md(sec)
    assert md[1] == "## Names and words" and any("Kalima" in x for x in md) and any("'bula'" in x for x in md)
    none = BR.languages_section(None, ["human"], ["wheat"], [])
    md0 = BR.languages_md(none)
    assert none["file"] is False and len([x for x in md0 if x.startswith("- ")]) == 1


def test_on_the_tiny_driver_run():
    from test_language_history import TinyRun
    from planet.language import history as H
    old = (H.RATE_SCALE, H.SHIFT_K, H.WORKERS)
    H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 240.0, 1.0, 1
    try:
        res = H.generate(None, run=TinyRun(), analyse=False)
    finally:
        H.RATE_SCALE, H.SHIFT_K, H.WORKERS = old
    a = NM.build_names(res, res["run"])
    b = NM.build_names(res, TinyRun())
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    living = [l for l in res["lects"] if l.alive and l.deme is not None]
    live = {k for k, v in a["demes"].items() if not v.get("gone")}   # (a gone deme keeps an entry for its ruins: PW-1604)
    assert {str(l.deme) for l in living} == live and all(a["demes"][str(l.deme)]["name"] for l in living)
    for v in a["demes"].values():
        assert all(x["roman"] and (x.get("kind") != "ruin" or x.get("abandoned_kyr") is not None)
                   for x in v.get("settlements") or [])
    assert set(a["peoples"]) == {res["run"].people_of(l.deme) for l in living}
    assert a["common"]["lect"] in {l.id for l in living}
    from planet.language import romanize as RO
    named = [v["endonym"] for v in a["peoples"].values()] + [pl for d in a["demes"].values() for pl in d["places"]]
    assert named and all(n["roman_full"] for n in named)  # the book spelling in roman, the full one in roman_full
    # (the book adds a mark only where its length style writes a long vowel with one, ā or á, which the workbench doubles)
    assert all(RO.diacritics(n["roman"]) <= RO.diacritics(n["roman_full"]) + n["ipa"].count("ː") for n in named)
    json.dumps(a)  # (the block is plain json)
    # personal names: every living lect has a tradition, given names (old and new) with etymologies, and bynames
    pn = a["personal"]
    assert set(pn) == {l.id for l in living}
    for lid, x in pn.items():
        assert x["tradition"]["given"] in ("dithematic", "phrase", "single") and x["given"], lid
        assert all(g["roman"][0].isupper() and g["ipa"] and g["etym"].startswith(g["roman"]) for g in x["given"])
        assert {g["age"] for g in x["given"]} <= {"old", "new"}
    # sister lects share their old names' tradition origin (inherited down the tree)
    trad = {l.id: pn[l.id]["tradition"] for l in living}
    assert len({v["origin"] for v in trad.values()}) < len(trad) or len(trad) == 1


def test_river_namer_weighted_by_population():
    """Among the demes on a river at its first naming, the namer is drawn by population: a numerous people usually names the
    water, a thin one (dragons) only sometimes."""
    inv = INV.draw_inventory(np.random.default_rng(5), PR.HUMAN)
    hum, drg = _mk("d1", "human", 1, 6, inv=inv), _mk("d2", "gold_dragon", 2, 7, inv=inv)
    run = FakeRun([_deme(0, "x"), _deme(1, "human"), _deme(2, "gold_dragon")], {p: _line(p) for p in ("human", "gold_dragon")})
    run.deme_population = lambda d, i: {1: 1000.0, 2: 100.0}[d]
    landscape = {"rivers": {str(r): {"demes": [[2, 2.0], [1, 2.0]]} for r in range(300)}, "lakes": {}}
    P = NM._Pass({"lects": [hum, drg], "seed": 2}, run, 2, landscape)
    picks = [P._first_on("river", r) for r in range(300)]
    assert all(k == 2.0 for _d, k in picks)
    share = sum(d == 2 for d, _k in picks) / len(picks)
    assert 0.1 < share < 0.4, share  # (expected sqrt(100)/(sqrt(1000)+sqrt(100)) = 0.24: the square-root weighting lets small peoples name a river now and then)
    assert picks == [P._first_on("river", r) for r in range(300)]  # deterministic
    landscape["rivers"]["9"] = {"demes": [[2, 1.0], [1, 2.0]]}  # the humans were there first: no draw
    assert P._first_on("river", 9) == (1, 2.0)


def test_name_caps_follow_the_length_scale():
    """A small-inventory CV language (long words) gets longer name parts and a higher name cap than MAX_SYLL; a
    mid-sized one keeps 2 and MAX_SYLL; long parts are clipped to the scaled caps, not to 4 syllables."""
    from dataclasses import replace
    base = _mk("d0", "human", 0, 1)
    assert NM._name_caps(base) == (2, NM.MAX_SYLL) or LX.length_scale(base.inventory) > 1.0
    c, v = list(from_ipa("ptkbs")), list(from_ipa("aiu"))
    small = replace(base.inventory, consonants=c, vowels=v, tones=[], shapes={"CV": 0.85, "V": 0.15}, max_onset=1,
                    max_coda=0, coda_class="any", onset_required=False, cost={x: 0.0 for x in c + v},
                    freq={x: 0.5 for x in c + v})
    assert LX.length_scale(small) > 1.5
    lc = LC.Lect(id="s0", deme=0, people="human", parent=None, how="proto", born_kyr=2.0, inventory=small,
                 lexicon=base.lexicon, grammar=base.grammar, profile=PR.HUMAN, population=1000.0)
    part, cap = NM._name_caps(lc)
    assert part >= 3 and cap > NM.MAX_SYLL
    long = tuple(from_ipa("pakatisubaki"))   # 6 syllables
    assert LX.syllables(NM._clip(long, lc)) == part and LX.syllables(NM._clip(long)) == 2


# ---------------------------------------------------------------------------------------------- faith, persons, settlements
def _with_files(tmp_path, run):
    gods = {"beings": [{"id": 0, "label": "god of sea and rain", "high": True, "devotion": 1.0, "individuation": 0.9,
                        "first_domain": "sea", "top": [["sea", 0.5]]}],
            "cultures": {"0": {"people": "human", "living": [0]}}}
    (tmp_path / "gods.json").write_text(json.dumps(gods))
    (tmp_path / "cultures.json").write_text(json.dumps({"deme_culture": [0, None, None]}))
    sites = {"sites": [{"id": 7, "cell": 5, "kind": "chief", "tier_now": "town", "pop_now": 3000, "founded_kyr": 1.5,
                        "founded_by": "orc", "abandoned_kyr": None},
                       {"id": 8, "cell": 6, "kind": "chief", "tier_now": "village", "pop_now": 300, "founded_kyr": 0.5,
                        "founded_by": "human", "abandoned_kyr": None}]}
    (tmp_path / "settlements.json").write_text(json.dumps(sites))
    run.dir = tmp_path
    run.deme_cells = lambda d, i: (np.array([5, 6]) if d == 0 else np.array([], int), None)
    run.river_id = lambda: np.zeros(10, int)
    return run


def test_faith_endonym_from_the_high_god(tmp_path):
    """E10: a people whose culture has a living high god can call itself after it ('the people of the sea god')."""
    res, run = _world()
    run = _with_files(tmp_path, run)
    P = NM._Pass(res, run, 11, None)
    assert P.high_god("human", 0)[0] == "SEA"
    n = P.endonym_in(P.main["human"], "human", "faith", {"faith": P.high_god("human", 0)})
    assert n["pattern"] == "E10" and n["variant"] == "faith" and "sea god" in n["gloss"] and n["parts"][-1] == "GOD"
    vs = {P.endonym_pattern("human")[0] for P.seed in range(60)}
    assert "faith" in vs


def test_patronymic_and_settlements(tmp_path):
    """A patronymic is the parent's name + GEN + SON/DAUGHTER in the lect's order; a deme's towns get names from its own
    words, and one founded by another people keeps their name as heard (P2)."""
    from planet.language import personal as PE
    res, run = _world()
    run = _with_files(tmp_path, run)
    a = NM.build_names(res, run)
    P = NM._Pass(res, run, 11, None)
    pe = PE.Personal(P)
    l = P.main["human"]
    t = dict(pe.tradition(l), byname="patronymic")
    given = [g for g in (pe._given(l, t, "new", i) for i in range(4)) if g]
    b = pe._byname(l, t, given, 0)
    assert b["kind"] == "patronymic" and "son of" in b["gloss"] and given[1]["roman"] in b["etym"]
    st = a["demes"]["0"]["settlements"]
    assert [s["site"] for s in st] == [7, 8] and st[0]["pattern"] == "P2" and st[0]["substrate_of"] == "d1"
    assert st[1]["pattern"] is None and st[1]["named_by"] == "d0" and all(s["roman"][0].isupper() for s in st)


# ---------------------------------------------------------------------------------------------- PW-1546: taxonomy processes
def test_relay_of_a_third_peoples_own_name():
    """X4: a thin-contact row borrowed from a third people is that people's own name for the subject, heard again (a24559
    had borrowed_from only on exotic and edge rows, so X4 never fired)."""
    res, run = _world()
    nb = {"valence": "neighbour", "basis": "neighbours", "since_kyr": 0.5, "strength": 0.9}
    run.meta["present"]["reputation"]["rows"] = {
        "elf": {"orc": dict(nb)},
        "human": {"orc": {"valence": "exotic", "basis": "hearsay", "since_kyr": 0.5, "strength": 0.3, "borrowed_from": "elf"}}}
    ex = {x["by_people"]: x for x in NM.build_names(res, run)["peoples"]["orc"]["exonyms"]}
    assert ex["human"]["pattern"] == "X4" and ex["human"]["relay"] == ["d2"] and "elf name for them" in ex["human"]["gloss"]


def test_misattributed_origin():
    """X9: the observer takes a thinly known people to come from a people it knows well in that direction."""
    res, run = _world()
    run.meta["present"]["reputation"]["rows"] = {"human": {
        "elf": {"valence": "neighbour", "basis": "neighbours", "since_kyr": 0.5, "strength": 0.9, "from_dir": "east"},
        "orc": {"valence": "exotic", "basis": "hearsay", "since_kyr": 0.5, "strength": 0.3, "from_dir": "east"}}}
    old = NM.X9_W
    NM.X9_W = 1e6
    try:
        x = next(x for x in NM.build_names(res, run)["peoples"]["orc"]["exonyms"] if x["by_people"] == "human")
    finally:
        NM.X9_W = old
    assert x["pattern"] == "X9" and "elf" in x["gloss"]


def test_conquerors_name_and_glossonym_drift():
    """P1: a deme of another people that shifted to the rulers' speech takes the rulers' name; the language can be named
    from another root ('our speech')."""
    res, run = _world()
    shifted = res["lects"][0].copy("d1.1", 1, 1.0, "shift")
    res["lects"][1].died_kyr = 1.0
    res["lects"].append(shifted)
    res["shifts"] = [{"deme": 1, "kyr": 1.0, "from_lect": "d1", "to_lect": "d1.1", "ruler_lect": "d0", "ruler_deme": 0,
                      "speakers": "orc", "ruler_people": "human"}]
    old = NM.P1_TAKE, NM.GLOSSONYM_W
    NM.P1_TAKE, NM.GLOSSONYM_W = 1.0, {"ours": 1.0}
    try:
        names = NM.build_names(res, run)
    finally:
        NM.P1_TAKE, NM.GLOSSONYM_W = old
    assert names["demes"]["1"]["name"]["pattern"] == "P1" and "human" in names["demes"]["1"]["name"]["gloss"]
    assert any(h["process"] == "P1" for h in names["peoples"]["orc"]["history"])
    assert all("our" in p["glossonym"]["gloss"] for p in names["peoples"].values())


def test_landmass_named_by_its_first_settlers():
    res, run = _world()
    run.meta["present"]["landmasses"] = [{"called": "Testa", "settled_by": {"by": "elf", "ago_kyr": 3000.0}}]
    res["lects"][0].population = 5000.0   # (the humans hold it today: they hear the elves' name)
    lm = NM.build_names(res, run)["landmasses"]["Testa"]
    assert lm["named_by"] == "d2" and lm["roman"] and lm["today"]["how"]


def test_name_length_by_tradition():
    """Item 14: a short tradition keeps given names short (Chinese-like), a long one joins three whole themes."""
    from planet.language import personal as PE
    from planet.language.lexicon import syllables
    res, run = _world()
    old = PE.NAME_LENGTH_W
    out = {}
    try:
        for k in ("short", "long"):
            PE.NAME_LENGTH_W = {k: 1.0}
            out[k] = NM.build_names(res, run)["personal"]
    finally:
        PE.NAME_LENGTH_W = old
    sh = [g for p in out["short"].values() for g in p["given"]]
    lo = [g for p in out["long"].values() for g in p["given"]]
    assert sh and lo and all(p["tradition"]["length"] == "short" for p in out["short"].values())
    mean = lambda gs: sum(syllables(from_ipa(g["ipa"])) for g in gs) / len(gs)  # noqa: E731
    assert mean(lo) > mean(sh)


# ---------------------------------------------------------------------------------------------- PW-1658 / PW-1654
def test_english_common_renders_meanings():
    """PW-1654: a name's meaning as an English compound with English's own generics (Grimsby-style founders)."""
    from planet.language import placenames as PL
    assert PL.english({"generic": "FORD", "spec": {"kind": "adj", "concept": "RED"}}, 1)[0] == "Redford"
    en, how = PL.english({"generic": "HOUSE", "spec": {"kind": "founder", "name": "Grïm"}}, 2)
    assert en in ("Grimsham", "Grimstead", "Grimsby") and "Grïm's" in how
    assert PL.english({"generic": None, "spec": {"kind": "descendants", "name": "Kato"}}, 3)[0] == "Katoings"
    assert PL.english({"generic": "MARKET", "spec": {"kind": "adj", "concept": "NEW"}}, 4)[0] in ("Newwick", "Chipping New")
    assert PL.anglicize("Ġèrrrhèlinè") == "Gerel" and PL.anglicize("Trrerhrris") == "Treris"


def test_english_unique_per_region_and_clean():
    """Two places of one region with the same English name are told apart by a qualifier; a river keeps one name along
    its course; nothing reads as a slur."""
    from planet.language import placenames as PL
    from planet.language import romanize as RO
    recs = [{"site": 1, "english": "Newton"}, {"site": 2, "english": "Newton"}, {"site": 3, "english": "Newton"},
            {"kind": "river", "id": 4, "english": "Redburn"}, {"kind": "river", "id": 4, "english": "Redburn"},
            {"site": 5, "english": "Newton", "reg": "b"}]
    PL.unique_english(recs, lambda r: r.get("reg", "a"))
    names = [r["english"] for r in recs]
    assert names[0] == "Newton" and len(set(names[:3])) == 3 and all(n.endswith("Newton") for n in names[:3])
    assert names[3] == names[4] == "Redburn" and names[5] == "Newton"
    assert all(RO.offensive(n.replace(" ", "")) is None for n in names)
    # a site listed in two regions takes a name free in both (site 21 sits in b and in a, where site 20 is Oakley)
    recs = [{"site": 20, "english": "Oakley", "reg": "a"}, {"site": 21, "english": "Oakley", "reg": "b"},
            {"site": 21, "english": "Oakley", "reg": "a"}]
    PL.unique_english(recs, lambda r: r["reg"])
    assert recs[0]["english"] == "Oakley" and recs[1]["english"] == recs[2]["english"] != "Oakley"


def test_naming_habits_inherited_and_rendered(tmp_path):
    """PW-1658: every settlement carries its family's habit, meaning, English Common name and naming history; sister
    lects share the habit their proto drew."""
    from planet.language import personal as PE
    res, run = _world()
    run = _with_files(tmp_path, run)
    a = NM.build_names(res, run)
    st = a["demes"]["0"]["settlements"]
    assert all(s["english"] and s["english"][0].isupper() and s["meaning"]["template"] == s["habit"] for s in st)
    assert all(s["history"] and s["history"][0][1] == s["named_by"] for s in st)
    assert st[0]["pattern"] == "P2" and st[0]["history"][-1][1] == st[0]["lect"]
    assert a["habits"] and all(h["template"] in ("suffix", "prefix", "possessive", "construct", "feature", "locative")
                               for h in a["habits"].values())
    P = NM._Pass(res, run, 11, None)
    pe = PE.Personal(P)
    for l in P.living:
        ch = pe.chain(l)
        assert pe.H.habit(l)["origin"] == ch[0].id   # (drawn by the proto at the root of the line)


def test_one_founding_per_site_across_demes(tmp_path):
    """Lane 15b: a site several demes list is founded once (one namer, one meaning, one habit); each deme hears it in its
    own form, and the English Common name is the same everywhere and translates that one meaning."""
    from planet.language import placenames as PL
    res, run = _world()
    d0 = res["lects"][0]   # a daughter of the human proto in a fourth deme, alive at both foundings: two human namers
    res["lects"].append(LC.Lect(id="d3", deme=3, people="human", parent="d0", how="split", born_kyr=1.8, died_kyr=None,
                                inventory=d0.inventory, lexicon=d0.lexicon, grammar=d0.grammar, profile=PR.HUMAN,
                                population=900.0))
    run.demes.append(_deme(3, "human"))
    run = _with_files(tmp_path, run)
    run.deme_cells = lambda d, i: (np.array([5, 6]), None)   # every deme lists both sites
    a = NM.build_names(res, run)
    recs: dict = {}
    for dm in a["demes"].values():
        for s in dm.get("settlements") or ():
            recs.setdefault(s["site"], []).append(s)
    assert any(len(v) > 1 for v in recs.values())
    for v in recs.values():
        assert len({json.dumps(s["meaning"], sort_keys=True) for s in v}) == 1
        assert len({s["named_by"] for s in v}) == len({s["english"] for s in v}) == len({s["habit"] for s in v}) == 1
        assert len({tuple(s["history"][0][1:4]) for s in v}) == 1   # (one founding record)
        for s in v:
            en, how = PL.english(s["meaning"], s["site"])
            assert s["english"].endswith(en) and s["english_how"].startswith(how)


def test_rendaku_voices_the_generic():
    """The feature habit voices the generic's first consonant in a compound (-kawa > -gawa) when the lect has the voiced
    counterpart, and leaves it alone otherwise."""
    from planet.language import placenames as PL

    class L:
        def __init__(self, segs):
            self._s = segs

        def segments(self):
            return self._s
    k, g, a = from_ipa("k")[0], from_ipa("g")[0], from_ipa("a")[0]
    assert PL.Habits._rendaku(L([k, g, a]), (k, a))[0] == g
    assert PL.Habits._rendaku(L([k, a]), (k, a))[0] == k


# ---------------------------------------------------------------------------------------------- PW-1739: output slips
def test_slip_scanner_catches_each_kind():
    names = {"demes": {"1": {"name": {"gloss": "named after the the river (Ka)"},
                             "places": [{"english": "Market The Black Sea", "gloss": "the land of the named after it"},
                                        {"english": "Loyings 2", "gloss": "the river river", "roman": "Ka''u"}]}},
             "personal": {"d1": {"bynames": [{"roman": "A" * 41, "kind": "patronymic"}]}}, "families": {}}
    s = NM.slips(names)
    assert all(s[k] for k in ("the_the", "doubled_word", "mid_the", "numbered", "double_apostrophe", "of_the_verb",
                              "long_full_name", "unnamed_family")), {k: len(v) for k, v in s.items()}


def test_glosses_never_double_the_article():
    assert NM._the("the river") == "the river" and NM._the("black river") == "the black river"
    assert NM._land_gloss("named after the river (Ka)") == "the land of the people named after the river"
    assert NM._land_gloss("the real people") == "the land of the real people"
    assert NM._land_gloss("the real people", "speech") == "the speech of the real people"
    assert NM._poss("Zing'") == "Zing's" and NM._poss("Grim") == "Grim's"


def test_unique_english_never_numbers():
    from planet.language.placenames import unique_english
    recs = [{"english": "Tezicstow", "english_how": "", "site": i, "_r": "west"} for i in range(60)]
    recs.append({"english": "The Black Sea", "english_how": "", "id": None, "_r": "west"})
    recs.append({"english": "The Black Sea", "english_how": "", "id": None, "_r": "west"})
    unique_english(recs, lambda r: r["_r"], lambda r: ([("river", "Blackwater"), ("peak", "Coldfell")], ["Ayson", "Brand"]))
    ens = [r["english"] for r in recs]
    assert len(set(ens)) == len(ens)
    assert not any(e.rsplit(" ", 1)[-1].isdigit() for e in ens), ens
    assert "Tezicstow-on-Blackwater" in ens and any(e.endswith(" Ayson") for e in ens)
    assert ens[-1].startswith("The ") and " The " not in ens[-1]


def test_names_on_the_tiny_run_have_no_slips():
    from test_language_history import TinyRun
    from planet.language import history as H
    old = (H.RATE_SCALE, H.SHIFT_K, H.WORKERS)
    H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 240.0, 1.0, 1
    try:
        res = H.generate(None, run=TinyRun(), analyse=True)
    finally:
        H.RATE_SCALE, H.SHIFT_K, H.WORKERS = old
    a = NM.build_names(res, res["run"])
    s = NM.slips(a)
    assert not any(s.values()), {k: v[:3] for k, v in s.items() if v}
    # living families and languages are named (PW-1739: the viewer showed fam0)
    living = [l for l in res["lects"] if l.alive and l.deme is not None]
    fams = {getattr(l, "family_scholars", None) for l in living} - {None}
    assert fams <= set(a["families"]) and all(a["families"][f]["name"].startswith("the ") for f in fams)
    true = {getattr(l, "family_true", None) for l in living} - {None}
    assert true <= set(a["scholars"]) and all(a["scholars"][f]["living"] for f in true)
    rows = (res.get("families") or {}).get("languages") or []
    assert rows and all(not r["name"].startswith("speech of") and r.get("where") for r in rows)
    # 20 given names where the tradition's pool allows; patronymics cut to a sane length
    pn = a["personal"]
    assert max(len(x["given"]) for x in pn.values()) > 6
    assert all(len(b["roman"].replace(" ", "")) <= NM.LONG_FULL_NAME for x in pn.values() for b in x["bynames"])
