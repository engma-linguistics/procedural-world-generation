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
    assert {str(l.deme) for l in living} == set(a["demes"]) and all(a["demes"][str(l.deme)]["name"] for l in living)
    assert set(a["peoples"]) == {res["run"].people_of(l.deme) for l in living}
    assert a["common"]["lect"] in {l.id for l in living}
    from planet.language import romanize as RO
    named = [v["endonym"] for v in a["peoples"].values()] + [pl for d in a["demes"].values() for pl in d["places"]]
    assert named and all(n["roman_full"] for n in named)  # the book spelling in roman, the full one in roman_full
    assert all(RO.diacritics(n["roman"]) <= RO.diacritics(n["roman_full"]) for n in named)
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
