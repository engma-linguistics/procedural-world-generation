"""Machine-aware presets (PW-1720): what this machine can hold, written into the install's config.toml.

`planet machine probe` (and `planet self probe`, `planet self first-run`) reads the machine (probe()), works out the
presets (presets_for(), a pure function of the probe, so it is tested with made-up machines) and writes them into the
config's [presets] table (write()). The server, `planet make` and the viewer's Machine panel read them back.

The rule. A feature's measured peak memory (PEAKS, each with where it was measured) is set against the machine's
budget: SHARE of its RAM (the smaller of the physical RAM and a cgroup memory cap), the rest left to the system, the
browser and the user's own programs. A feature is
  - "allow" when its peak plus SPARE_GB fits in the budget,
  - "warn"  when the peak alone fits (it should finish if nothing else big runs),
  - "off"   when it does not fit: the server and `planet make` refuse it with a message, not an OOM.
The user can override any gate (the viewer's Machine panel, `planet machine set <gate> allow`); overrides live in the
config's [overrides] table, which a new probe keeps.

Only an install applies the presets: they are read through $PLANET_CONFIG (appconfig), which a checkout run never
sets, so a developer's checkout is never gated (active() is False there; the panel still shows the probe).
Numbers and where they come from: docs/review/plan/machine-presets.md.
"""
from __future__ import annotations

import math
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import api, appconfig as AC

# ---- measured peaks (GB of resident memory), each with its source --------------------------------------------------
PEAKS: dict[str, dict] = {
    "make_l6": {"label": "L6 worlds (planet make, 2 Myr time zoom)", "gb": 3.9,
                "src": "installer.md, end-to-end test: the L6 starter world, peak RSS 3.9 GB"},
    "make_l7": {"label": "L7 worlds (run and 2 Myr time zoom)", "gb": 6.6,
                "src": "two-myr.md section 2: L7 2 Myr time zoom 040d59, 6.6 GB peak (the run itself ~0.9 GB)"},
    "make_l8": {"label": "L8 worlds (run)", "gb": 30.0,
                "src": "milestones-to-v1.md section 4 (coordination.md): an L8 run peaks at 30 GB at its final write"},
    "peoples_1myr": {"label": "peoples history, 1 Myr time zoom (L7)", "gb": 14.5,
                     "src": "two-myr.md section 2: dnd peoples b74691 on a 1 Myr L7 zoom, 14.5 GB peak"},
    "peoples_2myr": {"label": "peoples history, 2 Myr time zoom (L7)", "gb": 20.3,
                     "src": "two-myr.md section 2: dnd peoples 580f8c on a 2 Myr L7 zoom, 20.3 GB peak"},
    "refine_l8": {"label": "refine a world to L8", "gb": 11.7,
                  "src": "two-myr.md section 2: refine of 6e2f17 to L8 (bcf4ba), 11.7 GB peak"},
    "refine_l9": {"label": "refine a world to L9", "gb": 39.0,
                  "src": "milestones-to-v1.md section 4 (PW-1262): refine to L9, 38 min, 39 GB"},
    "split_1myr": {"label": "L8 split peoples history, 1 Myr", "gb": 35.5,
                   "src": "two-myr.md section 2: split 025b98 (refine-l8/split.md), 35.5 GB peak"},
    "split_2myr": {"label": "L8 split peoples history, 2 Myr", "gb": 69.3,
                   "src": "two-myr.md section 2: split 1f49d0, 69.3 GB peak (lane 305's fix estimates ~35 GB, "
                          "not measured at L8: the measured number is used)"},
    "tiles_l1": {"label": "LOD zoom tiles, level 1 (4 km sections)", "gb": api.TILE_PEAK_GB[1],
                 "src": "api.TILE_PEAK_GB[1]: lanes 290, 295 measured 8.3-8.4 GB"},
    "tiles_l2": {"label": "LOD zoom tiles, levels 2-4 (1 km to 25 m)", "gb": api.TILE_PEAK_GB[2],
                 "src": "api.TILE_PEAK_GB[2]: lanes 301, 303 measured 4-4.9 GB"},
}
GATES = tuple(PEAKS)
STATES = ("allow", "warn", "off")

SPARE_GB = api.REFINE_RAM_SPARE_GB  # (8 GB: the spare the refine and zoom guards already keep)
SPARE_SHARE = 0.25  # ... but at most a quarter of the RAM (8 GB spare on an 8 GB laptop would forbid everything)
JOB_GB = PEAKS["make_l7"]["gb"]  # a typical heavy job: --jobs is at most budget / this
CORES_PER_JOB = 4  # and at most a job per 4 cores (each worker gets the cores shared out, planet/parallel.py)
MAX_JOBS = 4  # server.JOBS
TILE_AT_ONCE = 3  # tiles.AT_ONCE
TILE_CAP_GB = 60.0  # tiles.CAP_GB
TILE_CAP_DISK_SHARE = 0.2  # the tile cache takes at most a fifth of the free disk
DISK_REFUSE_GB, DISK_WARN_GB = 20, 50  # install.sh check_disk
L7_MIN_CORES = 8  # the default level is L7 only from 8 cores (milestones-to-v1.md section 4: the minimum machine)
LOW_VRAM_GB = 2.0  # under this the viewer starts in low detail (milestones-to-v1.md section 4)
LOW_RAM_GB = 16.0  # and on a machine with less RAM than this (the browser shares it)


def share_of(ram_gb: float) -> float:
    """The share of the RAM the app may use (milestones-to-v1.md section 4's per-process cap, an estimate)."""
    return 0.70 if ram_gb < 32 else 0.75 if ram_gb < 64 else 0.80


# ---- the probe ------------------------------------------------------------------------------------------------------
# One branch per OS (Linux, macOS, Windows), each with a safe fallback: what can't be read is None, and presets_for
# plans for the minimum machine's 32 GB when the RAM is unknown (and says so). Nothing here needs /proc, /sys, systemd
# or nvidia-smi to exist. The parsers take text (or a fake kernel32), so the tests run every OS's branch on Linux.
def _run(cmd: list[str]) -> str | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True).stdout
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def os_kind(system: str | None = None) -> str:
    """linux | mac | windows | other (platform.system())."""
    s = (system or platform.system()).lower()
    return "mac" if s == "darwin" else s if s in ("linux", "windows") else "other"


def parse_memtotal(text: str) -> float | None:
    """Linux /proc/meminfo -> MemTotal, GB."""
    m = re.search(r"^MemTotal:\s+(\d+)\s*kB", text or "", re.M)
    return int(m.group(1)) * 1024 / 1e9 if m else None


def parse_memsize(text: str) -> float | None:
    """macOS `sysctl -n hw.memsize` (bytes) -> GB."""
    t = (text or "").strip()
    return int(t) / 1e9 if t.isdigit() else None


def windows_ram_gb(kernel32=None) -> float | None:
    """Windows: GlobalMemoryStatusEx's ullTotalPhys, GB (kernel32: ctypes.windll.kernel32, or a fake for tests)."""
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        k = kernel32 if kernel32 is not None else ctypes.windll.kernel32  # (AttributeError off Windows)
        st = MEMORYSTATUSEX()
        st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not k.GlobalMemoryStatusEx(ctypes.byref(st)):
            return None
        return st.ullTotalPhys / 1e9 or None
    except (AttributeError, OSError, ValueError, TypeError):
        return None


def total_ram_gb(system: str | None = None) -> float | None:
    """Physical RAM, GB, by OS; None when it can't be read."""
    kind = os_kind(system)
    if kind == "linux":
        try:
            return parse_memtotal(Path("/proc/meminfo").read_text())
        except OSError:
            return None
    if kind == "mac":
        return parse_memsize(_run(["sysctl", "-n", "hw.memsize"]) or "")
    if kind == "windows":
        return windows_ram_gb()
    return None


def cgroup_cap_gb(system: str | None = None) -> float | None:
    """Linux only: the tightest cgroup v2 memory.max over this process (a container, or systemd-run MemoryMax), GB."""
    if os_kind(system) != "linux":
        return None
    try:
        rel = next(l.split("::", 1)[1].strip() for l in Path("/proc/self/cgroup").read_text().splitlines()
                   if l.startswith("0::"))
    except (OSError, StopIteration):
        return None
    parts, best = [x for x in rel.strip("/").split("/") if x], None
    for i in range(len(parts), 0, -1):
        try:
            m = (Path("/sys/fs/cgroup").joinpath(*parts[:i]) / "memory.max").read_text().strip()
        except OSError:
            continue
        if m.isdigit():
            best = int(m) / 1e9 if best is None else min(best, int(m) / 1e9)
    return best


def usable_cores() -> int:
    try:
        return len(os.sched_getaffinity(0))  # (Linux: honours taskset and cpusets)
    except (AttributeError, OSError):
        return os.cpu_count() or 1  # (macOS, Windows)


def parse_nvidia_smi(text: str) -> dict | None:
    """`nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits` -> the biggest GPU {name, vram_gb}."""
    best = None
    for line in (text or "").strip().splitlines():
        name, _, mib = line.rpartition(",")
        try:
            g = {"name": name.strip(), "vram_gb": round(float(mib) * 1.048576 / 1000, 1), "kind": "discrete"}
        except ValueError:
            continue
        if best is None or g["vram_gb"] > best["vram_gb"]:
            best = g
    return best


def _kind_of(name: str) -> str:
    low = name.lower()
    if re.search(r"virtio|vmware|qxl|bochs|basic (display|render)|llvmpipe|swiftshader", low):
        return "software"
    if "intel" in low and "arc" not in low:
        return "integrated"
    if "nvidia" in low or "arc" in low or re.search(r"radeon (rx|pro)", low):
        return "discrete"
    if re.search(r"apple m\d", low):
        return "unified"  # (Apple silicon: the GPU shares the RAM; capable, so not low detail by itself)
    return "unknown"


_ORDER = {"discrete": 0, "unified": 1, "unknown": 2, "integrated": 3, "software": 4}


def parse_lspci(text: str) -> dict | None:
    """Linux `lspci` -> the display controller {name, kind}: a discrete card is preferred to an integrated one."""
    found = []
    for line in (text or "").splitlines():
        if re.search(r"VGA compatible controller|3D controller|Display controller", line):
            name = line.split(": ", 1)[-1].strip()
            found.append({"name": name, "vram_gb": None, "kind": _kind_of(name)})
    return min(found, key=lambda g: _ORDER[g["kind"]]) if found else None


def parse_system_profiler(text: str) -> dict | None:
    """macOS `system_profiler SPDisplaysDataType` -> {name, vram_gb (a discrete card's), kind}."""
    found = []
    for block in re.split(r"\n(?=\s{4}\S[^\n]*:\n)", text or ""):
        m = re.search(r"Chipset Model:\s*(.+)", block)
        if not m:
            continue
        name = m.group(1).strip()
        v = re.search(r"VRAM \([^)]*\):\s*([\d.]+)\s*(MB|GB)", block)
        vram = None if not v else round(float(v.group(1)) / (1024 if v.group(2) == "MB" else 1), 1)
        found.append({"name": name, "vram_gb": vram, "kind": _kind_of(name)})
    return min(found, key=lambda g: _ORDER[g["kind"]]) if found else None


def probe_gpu(system: str | None = None) -> dict:
    """Coarse, by OS: nvidia-smi where it is installed (Linux and Windows), else lspci (Linux) or system_profiler
    (macOS); on Windows without nvidia-smi the GPU is left to the viewer, which reads WebGL's renderer string."""
    kind = os_kind(system)
    g = None
    if shutil.which("nvidia-smi"):
        g = parse_nvidia_smi(_run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]) or "")
    if g is None and kind == "linux" and shutil.which("lspci"):
        g = parse_lspci(_run(["lspci"]) or "")
    if g is None and kind == "mac":
        g = parse_system_profiler(_run(["system_profiler", "SPDisplaysDataType"]) or "")
    return g or {"name": None, "vram_gb": None, "kind": "unknown"}


def probe(data_root: Path | None = None) -> dict:
    """This machine: cores, RAM (and a Linux cgroup cap), free disk under the data root, the GPU (coarse)."""
    from . import store as S
    root = Path(data_root) if data_root else S.root()
    p = root
    while not p.exists() and p != p.parent:
        p = p.parent
    return {"cores": usable_cores(), "ram_gb": _r(total_ram_gb()), "cgroup_cap_gb": _r(cgroup_cap_gb()),
            "disk_free_gb": _r(api.free_disk_gb(p)), "data_root": str(root), "gpu": probe_gpu(),
            "os": f"{platform.system()} {platform.machine()}"}


def _r(x):
    return None if x is None else round(float(x), 1)


# ---- probe -> presets -----------------------------------------------------------------------------------------------
def gate(peak: float, budget: float, spare: float) -> str:
    return "allow" if peak + spare <= budget else "warn" if peak <= budget else "off"


def presets_for(p: dict) -> dict:
    """The presets for a probe (pure: the tests feed it made-up machines). Keys are written as they are into
    config.toml's [presets]; `gates` is its [presets.gates] table."""
    cores = max(1, int(p.get("cores") or 1))
    ram = p.get("ram_gb") or 0.0
    if p.get("cgroup_cap_gb"):
        ram = min(ram, p["cgroup_cap_gb"]) if ram else p["cgroup_cap_gb"]
    known = bool(ram)
    if not ram:  # (RAM unknown: plan for the minimum machine's 32 GB, milestones-to-v1.md section 4, and say so)
        ram = 32.0
    budget = round(share_of(ram) * ram, 1)
    spare = round(min(SPARE_GB, SPARE_SHARE * ram), 1)
    gates = {k: gate(v["gb"], budget, spare) for k, v in PEAKS.items()}
    if gates["tiles_l1"] == "off":  # (levels 2-4 read level 1: without it there are no tiles)
        gates["tiles_l2"] = "off"
    tile_levels = [] if gates["tiles_l1"] != "allow" else [1, 2, 3, 4] if gates["tiles_l2"] == "allow" else [1]
    at_once = 0 if not tile_levels else max(1, min(TILE_AT_ONCE, int((budget - spare) // PEAKS["tiles_l1"]["gb"])))
    jobs = max(1, min(MAX_JOBS, cores // CORES_PER_JOB, int(budget // JOB_GB)))
    level = 7 if gates["make_l7"] == "allow" and cores >= L7_MIN_CORES else 6
    disk = p.get("disk_free_gb")
    cache = TILE_CAP_GB if disk is None else max(1.0, min(TILE_CAP_GB, math.floor(TILE_CAP_DISK_SHARE * disk)))
    gpu = p.get("gpu") or {}
    vram = gpu.get("vram_gb")
    low = (gpu.get("kind") in ("integrated", "software") or (vram is not None and vram < LOW_VRAM_GB)
           or ram < LOW_RAM_GB)
    return {
        "probed_os": p.get("os") or "unknown", "ram_known": known,
        "probed_cores": cores, "probed_ram_gb": round(ram, 1), "probed_disk_free_gb": disk,
        "probed_gpu": gpu.get("name") or "unknown", "probed_vram_gb": vram,
        "budget_gb": budget, "spare_gb": spare,
        "mem_cap_gb": int(budget),
        "default_level": level,
        "default_kyr": 2000 if gates["peoples_2myr"] == "allow" else 1000,
        "jobs": jobs,
        "tile_at_once": at_once,
        "tile_levels": tile_levels,
        "tile_cache_gb": float(cache),
        "disk": "off" if disk is not None and disk < DISK_REFUSE_GB else "warn" if disk is not None and disk < DISK_WARN_GB
                else "allow",
        "low_detail": "on" if low else "auto",
        "gates": gates,
    }


# ---- reading them back ----------------------------------------------------------------------------------------------
def current(cfg: dict | None = None) -> dict:
    """The config's presets ({} in a checkout, or before a probe)."""
    return AC.presets(cfg)


def active(cfg: dict | None = None) -> bool:
    """Whether presets are applied (an install with a probed config), unless $PLANET_PRESETS=off."""
    return os.environ.get("PLANET_PRESETS", "").lower() not in ("off", "0", "no") and bool(current(cfg).get("gates"))


def overrides(cfg: dict | None = None) -> dict:
    o = (AC.load() if cfg is None else cfg).get("overrides") or {}
    return {k: v for k, v in o.items() if k in PEAKS and v in STATES}


def state(name: str, cfg: dict | None = None) -> str:
    """A gate's state as applied: the override, else the preset, else allow (no presets: nothing is gated)."""
    cfg = AC.load() if cfg is None else cfg
    if not active(cfg):
        return "allow"
    return overrides(cfg).get(name) or (current(cfg).get("gates") or {}).get(name, "allow")


def _why(name: str, pr: dict) -> str:
    pk = PEAKS[name]
    return (f"it peaks at about {pk['gb']:g} GB ({pk['src']}); this machine's budget is {pr.get('budget_gb', '?')} GB "
            f"of {pr.get('probed_ram_gb', '?')} GB RAM, with {pr.get('spare_gb', '?')} GB kept spare")


def check(names, cfg: dict | None = None) -> dict:
    """{"refuse": [...], "warn": [...]} for these gates (messages for the user)."""
    cfg = AC.load() if cfg is None else cfg
    pr, out = current(cfg), {"refuse": [], "warn": []}
    for n in dict.fromkeys(names):
        st = state(n, cfg)
        if st == "off":
            out["refuse"].append(f"{PEAKS[n]['label']} is off on this machine: {_why(n, pr)}. If you know better, "
                                 f"allow it in the viewer's Machine panel or with `planet machine set {n} allow`")
        elif st == "warn":
            out["warn"].append(f"{PEAKS[n]['label']} may not fit: {_why(n, pr)}. Close other big programs first")
    return out


def peoples_gate(level: int, kyr: float) -> str:
    """The gate of a peoples history on a world of `level` over a `kyr` time zoom (L6 and L7 use the L7 numbers: L6 is
    not measured, so the L7 peak is its upper bound; L8 and finer use the split's)."""
    long = kyr > 1000
    return ("split_2myr" if long else "split_1myr") if level >= 8 else ("peoples_2myr" if long else "peoples_1myr")


def make_gates(spec: dict) -> list[str]:
    """The gates a `planet make` / POST /api/make request crosses (spec: make.parse_make_request's)."""
    lv = int(spec["level"])
    out = [f"make_l{lv}"] if lv >= 6 else []
    if spec.get("peoples"):
        out.append(peoples_gate(lv, float(spec.get("kyr", 2000))))
    return out


def refine_gates(level: int) -> list[str]:
    return [f"refine_l{level}"] if level >= 8 else []


def lineages_gates(req: dict) -> list[str]:
    """The gate of a POST /api/lineages {world | timezoom} (the world's level and its time zoom's length)."""
    import json
    from . import store as S
    try:
        if req.get("world"):
            h = S.read_header(S.find_world(str(req["world"]).removesuffix(".json")))
            lv, kyr = int(h["meta"]["level"]), float(h["meta"].get("timezoom_kyr") or 2000)
        else:
            m = json.loads((S.find_run(str(req["timezoom"])) / "run.json").read_text())["meta"]
            lv, kyr = int(m["level"]), float(m["kyr"])
    except (KeyError, ValueError, OSError, SystemExit):
        return []
    return [peoples_gate(lv, kyr)]


def fill_defaults(req: dict, cfg: dict | None = None) -> dict:
    """A make request with the presets' default level and time zoom length where it gives none."""
    if not active(cfg):
        return req
    pr = current(cfg)
    out = dict(req)
    if out.get("level") in (None, "") and pr.get("default_level"):
        out["level"] = int(pr["default_level"])
    if out.get("kyr") in (None, "") and pr.get("default_kyr"):
        out["kyr"] = int(pr["default_kyr"])
    return out


def tile_settings(cfg: dict | None = None) -> dict:
    """{cap_gb, at_once, levels} for the tile service ({} unless presets apply; $PLANET_TILE_CACHE_GB still wins)."""
    cfg = AC.load() if cfg is None else cfg
    if not active(cfg):
        return {}
    pr = current(cfg)
    out = {"at_once": int(pr.get("tile_at_once", TILE_AT_ONCE))}
    if pr.get("tile_cache_gb") and not os.environ.get("PLANET_TILE_CACHE_GB"):
        out["cap_gb"] = float(pr["tile_cache_gb"])
    levels = set(pr.get("tile_levels", [1, 2, 3, 4]))
    ov = overrides(cfg)
    if ov.get("tiles_l1") in ("allow", "warn"):
        levels.add(1)
    if ov.get("tiles_l2") in ("allow", "warn") and 1 in levels:
        levels |= {2, 3, 4}
    if ov.get("tiles_l1") == "off":
        levels = set()
    if ov.get("tiles_l2") == "off":
        levels -= {2, 3, 4}
    out["levels"] = sorted(levels)
    out["at_once"] = max(1, out["at_once"])  # (with no level on, the level filter blocks and says why: tiles.pump)
    return out


def report(cfg: dict | None = None, live: dict | None = None) -> dict:
    """GET /api/machine: the presets as applied (or, in a checkout, worked out from a live probe and not applied),
    each gate with its state, the preset's state, its peak and source."""
    cfg = AC.load() if cfg is None else cfg
    on = active(cfg)
    pr = current(cfg) if on else presets_for(live if live is not None else probe())
    ov = overrides(cfg)
    gates = [{"gate": k, "label": v["label"], "peak_gb": v["gb"], "source": v["src"],
              "preset": (pr.get("gates") or {}).get(k, "allow"), "override": ov.get(k),
              "state": state(k, cfg) if on else (pr.get("gates") or {}).get(k, "allow")} for k, v in PEAKS.items()]
    return {"applied": on, "config": str(AC.path()) if AC.path() else None, "can_save": AC.path() is not None,
            "presets": {k: v for k, v in pr.items() if k != "gates"}, "gates": gates}


# ---- writing them ---------------------------------------------------------------------------------------------------
def _toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _table(name: str, d: dict, comment: str = "") -> list[str]:
    out = [f"[{name}]" + (f"  # {comment}" if comment else "")]
    out += [f"{k} = {_toml_value(v)}" for k, v in d.items() if v is not None and not isinstance(v, dict)]
    return out


def replace_tables(text: str, tables: dict[str, list[str]]) -> str:
    """The config text with these tables (and their sub-tables) replaced, or appended; the placeholder comment
    install.sh writes ("# [presets] ...") goes. Everything else is kept as it is."""
    lines, out, skip = text.splitlines(), [], False
    names = tuple(tables)
    for line in lines:
        s = line.strip()
        m = re.match(r"\[\s*([A-Za-z0-9_.\-]+)\s*\]", s)
        if m:
            skip = m.group(1).split(".")[0] in names
        if re.match(r"#\s*\[presets\]", s):
            continue
        if not skip:
            out.append(line)
    while out and not out[-1].strip():
        out.pop()
    for body in tables.values():
        out += [""] + body
    return "\n".join(out) + "\n"


def write(pr: dict, path: Path, probe_info: dict | None = None) -> None:
    """Write the presets into the config at path ([presets] and [presets.gates] replaced; [overrides] kept)."""
    import tomllib
    text = path.read_text() if path.is_file() else ""
    body = _table("presets", pr, "machine-aware presets: written by `planet machine probe`, a new probe replaces them")
    body += [""] + _table("presets.gates", pr.get("gates") or {}, "allow | warn | off; change one in [overrides]")
    new = replace_tables(text, {"presets": body})
    tomllib.loads(new)  # (never write a file that would not read back)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(new)
    tmp.replace(path)


def set_override(name: str, value: str | None, path: Path) -> dict:
    """Set (or with value None / "auto", clear) a gate's override in the config's [overrides]; the overrides now."""
    import tomllib
    if name not in PEAKS:
        raise ValueError(f"no gate {name!r}; the gates: {', '.join(PEAKS)}")
    if value not in (None, "auto", *STATES):
        raise ValueError("an override is allow, warn, off or auto")
    text = path.read_text() if path.is_file() else ""
    ov = dict((tomllib.loads(text).get("overrides") or {}) if text else {})
    if value in (None, "auto"):
        ov.pop(name, None)
    else:
        ov[name] = value
    body = _table("overrides", ov, "your choices over the machine presets (the viewer's Machine panel writes them)") \
        if ov else []
    new = replace_tables(text, {"overrides": body}) if ov else replace_tables(text, {"overrides": []})
    tomllib.loads(new)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(new.rstrip("\n") + "\n")
    tmp.replace(path)
    return ov


def describe(pr: dict) -> list[str]:
    """The presets as lines for the terminal."""
    g = pr.get("gates") or {}
    disk = pr.get("probed_disk_free_gb")
    lines = [f"  machine   {pr['probed_cores']} cores, {pr['probed_ram_gb']:g} GB RAM, "
             f"{'?' if disk is None else f'{disk:g}'} GB free disk, GPU {pr['probed_gpu']}" + (f" ({pr['probed_vram_gb']:g} GB)" if pr.get("probed_vram_gb") else ""),
             *([] if pr.get("ram_known", True) else
               ["  (the RAM could not be read: planned for 32 GB, the minimum machine; check the gates yourself)"]),
             f"  budget    {pr['budget_gb']:g} GB for the app ({share_of(pr['probed_ram_gb']):.0%} of the RAM), "
             f"{pr['spare_gb']:g} GB kept spare beside each big job",
             f"  defaults  level {pr['default_level']}, {pr['default_kyr'] / 1000:g} Myr time zoom, {pr['jobs']} job(s) at once, "
             f"memory cap {pr['mem_cap_gb']} GB",
             f"  tiles     " + (f"{pr['tile_at_once']} at once, levels {pr['tile_levels']}" if pr["tile_levels"] else "off")
             + f", cache cap {pr['tile_cache_gb']:g} GB",
             f"  viewer    low detail {pr['low_detail']}"]
    for k, v in PEAKS.items():
        lines.append(f"  {g.get(k, 'allow'):<5}     {v['label']} (~{v['gb']:g} GB)")
    return lines
