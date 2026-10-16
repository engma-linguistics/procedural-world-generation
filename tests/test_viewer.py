"""The viewer's pages parse: each inline script (module or classic) is checked with
`node --check` (a syntax error, or a name declared twice, would leave the page
blank). Skipped where node isn't installed."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("page", ["index.html", "zoom.html"])
def test_viewer_scripts_parse(page, tmp_path):
    html = (VIEWER / page).read_text()
    scripts = re.findall(r'<script( type="module")?>(.*?)</script>', html, re.S)  # (not the importmap)
    assert scripts, f"no script in {page}"
    for k, (module, js) in enumerate(scripts):
        f = tmp_path / f"{page}.{k}.{'mjs' if module else 'cjs'}"
        f.write_text(js)
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, f"{page} script {k}:\n{r.stderr}"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("script", ["zoom3d.js"])
def test_viewer_modules_parse(script, tmp_path):
    """The viewer's own ES modules (zoom3d.js: the zoom's 3D view, PW-072)."""
    f = tmp_path / (Path(script).stem + ".mjs")
    f.write_text((VIEWER / script).read_text())
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, f"{script}:\n{r.stderr}"
