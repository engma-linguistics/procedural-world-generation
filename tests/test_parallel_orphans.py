"""PW-543: pool workers exit on their own when the parent is SIGKILLed."""
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

SCRIPT = textwrap.dedent('''
    import os, time
    from planet import parallel

    def task(i, progress):
        return os.getpid()

    if __name__ == "__main__":
        pool = parallel.Pool(2, 1)
        futs = [pool.submit(task, i) for i in range(4)]
        pids = sorted({pool.result(f) for f in futs})
        print("PIDS", *pids, flush=True)
        time.sleep(120)  # (the test kills this process)
''')


def alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="uses /proc")
def test_workers_exit_when_parent_is_killed(tmp_path):
    script = tmp_path / "orphan_script.py"
    script.write_text(SCRIPT)
    env = {**os.environ, "PYTHONPATH": f"{REPO}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"}
    proc = subprocess.Popen([sys.executable, str(script)], cwd=REPO, env=env,
                            stdout=subprocess.PIPE, text=True)
    pids = []
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            line = proc.stdout.readline()
            if line.startswith("PIDS"):
                pids = [int(x) for x in line.split()[1:]]
                break
            if not line and proc.poll() is not None:
                break
        assert pids, "the pool script reported no worker pids"
        assert all(alive(p) for p in pids)
    finally:
        proc.send_signal(signal.SIGKILL)  # (only the process started here)
        proc.wait()
    deadline = time.time() + 8
    while time.time() < deadline and any(alive(p) for p in pids):
        time.sleep(0.2)
    left = [p for p in pids if alive(p)]
    for p in left:  # (these are this test's own workers: clean up before failing)
        os.kill(p, signal.SIGKILL)
    assert not left, f"workers outlived the killed parent: {left}"
