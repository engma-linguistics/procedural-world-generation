"""Contact kinds in borrowing (PW-1636, planet/language/contact.py): field profiles, meat and product splits, the
high register."""
import numpy as np
import pytest

from planet.language import contact as CT
from planet.language import inventory as I
from planet.language import lexicon as L


@pytest.fixture(scope="module")
def concepts():   # (the herd animals and their meat as a people that has met them: PW-1745 gates them by range)
    return [L.replace(c, proto=True) if c.domain == "animal" or c.id.startswith(L.MEAT_OF) else c for c in L.concepts()]


def _proto(seed, concepts, lect):
    rng = np.random.default_rng(seed)
    inv = I.draw_inventory(rng)
    return inv, L.proto_lexicon(rng, inv, concepts, 20.0, lect)


def test_profiles_mean_normalised(concepts):
    """Every profile averages 1 over the open-class list; closed-class words stay at 1; crops under trade at most 1."""
    open_ = [c.id for c in concepts if c.pos != "NAME" and CT.field_group(c.id) != "closed"]
    for kind in CT.RAW:
        assert abs(np.mean([CT.mult(kind, k) for k in open_]) - 1.0) < 1e-6, kind
        for k in ("I", "THOU", "WHO", "THIS", "ONE"):
            assert CT.mult(kind, k) == 1.0
        assert CT.mult(kind, "HUNDRED") == (3.0 if kind == "trade" else 1.0)   # p.numerals A (owner 2026-11-11)
    assert CT.mult("trade", "crop:wheat") <= 1.0
    assert CT.mult("elite", "LAW") > 2 and CT.mult("elite", "HAND") < 1 and CT.mult("elite", "meat:cattle") > 2
    assert CT.mult("trade", "MARKET") > 2 and CT.mult("trade", "LAW") < CT.mult("elite", "LAW")
    assert CT.mult("flat", "LAW") == CT.mult(None, "LAW") == 1.0


def test_trade_numerals_hook(monkeypatch):
    monkeypatch.setattr(CT, "TRADE_NUMERALS", {"HUNDRED": 3.0})
    assert CT.mult("trade", "HUNDRED") == 3.0 and CT.mult("elite", "HUNDRED") == 1.0 and CT.mult("trade", "ONE") == 1.0


def test_new_concepts(concepts):
    """P3: meats beside their animals (built as animal + MEAT compounds), and the trade, rule and law words (late)."""
    by = {c.id: c for c in concepts}
    for k in ("meat:cattle", "meat:pig", "meat:caprine", "meat:deer", "PRICE", "MONEY", "DEBT", "WEIGH", "LAW", "JUDGE",
              "TAX", "NOBLE"):
        assert k in by, k
    assert "meat:dog" not in by
    assert not by["MONEY"].proto and by["MONEY"].id in L.TECH_CONCEPT
    meta = {"animals": {"stocks": {"cattle": {}}}, "crops": {"stocks": {}}}
    ids = {c.id for c in L.concepts(meta)}
    assert "meat:cattle" in ids and "meat:pig" not in ids and "meat:deer" in ids
    _inv, lex = _proto(5, concepts, "P")
    w = lex["meat:cattle"]
    assert w.etym[-1].process == "compound:MEAT+animal:cattle"
    for parent, children in CT.splits().items():
        assert parent in by or L.resolve(parent) in by, parent
        for c, kd in children:
            assert c in by and kd in ("meat", "product"), c


def test_doublet_meat_split(concepts):
    """An elite donor's word for the animal comes in for its meat; the native animal word stays."""
    inv, lex = _proto(11, concepts, "R")
    _dinv, donor = _proto(12, concepts, "D")
    native = lex["animal:cattle"]
    new = L.borrow(donor["animal:cattle"], "D", lex, None, inv, 3.0, CT.channel("elite"), store=False)
    hits = 0
    for s in range(20):
        lx = lex.copy()
        r = CT.doublet(np.random.default_rng(s), lx, "animal:cattle", new, "D", "elite", {"D": donor}, None, inv, 3.0)
        if r is not None:
            hits += 1
            assert r == ("meat:cattle", "split")
            assert lx["animal:cattle"] is native and lx["meat:cattle"].form == new.form
            st = lx["meat:cattle"].etym[-1]
            assert st.process == "borrow:D" and "doublet" in st.note and "'cattle'" in st.note
            assert CT.kind_of_note(st.note) == "elite"
    assert 0 < hits < 20
    # a neighbour's loan never doubles
    assert CT.doublet(np.random.default_rng(0), lex.copy(), "animal:cattle", new, "D", "flat", {"D": donor}, None, inv,
                      3.0) is None


def test_register_doublet_lives_beside_and_finishes(concepts):
    inv, lex = _proto(21, concepts, "R")
    _dinv, donor = _proto(22, concepts, "D")
    k = "TABLE"
    assert L.concept_info(k).freq_class >= CT.REGISTER_MIN_FREQ
    new = L.borrow(donor[k], "D", lex, None, inv, 3.0, CT.channel("elite"), store=False)
    got = None
    for s in range(60):
        lx = lex.copy()
        got = CT.doublet(np.random.default_rng(s), lx, k, new, "D", "elite", {"D": donor}, None, inv, 3.0)
        if got is not None:
            break
    assert got == (CT.HIGH + k, "register")
    assert lx[k] is lex[k] and CT.HIGH + k in lx.words
    reg = CT.finish_registers(lx)
    assert CT.HIGH + k not in lx.words and reg[k][2] == "D" and lx.systems["registers"]["high"][k][1] in ("doublet",
                                                                                                         "synonym")


def test_step_uses_contact_kinds(concepts):
    """Under an elite donor, loans lean to the prestige fields and some come in as doublets; a flat donor makes none."""
    inv, base = _proto(31, concepts, "R")
    _dinv, donor = _proto(32, concepts, "D")
    out = {}
    for kind in ("elite", "flat"):
        lex = base.copy()
        L.step(np.random.default_rng(1), lex, 400.0, inv, contact_words={"D": donor}, kyr=5.0, lect_id="R",
               contact_weights={"D": 1.0}, contact_kinds={"D": kind})
        loans = [k for k, w in lex.words.items() if w.etym[-1].process == "borrow:D"]
        pres = sum(CT.field_group(k) in CT.PRESTIGE for k in loans) / max(len(loans), 1)
        out[kind] = (pres, lex.counts.get("doublet", 0), loans)
    assert out["elite"][0] > out["flat"][0]
    assert out["elite"][1] > 0 and out["flat"][1] == 0
