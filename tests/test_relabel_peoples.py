"""tools/relabel_peoples_runs.py (PW-1394): the one-off that gives peoples runs made before the kind 'peoples' their new label."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from planet import store as S

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "relabel_peoples_runs.py"


@pytest.fixture
def tool(tmp_path):
    S.set_root(tmp_path / "data")
    spec = importlib.util.spec_from_file_location("relabel_peoples_runs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    yield mod
    S.set_root(None)


def _run(rid, kind, phase=None):
    meta = {"kind": kind, **({"phase": phase} if phase else {}), "time_unit": "kyr", "source_run": "src", "at_myr": 1.0, "kyr": 5.0,
            "seed": 1, "level": 4, "myr": 40, "created": "2026-11-03 00:00:00", "timezoom": "tz1", "world": "w1"}
    d = S.runs_dir() / rid
    d.mkdir(parents=True)
    S.write_json(d / "run.json", {"format": "procgen-run/2", "kind": kind, "id": rid, "name": rid, "meta": meta,
                                  "grid": "g", "frames": [{"t": -1.0}, {"t": 0.0}]})
    return d / "run.json"


def test_relabel_only_touches_kind_and_phase(tool, tmp_path, monkeypatch, capsys):
    old, recent, tz = _run("pe1", "timezoom", "lineages"), _run("re1", "timezoom", "recent"), _run("tz1", "timezoom")
    before = {p: p.read_text() for p in (recent, tz)}
    was = json.loads(old.read_text())
    monkeypatch.setattr(sys, "argv", ["relabel", "--backup", str(tmp_path / "bk")])
    tool.main()  # (a dry run changes nothing)
    assert "1 peoples runs" in capsys.readouterr().out and json.loads(old.read_text()) == was
    monkeypatch.setattr(sys, "argv", ["relabel", "--backup", str(tmp_path / "bk"), "--apply"])
    tool.main()
    now = json.loads(old.read_text())
    assert now["kind"] == "peoples" and now["meta"]["kind"] == "peoples" and "phase" not in now["meta"]
    was["kind"] = was["meta"]["kind"] = "peoples"
    del was["meta"]["phase"]
    assert now == was  # (nothing else changed)
    assert json.loads((tmp_path / "bk" / "pe1.run.json").read_text())["meta"]["phase"] == "lineages"  # (the original is kept)
    assert {p: p.read_text() for p in (recent, tz)} == before  # (recent passes and time zooms are left alone)
    assert S._run_item(old)["kind"] == "peoples"
    assert not list(old.parent.glob("*.tmp")) and not list(old.parent.glob(".*.tmp"))
    capsys.readouterr()
    tool.main()  # (a second run finds nothing to do)
    assert "0 peoples runs" in capsys.readouterr().out
