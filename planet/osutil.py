"""The few things planet does that differ by OS (PW-1760: native Windows).

Linux and macOS keep the POSIX calls they always used (os.kill(pid, 0), fcntl.flock, /proc); each function here only
adds a Windows branch, chosen by sys.platform at call time (so tests can fake it). The Windows calls go through ctypes
(kernel32) and msvcrt, both in the standard library: no new dependency.

Why each one matters on Windows:
- pid_alive: Python's os.kill(pid, 0) on Windows is TerminateProcess, so asking whether a run is alive would end it.
- proc_start: a process's start time tells a run's own process from a later one given the same pid.
- lock_fd / unlock_fd: Windows has no fcntl; msvcrt.locking takes a byte-range lock that other processes wait on.
- replace: os.replace onto a file another process has open fails with PermissionError on Windows for a moment.
- fork_workers: Windows has no fork, so a pass that forks its workers runs in this process instead.
"""
from __future__ import annotations

import errno
import os
import sys
import time

try:
    import msvcrt
except ImportError:  # (Linux, macOS)
    msvcrt = None

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
ERROR_ACCESS_DENIED = 5


def is_windows() -> bool:
    return sys.platform == "win32"


def _kernel32():
    """kernel32 with the handle-returning functions typed (a HANDLE is 64 bits; ctypes' default int would cut it)."""
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.OpenProcess.restype = wintypes.HANDLE
    k.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    k.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    k.CloseHandle.argtypes = (wintypes.HANDLE,)
    k.GetLastError = lambda: ctypes.get_last_error()  # (the error saved right after the call, use_last_error)
    return k


def pid_alive(pid: int, kernel32=None) -> bool:
    """Whether process pid exists. POSIX: os.kill(pid, 0) (a PermissionError means it exists). Windows: OpenProcess and
    GetExitCodeProcess == STILL_ACTIVE, never os.kill (kernel32: a fake for tests)."""
    if not is_windows():
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            pass
        return True
    import ctypes
    try:
        k = kernel32 if kernel32 is not None else _kernel32()
        h = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return k.GetLastError() == ERROR_ACCESS_DENIED  # (it exists but is not ours to look at)
        try:
            code = ctypes.c_ulong(0)
            if not k.GetExitCodeProcess(h, ctypes.byref(code)):
                return True  # (it opened: it exists)
            return code.value == STILL_ACTIVE
        finally:
            k.CloseHandle(h)
    except (AttributeError, OSError, ValueError):
        return True  # (can't tell: never call a live run interrupted on a guess)


def proc_start(pid: int, kernel32=None) -> str | None:
    """When process pid started, as a string to compare, or None where it can't be read. Linux: /proc/<pid>/stat's
    field 22 (clock ticks since boot). Windows: GetProcessTimes' creation time (100 ns since 1601). macOS: None."""
    if not is_windows():
        from pathlib import Path
        try:
            return Path(f"/proc/{pid}/stat").read_text().rpartition(")")[2].split()[19]
        except (OSError, IndexError):
            return None
    import ctypes
    try:
        k = kernel32 if kernel32 is not None else _kernel32()
        h = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return None
        try:
            from ctypes import wintypes
            t = [wintypes.FILETIME() for _ in range(4)]
            if not k.GetProcessTimes(h, *(ctypes.byref(x) for x in t)):
                return None
            return str((t[0].dwHighDateTime << 32) | t[0].dwLowDateTime)
        finally:
            k.CloseHandle(h)
    except (AttributeError, OSError, ValueError):
        return None


# ---------------------------------------------------------------------------------------------- file locks (Windows)
LOCK_RETRY_S = 0.05


def lock_fd(fd: int) -> None:
    """Wait for an exclusive lock on fd's first byte (Windows: msvcrt.locking; held until unlock_fd). A no-op where
    msvcrt is missing: POSIX callers use fcntl.flock instead (store.lock)."""
    if msvcrt is None:
        return
    os.lseek(fd, 0, os.SEEK_SET)
    while True:
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return
        except OSError as e:
            if e.errno not in (errno.EACCES, errno.EDEADLOCK):
                raise
            time.sleep(LOCK_RETRY_S)


def unlock_fd(fd: int) -> None:
    """Release lock_fd's lock (Windows frees a closed handle's locks only eventually, so it is released first)."""
    if msvcrt is None:
        return
    os.lseek(fd, 0, os.SEEK_SET)
    try:
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        pass


# ---------------------------------------------------------------------------------------------- files and processes
REPLACE_TRIES = 40  # x 0.05 s: a reader holding the file open on Windows (an antivirus scan, the server sending it)


def replace(src, dst) -> None:
    """os.replace; on Windows, retried for up to ~2 s while another process has dst open (PermissionError)."""
    if not is_windows():
        os.replace(src, dst)
        return
    for i in range(REPLACE_TRIES):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == REPLACE_TRIES - 1:
                raise
            time.sleep(0.05)


def can_fork() -> bool:
    import multiprocessing as mp
    return "fork" in mp.get_all_start_methods()


def fork_workers(n: int) -> int:
    """n, or 1 where processes can't be forked (Windows): the language pass forks its workers (PW-1555)."""
    return n if can_fork() else 1


def parent_gone(parent: int) -> bool:
    """Whether a spawned worker's parent process has ended. POSIX: the worker is reparented (getppid changes).
    Windows never reparents (getppid keeps the old pid), so ask whether that pid still runs."""
    if not is_windows():
        return os.getppid() != parent
    return not pid_alive(parent)
