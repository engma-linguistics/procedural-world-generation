"""The installer (install.sh), the install config (planet/appconfig.py), the offline viewer and the RAM probe (PW-1716)."""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from planet import api, appconfig as AC

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "install.sh"


# ---------------------------------------------------------------------------------------------- install.sh
@pytest.mark.parametrize("shell", ["sh", "dash", "bash"])
def test_install_script_parses(shell):
    if shutil.which(shell) is None:
        pytest.skip(f"no {shell}")
    args = [shell, "--posix", "-n"] if shell == "bash" else [shell, "-n"]
    subprocess.run([*args, str(INSTALL)], check=True)


def _sandbox_env(tmp_path):
    """HOME and XDG dirs inside tmp_path: the script must never reach the real ones."""
    home = tmp_path / "home"
    home.mkdir()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("XDG_", "PLANET_", "PROCGEN_", "UV_")) and k != "VIRTUAL_ENV"}
    return {**env, "HOME": str(home)}


def _git_source(tmp_path):
    """A tiny git repo with two release tags, standing in for the release repo."""
    src = tmp_path / "src"
    (src / "planet").mkdir(parents=True)
    (src / "pyproject.toml").write_text('[project]\nname = "procgen-world"\nversion = "0.0.1"\n')
    (src / "install.sh").write_text(INSTALL.read_text())
    git = ["git", "-C", str(src), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(src)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "one"], check=True)
    for tag in ("v1.2.0", "v1.10.0", "v1.9.0", "not-a-release"):
        subprocess.run([*git, "tag", tag], check=True)
    return src


@pytest.mark.skipif(shutil.which("git") is None, reason="no git")
def test_install_dry_run_changes_nothing(tmp_path):
    env, root = _sandbox_env(tmp_path), tmp_path / "root"
    out = subprocess.run(["sh", str(INSTALL), "--dry-run", "--yes", "--root", str(root), "--source",
                          str(_git_source(tmp_path)), "--data", str(tmp_path / "data"), "--port", "8799"],
                         env=env, capture_output=True, text=True, check=True).stdout
    assert "version  v1.10.0" in out  # the newest v* tag, by version and not by text
    assert "uv sync --frozen --no-dev" in out and "Dry run done." in out
    assert "removing old version" not in out
    assert not root.exists() and not (tmp_path / "data").exists()
    assert not any((tmp_path / "home").iterdir())  # no launcher link, config or menu entry


def test_uninstall_dry_run_keeps_data_by_default(tmp_path):
    env, root, data = _sandbox_env(tmp_path), tmp_path / "root", tmp_path / "data"
    (root / "app").mkdir(parents=True)
    data.mkdir()
    (data / "keep").write_text("x")
    (root / "install.env").write_text(f"S_SOURCE='x'\nS_DATA='{data}'\nS_CONFIG='{tmp_path}/c/config.toml'\n"
                                      "S_BIN_LINK=''\nS_DESKTOP_FILE=''\n")
    run = lambda *a: subprocess.run(["sh", str(INSTALL), "uninstall", "--dry-run", "--yes", "--root", str(root), *a],
                                    env=env, capture_output=True, text=True, check=True).stdout
    out = run()
    assert f"Kept your data folder {data}" in out and (root / "app").is_dir()
    out = run("--delete-data")
    assert f"[dry-run] rm -rf {data}" in out and (data / "keep").exists()


def test_install_refuses_unknown_arguments(tmp_path):
    r = subprocess.run(["sh", str(INSTALL), "--frobnicate"], env=_sandbox_env(tmp_path), capture_output=True, text=True)
    assert r.returncode != 0 and "unknown argument" in r.stderr


def test_install_pins_uv_checksums():
    text = INSTALL.read_text()
    version = re.search(r"^UV_VERSION=(\S+)", text, re.M).group(1)
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert len(re.findall(r"\) echo [0-9a-f]{64} ;;", text)) == 4  # linux and mac, x86-64 and arm64


# ---------------------------------------------------------------------------------------------- the viewer offline
def test_viewer_loads_no_script_from_the_network():
    for p in (REPO / "viewer").rglob("*"):
        if p.suffix in (".html", ".js") and "vendor" not in p.parts:
            assert not re.search(r"https?://(cdn\.|unpkg|esm\.sh|cdnjs)", p.read_text()), p


def test_vendored_three_has_every_addon_the_viewer_imports():
    vendor = REPO / "viewer" / "vendor" / "three-r160"
    assert (vendor / "build" / "three.module.js").is_file()
    used = set()
    for p in (REPO / "viewer").rglob("*.js"):
        if "vendor" not in p.parts:
            used |= set(re.findall(r"""from\s+['"]three/addons/([^'"]+)['"]""", p.read_text()))
    for p in (REPO / "viewer").glob("*.html"):
        used |= set(re.findall(r"""from\s+['"]three/addons/([^'"]+)['"]""", p.read_text()))
        if "importmap" in p.read_text():
            assert "./vendor/three-r160/build/three.module.js" in p.read_text(), p
    assert used
    for rel in used:
        assert (vendor / "examples" / "jsm" / rel).is_file(), rel


# ---------------------------------------------------------------------------------------------- appconfig
def test_config_is_read_only_through_planet_config(tmp_path, monkeypatch):
    cfg = tmp_path / "config.toml"
    cfg.write_text('data = "/x"\n[serve]\nport = 8799\njobs = 2\n[presets]\nlevel = 7\n')
    monkeypatch.delenv("PLANET_CONFIG", raising=False)
    assert AC.load() == {} and AC.serve_defaults() == {}
    monkeypatch.setenv("PLANET_CONFIG", str(cfg))
    assert AC.serve_defaults() == {"port": 8799, "jobs": 2}
    assert AC.presets() == {"level": 7}


def test_pick_port_skips_a_taken_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen()
        taken = s.getsockname()[1]
        assert not AC.port_free(taken)
        assert AC.pick_port(taken, tries=5) not in (None, taken)
        assert not AC.is_planet_server(taken, timeout=0.5)


# ---------------------------------------------------------------------------------------------- free RAM (PW-1716)
MEMINFO = """MemTotal:       191000000 kB
MemFree:         2000000 kB
MemAvailable:   140500000 kB
Buffers:          100000 kB
"""

VM_STAT = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                3000.
Pages active:                            500000.
Pages inactive:                          200000.
Pages speculative:                         1000.
Pages throttled:                              0.
Pages wired down:                        150000.
Pages purgeable:                          10000.
"Translation faults":                 123456789.
Pages stored in compressor:              300000.
"""


def test_parse_meminfo():
    assert api.parse_meminfo(MEMINFO) == pytest.approx(140.5)
    assert api.parse_meminfo("MemTotal: 1 kB\n") is None


def test_parse_vm_stat():
    # free + inactive + speculative pages, 16 KiB each
    assert api.parse_vm_stat(VM_STAT) == pytest.approx((3000 + 200000 + 1000) * 16384 / 1e9)
    assert api.parse_vm_stat(VM_STAT.replace("16384", "4096")) == pytest.approx(204000 * 4096 / 1e9)
    assert api.parse_vm_stat("") is None
    assert api.parse_vm_stat("Mach Virtual Memory Statistics: (page size of 4096 bytes)\nPages active: 5.\n") is None


def test_free_ram_on_a_mac(monkeypatch):
    """No /proc: vm_stat answers; without it a quarter of hw.memsize, so the guards stay on."""
    monkeypatch.setattr(api, "Path", lambda p: Path("/nonexistent/meminfo"))
    monkeypatch.setattr(sys, "platform", "darwin")
    out = {"vm_stat": VM_STAT, "sysctl": "68719476736\n"}
    monkeypatch.setattr(api, "_run_text", lambda cmd: out.get(cmd[0]))
    assert api.free_ram_gb() == pytest.approx(204000 * 16384 / 1e9)
    out["vm_stat"] = None
    assert api.free_ram_gb() == pytest.approx(68719476736 * 0.25 / 1e9)
    out["sysctl"] = None
    assert api.free_ram_gb() is None


@pytest.mark.skipif(not Path("/proc/meminfo").exists(), reason="not Linux")
def test_free_ram_on_linux():
    assert api.free_ram_gb() > 0


def test_cgroup_room_reads_the_cap_and_ignores_uncapped():
    """PW-1731: inside a systemd-run MemoryMax scope the RAM guard sees the cap's room, not the host's free RAM."""
    from planet import api
    assert api.parse_cgroup_room("max\n", "123\n") is None
    assert abs(api.parse_cgroup_room("24000000000\n", "4000000000\n") - 20.0) < 1e-9
    assert api.parse_cgroup_room("1000\n", "5000\n") == 0.0
