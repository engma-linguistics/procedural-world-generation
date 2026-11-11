"""Machine-aware presets (planet/machine.py, PW-1720) and the viewer's low-detail choice (viewer/machinecore.js, PW-1721).
The probe inputs are made up: an 8 GB / 4-core laptop, a 32 GB / 8-core desktop and a 180 GB / 48-core workstation."""

import json
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from planet import api, appconfig as AC, machine as MC

LAPTOP = {"cores": 4, "ram_gb": 8.0, "disk_free_gb": 120.0, "gpu": {"name": "Intel UHD Graphics 620", "kind": "integrated"}}
DESKTOP = {"cores": 8, "ram_gb": 32.0, "disk_free_gb": 400.0, "gpu": {"name": "GeForce RTX 3060", "vram_gb": 12.0, "kind": "discrete"}}
WORKSTATION = {"cores": 48, "ram_gb": 180.0, "disk_free_gb": 700.0,
               "gpu": {"name": "NVIDIA RTX PRO 6000", "vram_gb": 102.6, "kind": "discrete"}}
# Daniel's Mac, a hand-test target: Apple silicon, 24 GB (sysctl hw.memsize = 24 GiB = 25.8 GB), cores as os.cpu_count
# counts them (performance + efficiency; 8 here, and the presets are the same up to 12)
MAC24 = {"os": "Darwin arm64", "cores": 8, "ram_gb": round(24 * 2**30 / 1e9, 1), "disk_free_gb": None,
         "gpu": {"name": "Apple M-series", "kind": "unified"}}
ALL = set(MC.PEAKS)


def _on(pr):
    return {k for k, v in pr["gates"].items() if v == "allow"}


def test_laptop_8gb_4_cores():
    pr = MC.presets_for(LAPTOP)
    assert pr["budget_gb"] == 5.6 and pr["spare_gb"] == 2.0 and pr["mem_cap_gb"] == 5
    assert pr["jobs"] == 1 and pr["default_level"] == 6 and pr["default_kyr"] == 1000
    assert pr["tile_levels"] == [] and pr["tile_at_once"] == 0  # (a level-1 tile alone needs 8.3 GB)
    assert pr["gates"]["make_l6"] == "warn"  # (3.9 GB fits 5.6 but not with 2 GB spare)
    assert _on(pr) == set()
    assert pr["low_detail"] == "on"


def test_desktop_32gb():
    pr = MC.presets_for(DESKTOP)
    assert pr["budget_gb"] == 24.0 and pr["spare_gb"] == 8.0
    assert pr["jobs"] == 2 and pr["default_level"] == 7
    assert pr["tile_levels"] == [1, 2, 3, 4] and pr["tile_at_once"] == 1  # (the ticket: tiles one at a time)
    g = pr["gates"]
    assert {k for k in ("split_1myr", "split_2myr", "make_l8", "refine_l9") if g[k] == "off"} == {
        "split_1myr", "split_2myr", "make_l8", "refine_l9"}  # (the ticket: L8 splits off)
    assert g["refine_l8"] == "allow" and g["peoples_1myr"] == "allow" and g["peoples_2myr"] == "warn"
    assert pr["default_kyr"] == 1000
    assert pr["low_detail"] == "auto"


@pytest.mark.parametrize("cores", [8, 10, 12])
def test_daniels_mac_24gb(cores):
    pr = MC.presets_for({**MAC24, "cores": cores})
    assert pr["budget_gb"] == 18.1 and pr["spare_gb"] == 6.5 and pr["mem_cap_gb"] == 18
    assert pr["jobs"] == 2 and pr["default_level"] == 7 and pr["default_kyr"] == 1000
    assert pr["tile_levels"] == [1, 2, 3, 4] and pr["tile_at_once"] == 1 and pr["tile_cache_gb"] == 60.0
    assert pr["low_detail"] == "auto"
    assert pr["gates"] == {"make_l6": "allow", "make_l7": "allow", "make_l8": "off", "peoples_1myr": "warn",
                           "peoples_2myr": "off", "refine_l8": "warn", "refine_l9": "off", "split_1myr": "off",
                           "split_2myr": "off", "tiles_l1": "allow", "tiles_l2": "allow"}


def test_workstation_180gb():
    pr = MC.presets_for(WORKSTATION)
    assert pr["budget_gb"] == 144.0 and pr["jobs"] == 4 and pr["tile_at_once"] == 3 and pr["default_level"] == 7
    assert _on(pr) == ALL and pr["default_kyr"] == 2000 and pr["tile_cache_gb"] == 60.0


def test_a_cgroup_cap_shrinks_the_presets():
    pr = MC.presets_for({**WORKSTATION, "cgroup_cap_gb": 32.0})
    assert pr["probed_ram_gb"] == 32.0 and pr["gates"]["split_1myr"] == "off" and pr["tile_at_once"] == 1


def test_more_ram_never_turns_a_gate_off():
    rank = {"off": 0, "warn": 1, "allow": 2}
    last = None
    for ram in range(2, 260, 2):
        g = MC.presets_for({"cores": 16, "ram_gb": float(ram)})["gates"]
        if last:
            assert all(rank[g[k]] >= rank[last[k]] for k in g), ram
        last = g


def test_peaks_cite_their_source():
    assert MC.PEAKS["tiles_l1"]["gb"] == api.TILE_PEAK_GB[1] and MC.PEAKS["split_2myr"]["gb"] == 69.3
    assert all(v["src"] and v["gb"] > 0 for v in MC.PEAKS.values())


def test_gpu_parsers():
    g = MC.parse_nvidia_smi("NVIDIA GeForce GTX 1050, 2048\nNVIDIA RTX A6000, 49140\n")
    assert g["name"] == "NVIDIA RTX A6000" and g["vram_gb"] == pytest.approx(51.5, abs=0.1)
    lspci = ("00:02.0 VGA compatible controller: Intel Corporation UHD Graphics 620 (rev 07)\n"
             "01:00.0 3D controller: NVIDIA Corporation GP108M [GeForce MX150] (rev a1)\n")
    assert MC.parse_lspci(lspci)["kind"] == "discrete"
    assert MC.parse_lspci(lspci.splitlines()[0])["kind"] == "integrated"
    assert MC.parse_lspci("nothing") is None
    assert MC.presets_for({"cores": 8, "ram_gb": 64, "gpu": {"kind": "discrete", "vram_gb": 1.0}})["low_detail"] == "on"


def _config(tmp_path, monkeypatch, probe=DESKTOP):
    p = tmp_path / "config.toml"
    p.write_text('data = "/x"\n\n[serve]\nport = 8765\n\n# [presets]  placeholder\n')
    monkeypatch.setenv("PLANET_CONFIG", str(p))
    monkeypatch.delenv("PLANET_PRESETS", raising=False)
    MC.write(MC.presets_for(probe), p)
    return p


def test_write_keeps_the_rest_and_reads_back(tmp_path, monkeypatch):
    p = _config(tmp_path, monkeypatch)
    cfg = tomllib.loads(p.read_text())
    assert cfg["data"] == "/x" and cfg["serve"]["port"] == 8765 and "placeholder" not in p.read_text()
    assert cfg["presets"]["jobs"] == 2 and cfg["presets"]["gates"]["split_2myr"] == "off"
    assert MC.active() and AC.presets()["tile_levels"] == [1, 2, 3, 4]
    MC.set_override("split_1myr", "warn", p)
    MC.write(MC.presets_for(WORKSTATION), p)  # (a new probe replaces the presets, keeps the overrides)
    cfg = tomllib.loads(p.read_text())
    assert cfg["presets"]["jobs"] == 4 and cfg["overrides"] == {"split_1myr": "warn"} and p.read_text().count("[presets]") == 1


def test_gates_refuse_warn_and_override(tmp_path, monkeypatch):
    p = _config(tmp_path, monkeypatch)
    spec = {"level": 7, "peoples": "dnd", "kyr": 2000}
    assert MC.make_gates(spec) == ["make_l7", "peoples_2myr"]
    out = MC.check(MC.make_gates(spec))
    assert out["refuse"] == [] and len(out["warn"]) == 1 and "20.3 GB" in out["warn"][0]
    out = MC.check(MC.make_gates({"level": 8, "peoples": "dnd", "kyr": 1000}))
    assert len(out["refuse"]) == 2 and "planet machine set make_l8 allow" in out["refuse"][0]
    MC.set_override("make_l8", "allow", p)
    assert len(MC.check(["make_l8", "split_1myr"])["refuse"]) == 1
    MC.set_override("make_l8", "auto", p)
    assert MC.state("make_l8") == "off"
    monkeypatch.setenv("PLANET_PRESETS", "off")
    assert MC.check(["make_l8"]) == {"refuse": [], "warn": []}
    with pytest.raises(ValueError):
        MC.set_override("nope", "allow", p)


def test_no_install_config_gates_nothing(monkeypatch):
    monkeypatch.delenv("PLANET_CONFIG", raising=False)
    assert not MC.active() and MC.state("split_2myr") == "allow" and MC.tile_settings() == {}
    assert MC.fill_defaults({"seed": 1}) == {"seed": 1}
    r = MC.report(live=LAPTOP)
    assert not r["applied"] and {g["gate"]: g["state"] for g in r["gates"]}["make_l7"] == "off"


def test_defaults_and_tile_settings(tmp_path, monkeypatch):
    p = _config(tmp_path, monkeypatch)
    monkeypatch.delenv("PLANET_TILE_CACHE_GB", raising=False)
    assert MC.fill_defaults({"seed": 1}) == {"seed": 1, "level": 7, "kyr": 1000}
    assert MC.fill_defaults({"level": 6, "kyr": 300}) == {"level": 6, "kyr": 300}
    assert MC.tile_settings() == {"at_once": 1, "cap_gb": 60.0, "levels": [1, 2, 3, 4]}
    _config(tmp_path, monkeypatch, LAPTOP)
    assert MC.tile_settings()["levels"] == []
    MC.set_override("tiles_l1", "allow", p)
    MC.set_override("tiles_l2", "warn", p)
    assert MC.tile_settings() == {"at_once": 1, "cap_gb": 24.0, "levels": [1, 2, 3, 4]}


def test_tile_service_skips_levels_that_are_off():
    from planet import tiles as T

    class Jobs:
        def __init__(self):
            self.n = []

        def submit(self, req):
            self.n.append(req)
            return str(len(self.n))

        def get(self, jid):
            return {"status": "queued"}

        def active_where(self, f):
            return None

    svc = T.TileService(Jobs(), cap_gb=1, levels=())
    assert svc.levels == frozenset()
    from planet.zoom import lod as L
    q = T._Queue()
    k = L.Key("px.1.1", 1, 0, 0)
    svc.worlds["w"] = q
    q.queue = [k]
    svc.built = lambda wid, key: None
    svc.evict = lambda: None
    svc.flush = lambda force=False: None
    svc.pump()
    assert svc.jobs.n == [] and "off on this machine" in svc.note


def test_cli_machine_probe_writes_the_config(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text('data = "/x"\n')
    out = subprocess.run(["uv", "run", "python", "-m", "planet", "machine", "probe", "--write", "--config", str(p)],
                         capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent, timeout=120)
    assert out.returncode == 0, out.stderr
    cfg = tomllib.loads(p.read_text())
    assert cfg["data"] == "/x" and set(cfg["presets"]["gates"]) == set(MC.PEAKS) and cfg["presets"]["jobs"] >= 1


def test_server_machine_endpoint(tmp_path, monkeypatch):
    from planet import server
    p = _config(tmp_path, monkeypatch)
    body, code = server.machine_get()
    assert code == 200 and body["applied"] and len(body["gates"]) == len(MC.PEAKS)
    body, code = server.machine_set(json.dumps({"gate": "split_2myr", "state": "warn"}).encode())
    assert code == 200 and {g["gate"]: g["state"] for g in body["gates"]}["split_2myr"] == "warn"
    assert server.machine_set(b'{"gate": "x", "state": "allow"}')[1] == 400
    body, code = server.submit(None, "/api/make", json.dumps({"seed": 3, "level": 8}).encode())
    assert code == 409 and "L8 worlds (run) is off" in body["error"]


# ---- the viewer's side (node) -----------------------------------------------------------------------------------------
_JS = r"""
const M = await import(process.argv[1]);
const intel = { renderer: 'ANGLE (Intel, Mesa Intel(R) UHD Graphics 620 (KBL GT2), OpenGL 4.6)', maxTexture: 16384, webgl2: true };
const nv = { renderer: 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060)', maxTexture: 32768, webgl2: true, deviceMemory: 8 };
const out = {
  intel: M.chooseDetail('auto', intel, 'auto'), nv: M.chooseDetail('auto', nv, 'auto'), nvPreset: M.chooseDetail('auto', nv, 'on'),
  forcedFull: M.chooseDetail('full', intel, 'on'), sw: M.chooseDetail('auto', { renderer: 'Google SwiftShader', webgl2: true }),
  arc: M.chooseDetail('auto', { renderer: 'Intel Arc A770', maxTexture: 16384, webgl2: true }),
  small: M.chooseDetail('auto', { renderer: 'x', maxTexture: 4096, webgl2: true }),
  low: M.lodSettings(M.DETAIL.low, '', 2), urlWins: M.lodSettings(M.DETAIL.low, '?lodpx=1.5&lodmax=4&dpr=2', 2),
};
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_low_detail_choice_in_the_viewer():
    core = Path(__file__).resolve().parent.parent / "viewer" / "machinecore.js"
    out = subprocess.run(["node", "--input-type=module", "-e", _JS, core.as_uri()], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    r = json.loads(out.stdout)
    assert r["intel"]["level"] == "low" and r["nv"]["level"] == "full" and r["nvPreset"]["level"] == "low"
    assert r["forcedFull"]["level"] == "full" and r["sw"]["level"] == "low" and r["arc"]["level"] == "full"
    assert r["small"]["level"] == "low"
    assert r["low"] == {"maxTiles": 40, "maxBytes": 120000000, "fetches": 2, "refinePx": 3, "maxLevel": 3, "dpr": 1}
    assert r["urlWins"] == {"maxTiles": 40, "maxBytes": 120000000, "fetches": 2}


def test_make_options_take_the_preset_defaults(tmp_path, monkeypatch):
    from planet import make
    _config(tmp_path, monkeypatch)
    d = {**make.options()["defaults"], **MC.fill_defaults({})}
    assert d["level"] == 7 and d["kyr"] == 1000


# ---- each OS's probe branch, with faked inputs (only Linux runs here) ------------------------------------------------
def test_os_kind():
    assert [MC.os_kind(s) for s in ("Linux", "Darwin", "Windows", "FreeBSD")] == ["linux", "mac", "windows", "other"]


def test_ram_readers_per_os():
    assert MC.parse_memtotal("MemTotal:       16384000 kB\nMemFree: 1 kB\n") == pytest.approx(16.777, abs=0.01)
    assert MC.parse_memtotal("garbage") is None
    assert MC.parse_memsize("17179869184\n") == pytest.approx(17.18, abs=0.01) and MC.parse_memsize("") is None

    class Kernel32:  # (GlobalMemoryStatusEx fills the struct it is given)
        def __init__(self, total, ok=1):
            self.total, self.ok = total, ok

        def GlobalMemoryStatusEx(self, ref):
            ref._obj.ullTotalPhys = self.total
            return self.ok

    assert MC.windows_ram_gb(Kernel32(8 * 2**30)) == pytest.approx(8.59, abs=0.01)
    assert MC.windows_ram_gb(Kernel32(8 * 2**30, ok=0)) is None
    assert MC.windows_ram_gb() is None  # (no windll here: the safe fallback)
    assert MC.total_ram_gb("FreeBSD") is None and MC.cgroup_cap_gb("Windows") is None and MC.cgroup_cap_gb("Darwin") is None


def test_mac_gpu_from_system_profiler():
    text = """Graphics/Displays:

    Apple M2 Pro:

      Chipset Model: Apple M2 Pro
      Type: GPU
      Total Number of Cores: 19

    AMD Radeon Pro 5500M:

      Chipset Model: AMD Radeon Pro 5500M
      VRAM (Total): 8 GB

    Intel UHD Graphics 630:

      Chipset Model: Intel UHD Graphics 630
      VRAM (Dynamic, Max): 1536 MB
"""
    g = MC.parse_system_profiler(text)
    assert g == {"name": "AMD Radeon Pro 5500M", "vram_gb": 8.0, "kind": "discrete"}
    m = MC.parse_system_profiler(text.split("    AMD")[0])
    assert m["kind"] == "unified" and m["vram_gb"] is None
    assert MC.parse_system_profiler("") is None


@pytest.mark.parametrize("probe,expect", [
    # a Windows laptop (GlobalMemoryStatusEx 16 GB; no nvidia-smi: the GPU is left to the viewer)
    ({"os": "Windows AMD64", "cores": 8, "ram_gb": 17.2, "disk_free_gb": 200.0, "gpu": {"name": None, "kind": "unknown"}},
     {"jobs": 1, "default_level": 7, "low_detail": "auto", "split_1myr": "off", "make_l7": "allow"}),
    # an Apple silicon MacBook (sysctl hw.memsize 16 GiB; unified GPU)
    ({"os": "Darwin arm64", "cores": 10, "ram_gb": 17.2, "disk_free_gb": 300.0,
      "gpu": {"name": "Apple M2 Pro", "kind": "unified"}},
     {"jobs": 1, "low_detail": "auto", "refine_l8": "warn", "tiles_l1": "warn", "tile_levels": []}),
    # an Ubuntu box whose RAM could not be read: planned for 32 GB, and said so
    ({"os": "Linux x86_64", "cores": 8, "ram_gb": None, "disk_free_gb": None, "gpu": {}},
     {"ram_known": False, "probed_ram_gb": 32.0, "tile_cache_gb": 60.0, "split_2myr": "off"}),
])
def test_presets_per_os(probe, expect):
    pr = MC.presets_for(probe)
    got = {k: pr["gates"].get(k, pr.get(k)) for k in expect}
    assert got == expect
    assert MC.describe(pr)  # (prints without a KeyError whatever was missing)
