"""PW-1760: the native Windows installer (install.ps1) and the OS branches of the runtime (planet/osutil.py), tested on
Linux with faked OS values: sys.platform, a fake kernel32 and a fake msvcrt. The real Windows and macOS proof is the
GitHub Actions run (.github/workflows/install-smoke.yml) and Daniel's Mac checklist (docs/review/plan/install-mac-checklist.md)."""
from __future__ import annotations

import errno
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from planet import api, machine as MC, osutil as OS, store as S

REPO = Path(__file__).resolve().parent.parent
INSTALL_SH = REPO / "install.sh"
INSTALL_PS1 = REPO / "install.ps1"


# ---------------------------------------------------------------------------------------------- a fake kernel32
class Kernel32:
    """OpenProcess / GetExitCodeProcess / GetProcessTimes / CloseHandle over a table {pid: (exit code, start)}."""

    def __init__(self, procs: dict, denied=()):
        self.procs, self.denied, self.err, self.closed = procs, set(denied), 0, []

    def OpenProcess(self, access, inherit, pid):
        assert access == OS.PROCESS_QUERY_LIMITED_INFORMATION
        if pid in self.denied:
            self.err = OS.ERROR_ACCESS_DENIED
            return 0
        if pid not in self.procs:
            self.err = 87  # (ERROR_INVALID_PARAMETER: no such process)
            return 0
        return 1000 + pid

    def GetLastError(self):
        return self.err

    def GetExitCodeProcess(self, h, ref):
        ref._obj.value = self.procs[h - 1000][0]
        return 1

    def GetProcessTimes(self, h, created, exited, kernel, user):
        start = self.procs[h - 1000][1]
        created._obj.dwHighDateTime, created._obj.dwLowDateTime = start >> 32, start & 0xFFFFFFFF
        return 1

    def CloseHandle(self, h):
        self.closed.append(h)
        return 1


@pytest.fixture
def windows(monkeypatch):
    """sys.platform = win32, a fake kernel32 (pid 4242 running, 4343 exited, 7 a system process), and os.kill fails
    the test if anything calls it (on Windows it would end the process)."""
    k = Kernel32({4242: (OS.STILL_ACTIVE, 133_000_000_000_000_123), 4343: (0, 5)}, denied={7})
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(OS, "_kernel32", lambda: k)

    def no_kill(*a):
        raise AssertionError("os.kill on Windows terminates the process")
    monkeypatch.setattr(os, "kill", no_kill)
    return k


# ---------------------------------------------------------------------------------------------- process liveness
def test_pid_alive_on_posix_unchanged():
    assert OS.pid_alive(os.getpid())
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    assert not OS.pid_alive(p.pid)


def test_pid_alive_on_windows_never_kills(windows):
    assert OS.pid_alive(4242)
    assert not OS.pid_alive(4343)  # (exited: its exit code is not STILL_ACTIVE)
    assert not OS.pid_alive(99999)  # (no such process)
    assert OS.pid_alive(7)  # (access denied: it exists)
    assert windows.closed == [1000 + 4242, 1000 + 4343]  # (every handle opened is closed)


def test_run_status_on_windows_reads_a_running_run_without_killing_it(windows, tmp_path):
    assert S._alive({"pid": 4242, "pid_start": "133000000000000123"})
    assert not S._alive({"pid": 4242, "pid_start": "1"})  # (a later process given the same pid)
    assert not S._alive({"pid": 4343, "pid_start": None})
    (tmp_path / "run.json").write_text('{\n"status": "running",\n"meta": {"pid": 4242, "pid_start": "133000000000000123"}\n}\n')
    assert S.run_status(tmp_path) == "running"


def test_proc_start(windows):
    assert OS.proc_start(4242) == "133000000000000123"
    assert OS.proc_start(99999) is None


@pytest.mark.skipif(not Path("/proc/self/stat").exists(), reason="not Linux")
def test_proc_start_on_linux_unchanged(monkeypatch):
    raw = Path(f"/proc/{os.getpid()}/stat").read_text().rpartition(")")[2].split()[19]
    assert OS.proc_start(os.getpid()) == raw == S.process_stamp()["pid_start"]


def test_parent_gone(monkeypatch, windows):
    assert not OS.parent_gone(4242) and OS.parent_gone(4343)
    monkeypatch.setattr(sys, "platform", "linux")
    assert not OS.parent_gone(os.getppid()) and OS.parent_gone(os.getppid() + 1)


# ---------------------------------------------------------------------------------------------- the file lock
class Msvcrt:
    LK_UNLCK, LK_LOCK, LK_NLCK, LK_RLCK, LK_NBLCK = 0, 1, 2, 3, 4

    def __init__(self, busy=0):
        self.calls, self.busy = [], busy

    def locking(self, fd, mode, n):
        assert os.lseek(fd, 0, os.SEEK_CUR) == 0 and n == 1  # (always the first byte)
        if mode == self.LK_NBLCK and self.busy:
            self.busy -= 1
            raise OSError(errno.EDEADLOCK, "busy")
        self.calls.append(mode)


def test_store_lock_on_windows_takes_and_releases_a_byte_lock(monkeypatch, tmp_path):
    m = Msvcrt(busy=2)  # (another process holds it for two tries)
    monkeypatch.setattr(S, "fcntl", None)
    monkeypatch.setattr(OS, "msvcrt", m)
    monkeypatch.setattr(OS, "LOCK_RETRY_S", 0.0)
    with S.lock(tmp_path, "zoom-x"):
        with S.lock(tmp_path, "zoom-x"):  # (re-entrant: one OS lock)
            assert m.calls == [m.LK_NBLCK]
    assert m.calls == [m.LK_NBLCK, m.LK_UNLCK]


def test_lock_fd_raises_other_errors(monkeypatch, tmp_path):
    class Bad(Msvcrt):
        def locking(self, fd, mode, n):
            raise OSError(errno.EBADF, "bad")
    monkeypatch.setattr(OS, "msvcrt", Bad())
    fd = os.open(tmp_path / "l", os.O_RDWR | os.O_CREAT)
    try:
        with pytest.raises(OSError):
            OS.lock_fd(fd)
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------------------------- files, fork, memory
def test_replace_retries_on_windows_while_the_file_is_open(monkeypatch, tmp_path):
    real, fails = os.replace, [2]

    def flaky(a, b):
        if fails[0]:
            fails[0] -= 1
            raise PermissionError("in use")
        real(a, b)
    monkeypatch.setattr(os, "replace", flaky)
    monkeypatch.setattr(OS.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "platform", "win32")
    (tmp_path / "a").write_text("new")
    OS.replace(tmp_path / "a", tmp_path / "b")
    assert (tmp_path / "b").read_text() == "new" and fails == [0]
    monkeypatch.setattr(sys, "platform", "linux")
    fails[0] = 1
    (tmp_path / "a").write_text("x")
    with pytest.raises(PermissionError):  # (Linux: no retry, as before)
        OS.replace(tmp_path / "a", tmp_path / "b")


def test_no_fork_means_one_language_worker(monkeypatch):
    import multiprocessing as mp
    assert OS.fork_workers(8) == (8 if "fork" in mp.get_all_start_methods() else 1)
    monkeypatch.setattr(mp, "get_all_start_methods", lambda: ["spawn"])
    assert OS.fork_workers(8) == 1


def test_anonymous_map_without_map_flags(monkeypatch):
    """Windows' mmap has no MAP_PRIVATE / MAP_ANONYMOUS: plates._mapped still gives a zeroed, writable array."""
    from planet.tectonics import plates
    monkeypatch.delattr(plates.mmap, "MAP_ANONYMOUS")
    a = plates._mapped((3, 5), "f4")
    assert a.shape == (3, 5) and not a.any()
    a[1, 2] = 7
    assert a.sum() == 7


def test_windows_free_ram(monkeypatch):
    class K:
        def GlobalMemoryStatusEx(self, ref):
            ref._obj.ullTotalPhys, ref._obj.ullAvailPhys = 32 * 10**9, 11 * 10**9
            return 1
    assert MC.windows_free_ram_gb(K()) == pytest.approx(11.0)
    assert MC.windows_ram_gb(K()) == pytest.approx(32.0)
    assert MC.windows_free_ram_gb() is None  # (no windll here)
    monkeypatch.setattr(api, "Path", lambda p: Path("/nonexistent/meminfo"))
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(MC, "windows_free_ram_gb", lambda: 11.0)
    assert api.free_ram_gb() == 11.0  # (the RAM guards are on)


# ---------------------------------------------------------------------------------------------- install.ps1
def _sh_uv_version():
    return re.search(r"^UV_VERSION=(\S+)", INSTALL_SH.read_text(), re.M).group(1)


def test_install_scripts_pin_the_same_uv():
    ps = INSTALL_PS1.read_text()
    assert re.search(r"^\$UV_VERSION = '([^']+)'", ps, re.M).group(1) == _sh_uv_version()
    sums = re.findall(r"'([a-z0-9_]+-pc-windows-msvc)' = '([0-9a-f]{64})'", ps)
    assert [t for t, _ in sums] == ["x86_64-pc-windows-msvc"]


def test_install_ps1_has_every_verb_of_install_sh():
    sh_verbs = re.search(r"^\s+install \| update \| ([^)]+)\) CMD=", INSTALL_SH.read_text(), re.M).group(1)
    verbs = {"install", "update", *[v.strip() for v in sh_verbs.split("|")]}
    ps = INSTALL_PS1.read_text()
    listed = set(re.findall(r"'([a-z-]+)'", re.search(r"\$verbs = ([^\n]+)", ps).group(1)))
    assert verbs == listed
    for v in verbs:
        assert f"'{v}' {{" in ps  # (dispatched in main)


def test_windows_launcher_is_safe():
    ps = INSTALL_PS1.read_text()
    launcher = ps[ps.index("@echo off"):ps.index('"@', ps.index("@echo off"))]
    lines = [l.strip() for l in launcher.splitlines()]
    # `self` (uninstall deletes bin\, update rewrites this .cmd) is handed to a copy in %TEMP% before it runs: started
    # without `call`, so cmd never reads the deleted file again (CI run 43124045149: "The system cannot find the path
    # specified." twice and exit 1 after a successful uninstall)
    assert lines.index('if /I not "%~1"=="self" goto run') < lines.index('if /I "%~dp0"=="%TEMP%\\" goto self')
    chain = next(l for l in lines if l.startswith("copy /y "))
    assert chain == 'copy /y "%~f0" "%TEMP%\\procgen_world-self.cmd" >nul && "%TEMP%\\procgen_world-self.cmd" %*'
    assert "call " not in chain
    self_at = lines.index(":self")
    assert lines.index(chain) == self_at - 1
    assert "manage.ps1" in lines[self_at + 1] and lines[self_at + 2] == "goto :eof" and lines[self_at + 3] == ":run"
    assert not any("manage.ps1" in l for l in lines[:self_at])  # (nothing runs the manager from the original file)
    assert 'set "PYTHONUTF8=1"' in launcher  # (3.14 on Windows still writes text in the ANSI code page)
    assert "Toml-Path $S.Data" in ps  # (no backslashes in the TOML string)
    assert not re.search(r"^\s*exit\b", ps.replace("if ($failed -and $ScriptFile) { exit 1 }", ""), re.M)  # (iex: never close the window)


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="no pwsh on this machine")
def test_install_ps1_parses():
    cmd = ("$e = $null; [System.Management.Automation.Language.Parser]::ParseFile("
           f"'{INSTALL_PS1}', [ref]$null, [ref]$e) | Out-Null; if ($e) {{ $e | ForEach-Object {{ $_.ToString() }}; exit 1 }}")
    subprocess.run(["pwsh", "-NoProfile", "-Command", cmd], check=True)


# ---------------------------------------------------------------------------------------------- install.sh: no git, macOS
def _env(tmp_path, **extra):
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("XDG_", "PLANET_", "PROCGEN_", "UV_")) and k != "VIRTUAL_ENV"}
    return {**env, "HOME": str(home), **extra}


def test_install_sh_uses_the_github_tarball_without_git(tmp_path):
    out = subprocess.run(["sh", str(INSTALL_SH), "--dry-run", "--yes", "--root", str(tmp_path / "root"), "--data",
                          str(tmp_path / "data"), "--source", "https://github.com/o/r.git", "--ref", "v1.2.3"],
                         env=_env(tmp_path, PROCGEN_NO_GIT="1"), capture_output=True, text=True, check=True).stdout
    assert "version  v1.2.3" in out
    assert "fetch https://github.com/o/r/archive/v1.2.3.tar.gz" in out and "git clone" not in out
    assert not (tmp_path / "root").exists()


@pytest.mark.parametrize("arch,major,msg", [("x86_64", "15", "Intel Macs are not supported"),
                                            ("arm64", "13", "macOS 13 is too old"),
                                            ("arm64", "15", None)])
def test_install_sh_mac_checks(tmp_path, arch, major, msg):
    fake = tmp_path / "fakebin"
    fake.mkdir()
    (fake / "uname").write_text(f'#!/bin/sh\ncase "$1" in -s) echo Darwin ;; -m) echo {arch} ;; *) echo Darwin ;; esac\n')
    (fake / "sw_vers").write_text(f"#!/bin/sh\necho {major}.1\n")
    for f in fake.iterdir():
        f.chmod(0o755)
    env = _env(tmp_path, PATH=f"{fake}:{os.environ['PATH']}", PROCGEN_NO_GIT="1")
    r = subprocess.run(["sh", str(INSTALL_SH), "--dry-run", "--yes", "--root", str(tmp_path / "root"), "--data",
                        str(tmp_path / "data"), "--source", "https://github.com/o/r", "--ref", "v1"],
                       env=env, capture_output=True, text=True)
    if msg:
        assert r.returncode != 0 and msg in r.stderr
    else:
        assert r.returncode == 0 and "aarch64-apple-darwin" in r.stdout and "Procgen World.command" not in r.stderr
