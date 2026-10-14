"""issue-tracking/board.py: new, intake (number / reject / merge-into), check, next, decisions."""

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("board", REPO / "issue-tracking" / "board.py")
board = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(board)

DRAFT = """---
title: {title}
type: task
status: todo
parent: null
subsystem: {subsystem}
effort: {effort}
impact: {impact}
found_by: falls3
blocked_by: []
relates: []
refs: [planet/zoom.py, "zoom f81832"]
---

## Description
{desc}
"""


@pytest.fixture
def root(tmp_path):
    (tmp_path / "tickets").mkdir()
    (tmp_path / "inbox").mkdir()
    return tmp_path


def run(root, *argv):
    board.main(["--root", str(root), *argv])


def tickets(root):
    return board.Board(root).load()[0]


def new(root, title, effort="s", impact="med", subsystem="zoom", *extra):
    run(root, "new", "--type", "task", "--title", title, "--subsystem", subsystem,
        "--effort", effort, "--impact", impact, *extra)


def draft(root, name, title="Fix the thing", subsystem="zoom", effort="s", impact="med", desc="Why and what."):
    p = root / "inbox" / name
    p.write_text(DRAFT.format(title=title, subsystem=subsystem, effort=effort, impact=impact, desc=desc))
    return p


def check(root):
    with pytest.raises(SystemExit) as e:
        run(root, "check")
    return e.value.code


def test_new_numbers_and_validates(root, capsys):
    new(root, "First")
    new(root, "Second: with a colon", "m", "high", "climate", "--ref", "docs/overview.md")
    ts = tickets(root)
    assert sorted(ts) == ["PW-001", "PW-002"]
    t = ts["PW-002"]
    assert t["title"] == "Second: with a colon" and t["effort"] == "m" and t["refs"] == ["docs/overview.md"]
    assert t["_path"].name.startswith("PW-002-second-with-a-colon")
    assert check(root) == 0


def test_new_rejects_missing_parent(root):
    with pytest.raises(SystemExit):
        new(root, "Orphan", "s", "low", "zoom", "--parent", "PW-099")
    assert tickets(root) == {}


def test_intake_numbers_drafts_in_order(root, capsys):
    new(root, "Existing")
    draft(root, "draft-b.md", title="Bravo")
    draft(root, "draft-a.md", title="Alpha")
    run(root, "intake", "--list")
    out = capsys.readouterr().out
    assert "draft-a.md" in out and "Bravo" in out
    assert len(list((root / "inbox").glob("*.md"))) == 2  # --list changes nothing
    run(root, "intake")
    ts = tickets(root)
    assert ts["PW-002"]["title"] == "Alpha" and ts["PW-003"]["title"] == "Bravo"
    assert ts["PW-002"]["found_by"] == "falls3"
    assert ts["PW-002"]["refs"] == ["planet/zoom.py", "zoom f81832"]
    assert "Created from inbox draft draft-a.md" in ts["PW-002"]["_body"]
    assert not list((root / "inbox").glob("*.md"))
    assert check(root) == 0


def test_intake_leaves_bad_drafts(root, capsys):
    draft(root, "draft-good.md")
    draft(root, "draft-bad.md", subsystem="weather")
    with pytest.raises(SystemExit):
        run(root, "intake")
    assert list(tickets(root)) == ["PW-001"]
    assert [p.name for p in (root / "inbox").glob("*.md")] == ["draft-bad.md"]
    assert "bad subsystem 'weather'" in capsys.readouterr().out
    assert check(root) == 1  # check reports the bad draft too


def test_intake_reject(root, capsys):
    draft(root, "draft-dup.md")
    run(root, "intake", "--reject", "draft-dup.md", "duplicate of PW-004")
    assert not (root / "inbox" / "draft-dup.md").exists()
    assert "duplicate of PW-004" in capsys.readouterr().out
    assert tickets(root) == {}


def test_intake_merge_into(root):
    new(root, "Falls too small")
    draft(root, "draft-falls.md", title="Falls still small", desc="Seen on zoom 09c897.\n- 50 m at 10,000 m3/s")
    run(root, "intake", "--merge-into", "PW-001", "draft-falls.md")
    t = tickets(root)["PW-001"]
    assert len(tickets(root)) == 1
    assert "Merged inbox draft draft-falls.md" in t["_body"] and "Seen on zoom 09c897." in t["_body"]
    assert t["refs"] == ["planet/zoom.py", "zoom f81832"]
    assert not (root / "inbox" / "draft-falls.md").exists()
    assert check(root) == 0


def test_check_rejects_bad_fields(root, capsys):
    new(root, "Good")
    path = next((root / "tickets").glob("PW-001-*.md"))
    good = path.read_text()
    path.write_text(good.replace("effort: s", "effort: huge"))
    assert check(root) == 1
    assert "bad effort 'huge'" in capsys.readouterr().out
    path.write_text(good.replace("impact: med\n", "impact: med\npriority: high\n"))
    assert check(root) == 1
    assert "unknown field 'priority'" in capsys.readouterr().out
    path.write_text(good.replace("found_by: coordinator\n", ""))
    assert check(root) == 1
    assert "missing field 'found_by'" in capsys.readouterr().out
    path.write_text(good.replace("status: todo", "status: blocked"))
    assert check(root) == 1
    assert "blocked_by is empty" in capsys.readouterr().out
    path.write_text(good.replace("relates: []", "relates: [PW-777]"))
    assert check(root) == 1
    assert "relates PW-777 does not exist" in capsys.readouterr().out
    path.write_text(good)
    assert check(root) == 0


def test_check_parent_rank(root, capsys):
    new(root, "A task")
    run(root, "new", "--type", "story", "--title", "Story", "--subsystem", "zoom", "--effort", "m",
        "--impact", "med")
    path = next((root / "tickets").glob("PW-002-*.md"))
    path.write_text(path.read_text().replace("parent: null", "parent: PW-001"))
    assert check(root) == 1
    assert "story cannot sit under task PW-001" in capsys.readouterr().out


def test_next_ordering(root, capsys):
    new(root, "big-high", "l", "high")
    new(root, "small-low", "s", "low")
    new(root, "small-high", "s", "high")
    new(root, "xs-low", "xs", "low")
    new(root, "done-one", "xs", "high")
    run(root, "update", "PW-005", "fixed", "--status", "done")
    new(root, "other-subsystem", "xs", "high", "climate")
    capsys.readouterr()
    run(root, "next", "--subsystem", "zoom")
    titles = [ln.split()[-1] for ln in capsys.readouterr().out.splitlines()]
    assert titles == ["xs-low", "small-high", "small-low", "big-high"]
    run(root, "next", "--limit", "2")
    titles = [ln.split()[-1] for ln in capsys.readouterr().out.splitlines()]
    assert titles == ["other-subsystem", "xs-low"]
    new(root, "blocked-by-open", "xs", "high", "zoom", "--blocked-by", "PW-001")
    new(root, "blocked-by-done", "xs", "high", "zoom", "--blocked-by", "PW-005")
    capsys.readouterr()
    run(root, "next", "--subsystem", "zoom", "--limit", "1")
    assert capsys.readouterr().out.split()[-1] == "blocked-by-done"


def test_decisions(root, capsys):
    new(root, "Plain")
    run(root, "new", "--type", "task", "--title", "Lakes on which layers", "--subsystem", "viewer",
        "--effort", "s", "--impact", "low", "--status", "needs-decision",
        "--desc", "Options: A, B, C. Lean: C.")
    capsys.readouterr()
    run(root, "decisions")
    out = capsys.readouterr().out
    assert "PW-002" in out and "Lean: C." in out and "PW-001" not in out
    run(root, "update", "PW-002", "Owner: A is fine.", "--status", "done")
    capsys.readouterr()
    run(root, "decisions")
    assert "No tickets need a decision" in capsys.readouterr().out
    run(root, "morning")
    out = capsys.readouterr().out
    assert "## Decisions needed (0)" in out and "### viewer" in out and "Owner: A is fine." in out


def test_frontmatter_roundtrip():
    meta = {"id": "PW-001", "title": "Fix: the 'thing' #2", "type": "task", "status": "todo", "parent": None,
            "subsystem": "zoom", "effort": "s", "impact": "low", "found_by": "falls2 agent",
            "blocked_by": [], "relates": ["PW-002"],
            "refs": ["docs/plan_next.md", "zoom f81832", "a, b", "2026-10-14"],
            "created": board.today(), "updated": board.today()}
    assert board.parse_frontmatter(board.dump_frontmatter(meta)) == meta


@pytest.mark.skipif(shutil.which("jq") is None, reason="hook needs jq")
def test_hook_runs_check_from_edited_path(root, tmp_path):
    """The PostToolUse hook finds the repo from the edited file's path (a worktree)."""
    repo = tmp_path / "wt"
    (repo / "issue-tracking" / "tickets").mkdir(parents=True)
    shutil.copy(REPO / "issue-tracking" / "board.py", repo / "issue-tracking" / "board.py")
    hook = REPO / ".claude" / "hooks" / "issue_tracking_check.sh"
    bad = repo / "issue-tracking" / "tickets" / "PW-001-x.md"
    bad.write_text("---\nid: PW-001\n---\n")

    def fire(payload):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        return subprocess.run([str(hook)], input=json.dumps(payload), capture_output=True, text=True,
                              env=env, cwd=tmp_path)

    r = fire({"tool_name": "Write", "tool_input": {"file_path": str(bad)}, "cwd": str(tmp_path)})
    assert r.returncode == 2 and "missing field" in r.stderr
    r = fire({"tool_name": "Write", "tool_input": {"file_path": str(repo / "README.md")}, "cwd": str(repo)})
    assert r.returncode == 0
    r = fire({"tool_name": "Bash", "tool_input": {"command": "uv run python issue-tracking/board.py list"},
              "cwd": str(repo)})
    assert r.returncode == 2
    bad.unlink()
    r = fire({"tool_name": "Edit", "tool_input": {"file_path": str(bad)}, "cwd": str(tmp_path)})
    assert r.returncode == 0, r.stderr


def test_check_warns_on_dangling_data_refs(tmp_path, capsys):
    repo = tmp_path / "repo"
    root = repo / "issue-tracking"
    (root / "tickets").mkdir(parents=True)
    (root / "inbox").mkdir()
    for d in ("runs/fe7144", "zooms/f81832", "worlds"):
        (repo / d).mkdir(parents=True)
    (repo / "worlds" / "7c5adf.json").write_text("{}")
    new(root, "Refs", "s", "med", "zoom", "--ref", "run fe7144", "--ref", "world:7c5adf(1.0,2.0)",
        "--ref", "zoom:f81832", "--ref", "run:abcdef@40Myr(1,2)", "--desc", "Seen on world 000000.")
    capsys.readouterr()
    assert check(root) == 0  # a warning, not a failure
    assert "warning: 1 refs" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        run(root, "check", "--refs")
    out = capsys.readouterr().out
    assert "refs run abcdef" in out and "refs world 000000" in out and "fe7144" not in out
