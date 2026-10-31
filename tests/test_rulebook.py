"""Rulebook tool: offset logic always; PDF-backed checks only when the owner's local cache exists."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("rulebook", ROOT / "tools" / "rulebook.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)


def test_dmg_offset_is_zero():
    assert rb.printed_label("dmg", 303) == "303"


def test_phb_offsets_monotone_and_labelled():
    prev = 0
    for pdf in range(1, 294):
        lo, hi = rb.offset_range("phb", pdf)
        assert lo <= hi and lo >= prev
        prev = lo
    assert rb.printed_label("phb", 8) == "11"  # chapter 1 opens on p. 11
    assert rb.printed_label("phb", 100) == "106"
    assert rb.printed_label("phb", 213).endswith("?")  # between anchored stretches


def test_split_columns():
    text = "\n".join(f"left {i}      right {i}" for i in range(10))
    out = rb.split_columns(text)
    assert "left 3" in out.split("\n\n")[0] and "right 3" in out.split("\n\n")[1]


@pytest.mark.skipif(not (rb.CACHE / "dmg" / "p0303.txt").exists(), reason="local DMG cache absent")
def test_dmg_forest_and_grassland_have_gold_dragons():
    text = (rb.CACHE / "dmg" / "p0303.txt").read_text().lower()
    assert "green dragon" in text and text.count("gold dragon") >= 4
