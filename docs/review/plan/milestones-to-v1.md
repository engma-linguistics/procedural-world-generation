# Milestones from here to v1.0 (1 December)

*Planning lane, 2026-11-11. Proposal only: nothing here is a ruling until Daniel or the coordinator says so. Every number
names the command or file it came from; anything marked **estimate** is mine.*

## In plain words

- You're well ahead of the plan. v0.2.0 was tagged 3 days early and v0.3.0 7 days early. Since 1 Nov about 27 lanes'
  worth of work merges a day.
- There are 20 days left. With about 4 lanes at once, one of them kept on physics, that's roughly 45 lane-days of milestone
  work plus 5 days of freeze. The must-haves that are left fill about 30 of those days, which leaves 10–15 days spare.
- Proposal: **v0.4.0 Sun 15 Nov** (states move inside the history; zooming like Google Earth reaches the ground), **v0.5.0
  Fri 20 Nov** (your December world on L8, every Seven Meals people right), **v0.6.0 Wed 25 Nov** (the installer, names on
  the map and the kitchen deepened; feature freeze), then the checklist walk over Thanksgiving and **v1.0.0 Tue 1 Dec**.
- **Installer:** a one-command bootstrap script built on uv, Linux first, with macOS as best effort and Windows through
  WSL2. It sets up its own Python, keeps your worlds in a data folder outside the code, puts a "Procgen World" launcher in
  your app menu, and has update and uninstall commands.
- **Stretch:** the installer measures the machine and picks safe settings. Under 32 GB it offers no L8; under 64 GB no
  L8 at 2 Myr. Minimum machine: 8 cores, 32 GB, 100 GB free. Recommended: 16+ cores, 64 GB, 250 GB SSD.
- Best use of the spare room, for the cookbook: a flavour profile on each culture's food sheet; how it preserves food and
  what it ferments; and how its kitchen changed through time.

---

## 1. v0.2 and v0.3 in brief

**v0.2.0, tagged Sat 7 Nov** (target Tue 10 Nov). 101 merges and 447 commits (`git log --merges --oneline v0.1.0..v0.2.0 | wc -l`, and without `--merges`).
- Faiths you write: gods as a tree per deme, faiths as records with 13 taboo kinds, and religion views (PW-1306, PW-1311, the PW-1308 children).
- A culture's food: the per-culture brief and the cuisine sheet v0 (PW-1391), food taboos per culture, and dates in years.
- Peoples' density comes from one sourced ladder (way of life × tech × land; PW-1275). Peoples no longer have groups (PW-1357).
  Hunters learn crops slowly (PW-1373).
- The milestone holds 275 done tickets (`board.py milestones`), many of them food and peoples groundwork from October.
  Four leftovers are still open: PW-728, PW-856, PW-1308 and PW-1312, nearly done.

**v0.3.0, tagged Tue 10 Nov** (target Tue 17 Nov), with the full suite passing (2033). 149 merges and 623 commits
(`v0.2.0..v0.3.0`).
- States and war v0: polities (chiefdoms, states, empires) and a Polities layer; war as a change of owner; one seam for
  polities pulled out of counter.py; tech draws keyed per people.
- Invasions you schedule, with an "it happened / it didn't" read-out (PW-756).
- Outside the milestone: the L7→L8 split history (PW-1265); a 2 Myr time zoom by default (PW-1661); Andes-type ranges
  (PW-1497); language lanes 11–16 with the real-inventory benchmark; the LOD plan and the sections API (PW-1674, PW-1675).

**Since v0.3.0** (36 merges, `v0.3.0..HEAD`):
- States inside the history, on by default (PW-1700; full suite 2097).
- Google Earth-style zooming steps 2–4: the on-demand tile service (PW-1690), seamless squares (PW-1699, PW-1705, PW-1708),
  the globe diving to the ground and tilting (PW-1688, PW-1696).

**Pace**

| measure | value | source |
|---|---|---|
| merges 1–10 Nov | 270 (0 on 6 Nov); 282 including the morning of 11 Nov | `git log --merges --since=2026-11-01 --format=%cd --date=short \| sort \| uniq -c` (`--oneline \| wc -l` = 282) |
| merges per day, last 3 days | 57 / 49 / 58 (8–10 Nov) | same |
| merges per day, v0.1→v0.2 vs v0.2→v0.3 | ~17/day (101 in 6 days) vs ~50/day (149 in 3 days) | tag ranges above |
| distinct lanes merged per day | 17 / 25 / 36 (8–10 Nov) | lane numbers in the merge subjects of the same log |
| tickets closed per day | ~26 (257 over 1–10 Nov) | done/wontdo tickets by `updated:` date (**approximate**: a later edit moves the date) |
| tickets created per day | ~44 (445 over 1–10 Nov) | `created:` in `issue-tracking/tickets/*.md` |
| open tickets | 778: later 560, unscheduled 148, v4 35, v5 21, v1.0 10, v2 4 | `board.py milestones`; frontmatter count |
| open by subsystem (top) | peoples 138, climate 109, culture 107, viewer 71, zoom 66, timezoom 54 | frontmatter count |

The pace is real, but the board is growing by about 18 tickets a day. The milestone lists below hold only must-haves and a
short list of extras.

## 2. Time left

- **20 days** from Wed 11 Nov to Tue 1 Dec. Thanksgiving is Thu 26 Nov.
- **Capacity (estimate):**
  - 4 lane slots on average (3–5). One is always held for physics (north star), which leaves **3 milestone slots × 15 days (11–25 Nov) ≈ 45 lane-days**.
  - A lane-day is one slot for one day. Lanes are short: 17–36 distinct lanes merged a day comes to 5–8 per slot per day.
  - The machine, not the agents, is the cap on heavy runs: ~32 cores and ~90 GB in the daytime, with per-process memory caps.
- **Already committed and still open:**
  - v1.0: 10 open (`board.py milestones v1.0`). These are the LOD chain (PW-1198, PW-1673, PW-1709, PW-1710, PW-1711, PW-1713;
    lanes 301 and 303 running), PW-1691 (the L8 split at 2 Myr peaks at 69 GB), PW-1672, PW-1678 and PW-1287.
  - v5: 21 open, the December world and Seven Meals: PW-1437 (the candidates are ready; Daniel stars one), PW-1558, PW-1184,
    PW-1257, PW-758, PW-1400, PW-1630, PW-1631, PW-1664, PW-1584, PW-730, PW-755, PW-1439 and others.
  - v4: 35 open, but its core has landed (states live, calendars, names slot, war dials). About 12 of the 35 are trade and
    languages work that is not a v4 "done when" line (PW-1498, PW-1508, PW-1532, PW-1533, PW-1649, PW-1650, PW-676 and others).
    **Groom them to `later` or v0.6** (see v0.4.0).

## 3. Proposed milestones

| tag | date | theme | lane-days (estimate) |
|---|---|---|---|
| v0.4.0 | Sun 15 Nov | History that moves, closed out; Google Earth zoom reaches the ground | ~10 |
| v0.5.0 | Fri 20 Nov | Your December world on L8, every Seven Meals people right | ~14 |
| v0.6.0 | Wed 25 Nov | Installable and machine-aware; names on the map; the kitchen deepened. **Feature freeze** | ~15 |
| v1.0.0 | Tue 1 Dec | Checklist walk (agent, then Daniel), full suite, tag | ~5 (fixes only) |

That totals about 44 of roughly 45 lane-days. The buffer is the 26–30 Nov freeze, and the first cuts are listed in section 6.

### v0.4.0: Sun 15 Nov. History that moves, closed out; zooming reaches the ground
1. LOD step 5 (lane 301: levels 3–4 drawn, layers on tiles; PW-1710, PW-1711), then **step 6, the judge**. These are PW-1673's done-when lines; they are filed as v1.0, so this pulls them forward.
2. Rivers and falls at tile edges (lane 303: PW-1713, PW-1709).
3. Follow-ups to live states: PW-1616 (war-era dials and times of troubles), PW-1617 (war refugees), PW-1488 (attitudes walked twice).
4. Close or retire what the 11-11 flip superseded: PW-1596, PW-1597, PW-1671.
5. A nudge test with live polities (PW-1460; the "v3 nudge test still holds" line).
6. Languages: PW-1642 (in progress) and PW-1692 (rare sound changes fire 10× too often).
7. Grooming:
   - v2's four leftovers: close or re-home PW-728, PW-856, PW-1308 and PW-1312.
   - Trade (PW-1498, PW-1508, PW-1532, PW-1533) and PW-1649, PW-1650, PW-676 go to `later`, or to v0.6 if picked in section 5.

**Done when:** the v4 "done when" lines 1–5 (`docs/review/board/milestones-v2-v5.md`) pass in the viewer on a fresh Seven
Meals run, *and* on one world the globe scrolls continuously down to 25 m with a map layer on, with no seam visible at
square edges. Area tests pass, and the full suite passes before the tag.

### v0.5.0: Fri 20 Nov. Your December world on L8
1. Daniel stars one of December A/B/C (PW-1437). **This is an owner action, needed by Thu 12 Nov** so the overnight runs can start.
2. Refine it to L8 and run the split history at 2 Myr. **PW-1691 is the blocker:** a 69.3 GB peak against the new per-process caps.
3. Peoples on 2 Myr vs 1 Myr, over re-rolled tries (PW-1672).
4. L8 settled-window parity: PW-1630, PW-1664 (coastal towns), PW-1631 (−8% people), PW-1584 (mechanics that count cells), PW-1626.
5. Every Seven Meals people right: PW-1558 (in progress), PW-1184, PW-1257 (half-orcs), PW-758 (half-elves), PW-1400; PW-730 and PW-755 (canon re-read).
6. Opening an L8 world fast: PW-1560 (binary grid files).
7. **new:** installer v0 on Linux (the bootstrap draft below). It starts now so that problems show up early.

**Done when:** the v5 "done when" lines 1–4, read as L8 per the owner's 11-10 ruling. The chosen world opens at L8 with
peoples on it, Workbench Results lists every Seven Meals people as living near its parents, and the LOD zoom works on that
refined world. **~14 lane-days, plus overnight compute.**

### v0.6.0: Wed 25 Nov. Installable, named, and a deeper kitchen (feature freeze)
1. **new ×5:** the installer, i.e. the bootstrap, first run, update and uninstall, the macOS memory probe, and machine-aware presets (section 4).
2. Labels on the map, in the English Common or local names (PW-1655), and named features (PW-1656).
3. A settlement view: click a town to see its names, peoples, goods, rule, faith and history (PW-1659).
4. **new:** a flavour profile on the food sheet (section 5, #1).
5. Preservation and ferments: pull PW-744 and PW-1441 forward (section 5, #2).
6. **new:** cuisine through time in the viewer (section 5, #3).
7. The RAM guard sums queued jobs (PW-1678). This ties into the memory caps and the installer presets.

**Done when:**
- On a clean user account on Linux, one command installs. The launcher opens the viewer, and the first-run world builds.
  Uninstall removes everything except the data folder, which it asks about.
- A Seven Meals culture's food sheet shows its flavour profile, its preserving methods and its kitchen at three eras.
- Labels and the settlement view work on the December world.

**~15 lane-days.**

### v1.0.0: Tue 1 Dec. Walk and tag
- **Thu 26 – Fri 27:** an agent walks every "done when" list (v2–v6) headless on the December world (PW-1439).
  **Proposal:** the agent walks an *installed* copy, with its own data folder and a port other than 8765, not the dev checkout.
- **Sat 28 – Mon 30:** Daniel walks the same lists. The only fixes allowed are for a line that breaks.
- **Mon 30:** the full suite (13–22 min under load, `docs/coordination.md`), then tag on Tue 1 Dec.
- Anything else found in the walk goes to `later`.

## 4. The installer (v1.0 must-have)

**What it has to deal with (from the repo):**
- **Python.** The project needs Python ≥ 3.14 (`pyproject.toml`; `.python-version` = `3.14+gil`) and uv (`uv.lock`; `package = false`). Its dependencies are numba ≥ 0.68, numpy, piper-tts, onnx and espeakng-loader.
- **Numba.** It is JIT-compiled with `cache=True` at 190 sites (`grep -c` over `planet/`). The cache sits next to the code, so the code folder must be writable.
- **Data folder.**
  - Data lives under `$PLANET_DATA` or the repo (`planet/store.py::root`): `runs/`, `worlds/`, `zooms/`, `grids/` (109 MB, generated) and `.tiles/` (cap 60 GB, `$PLANET_TILE_CACHE_GB`).
  - Everything under `data/` is git-ignored: `data/earth` (1.8 GB, only for the Earth reference world), `data/language/raw` (161 MB) and `data/language/tts` (the piper voice, 121 MB; espeak is the fallback).
- **The viewer.** It is static JS. It loads three.js r160 from jsdelivr (`viewer/`), so **today it needs the internet**.
- **Sizes on Daniel's machine** (`du -sh`): runs 52 G (33 runs), zooms 18 G (170), worlds 4.6 G (107). One L7 1 Gyr run is 2.7 G (a19366); one L8 run is 5.9 G (6a6fd6).
- **The RAM guard** reads `/proc/meminfo` (`planet/api.py::free_ram_gb`). On macOS it returns None, so every RAM guard is silently off.

**Target OS:**
- **Linux x86-64 first.** It's Daniel's machine, and `/proc` is assumed.
- **macOS (arm64)** is best effort. The run-cost table was measured on a Mac laptop, so the code runs there, but the RAM probe needs a port.
- **Windows** goes through **WSL2**, documented. Native Windows waits until after v1.0 (paths, the TBB threading layer, espeak).

**Packaging options:**

| option | pros | cons |
|---|---|---|
| **uv bootstrap script** (`install.sh`) | uv fetches Python 3.14 itself, and `uv sync --frozen` reproduces `uv.lock` exactly. Small and transparent; it updates by tag | Needs the internet at install; it's a shell script, so Linux and macOS only |
| pipx | Familiar | Needs a system Python 3.14 and a real wheel. The project is `package = false` and reads repo-relative `viewer/` and `grids/` |
| PyInstaller / briefcase bundle | One file, no Python needed | numba, llvmlite and TBB are fragile to freeze, and the JIT cache sits inside a read-only bundle. Hundreds of MB per OS, and a build per OS |
| Docker | Isolation, and cgroup memory caps for free | Docker Desktop's VM caps memory on macOS and Windows and slows file I/O; heavy for one user; the browser still lives outside |

**Pick: the uv bootstrap script.** Docker could come later as an optional "server box".

**Install and first run:**
1. `curl -LsSf <release>/install.sh | sh`, or run it from a checkout. The script:
   - installs a pinned uv into `~/.local/share/procgen-world/uv`;
   - fetches the tagged release tarball into `…/app/<version>` and points `current` at it;
   - runs `uv sync --frozen --no-dev`, with uv fetching Python 3.14;
   - vendors three.js r160 into `viewer/vendor/`, so the viewer works offline;
   - writes `~/.config/procgen-world/config.toml` (`PLANET_DATA=~/procgen-world-data` by default; the user can choose the folder).
2. Warm-up: a level-4 run of a few Myr in a scratch data folder compiles the numba cache. **Time not measured: the ticket measures it.**
3. Starter world: by default it **generates** `planet make --seed 7` at L6 (~6 min per the README). A downloadable sample bundle
   is optional, after a measurement of what one finished world plus its run layers weighs. An L7 run is 2.7 GB, too much to download.
4. Optional extras, each with its size shown: the piper voice (121 MB) and the Earth datasets (1.8 GB).

**Launch:** a `procgen-world` command and a `.desktop` entry, or a `.command` file on macOS. It runs `planet serve` with the
config's `--jobs` and `--port`, and picks a free port if 8765 is taken. It opens the browser at `/viewer/`.

**Updates:**
- `procgen-world update` fetches the newest tag into a new `app/<version>`, runs `uv sync`, and moves `current` once the smoke check passes.
- It keeps the previous version for `procgen-world rollback`. Data is never touched.
- The project has no backward compatibility, so the update notes say whether old runs still open (the viewer already flags runs made by older code).
- The viewer's start screen shows "update available", since Daniel uses the viewer and not the CLI.

**Uninstall:** `procgen-world uninstall` removes the app folders, uv's private Python, the launcher and the config. It asks
separately about the data folder, shows its size, and keeps it by default.

### Stretch: machine-aware setup

The installer probes the machine and writes the presets into `config.toml`. The probe reads cores (`os.cpu_count`), RAM
(`/proc/meminfo`, or `sysctl hw.memsize` on macOS), free disk on the data folder, and the GPU: `lspci`/`nvidia-smi`
coarsely, then the viewer reports WebGL2 limits and the renderer string on its first open. The server and `planet make`
read the presets, and a **Machine** panel in the viewer's settings shows each feature as allowed, warned or off, with the
number that decided it.

Measured costs it uses:

| feature | cost | source |
|---|---|---|
| L6 run | ~11–13 min/Gyr laptop, ~260 s/Gyr idle Threadripper | coordination.md run costs |
| L7 run | 3010 s/Gyr, ~0.9 GB RSS, 1.4–1.7 GB layers per Gyr | `planet/make.py` RUN_S_PER_GYR; coordination.md |
| L7 time zoom, 2 Myr | 3.5 s/kyr ≈ 2 h | make.py TZ_S_PER_KYR |
| L8 run | ~5.7 h/Gyr at 8 threads, peak 30 GB at the final write, 3.9–5.9 GB disk | coordination.md; `du` 6a6fd6 |
| L8 time zoom, 2 Myr | 15 s/kyr ≈ 8 h | make.py |
| refine to L8 / L9 | 4 min 22 s, 11.7 GB / 38 min, 39 GB | decisions 11-10 (lane 280); PW-1262 |
| peoples history, L8 split | 35.5 GB at 1 Myr; 69.3 GB at 2 Myr (PW-1691) | decisions 11-10 |
| peoples history, L7 | ≈ 12 GB (**estimate**: L8 split was "3× memory" of L7) | decisions 11-10, lane 266 |
| LOD tile builds | level 1 8.3 GB; levels 2–4 3.2 GB each, 3 at once; plus 8 GB spare | `planet/tiles.py`, `planet/api.py` |

Presets by tier (thresholds are free RAM at install; **estimate**, to be tuned by the ticket):

| feature | < 16 GB | 16–31 GB (low) | 32–63 GB (**minimum**) | ≥ 64 GB (**recommended**) | ≥ 96 GB |
|---|---|---|---|---|---|
| default grid level | L6, warn | L6 | L7 | L7 | L7 |
| job concurrency (`--jobs`) | 1 | 1 | 2 | 4 | 4 |
| peoples history at L7 | off | warn | allow | allow | allow |
| LOD zoom tiles (at once) | off | levels 2–4 only, 1 at a time | 1 | 3 | 3 |
| tile cache cap | 10 GB | 20 GB | 40 GB | 60 GB | 60 GB |
| refine L8 / L8 split at 1 Myr | off | off | refine only | allow | allow |
| L8 split at 2 Myr, L9 refine | off | off | off | warn (L9 ok; 2 Myr split needs PW-1691) | allow |
| time zoom length offered | 1 Myr | 1 Myr | 2 Myr | 2 Myr | 2 Myr |
| per-process memory cap | 70% of RAM | 70% | 75% | 80% | 80% |

Disk: below 50 GB free it warns, and below 20 GB it refuses the install (an L7 world family is ~3 GB, plus the tile cache).
GPU: WebGL2 is required. Under ~2 GB of VRAM, or on software rendering, the viewer starts in low-detail mode (fewer tiles in
flight, no tilt shading).

- **Minimum machine:** 8 cores, 32 GB RAM, 100 GB free SSD, any WebGL2 GPU. That covers L7 worlds, peoples and LOD zoom one tile at a time.
- **Recommended:** 16+ cores, 64 GB, 250 GB free SSD, a discrete GPU with ≥ 4 GB. That adds L8 refine and splits at 1 Myr, and 3 tiles at once.
- Daniel's Threadripper class (24C, ≥ 96 GB) unlocks everything.

**Tickets to be** (drafts in `issue-tracking/inbox/`, milestone v1.0, proposed for v0.6.0):

| ticket | done when |
|---|---|
| Installer: uv bootstrap, launcher, data folder, offline three.js | On a clean Linux user, one command gives a working viewer with no network after install |
| Installer: first run, numba warm-up and starter world | The first launch shows progress, compiles, makes the L6 seed-7 world, and opens it; the times are recorded |
| Installer: update, rollback and uninstall | Each works on a test install; data is untouched; the viewer shows "update available" |
| RAM probe on macOS (free_ram_gb returns None) | The guards work on macOS, or refuse with a message instead of running unguarded |
| Machine-aware presets plus a Machine panel in the viewer | The probe writes the presets; server and make obey them; the viewer panel shows allow/warn/off with numbers |

## 5. More or More Better (ranked for the end goal, PW-692)

| # | candidate | value | cost (lane-days, **estimate**) | risk |
|---|---|---|---|---|
| 1 | **Flavour profile per culture** (new): a profile of the culture's tastes (salty, sour, umami, fat, heat, smoke, sweet, bitter, funk), built from salt distance, fuels (dung and peat give smoke), crops and spices, dairy, ferments and senses (PW-905). Shown on the food sheet, with the reason for each axis | Answers "how it tastes", the one PW-692 question with no answer yet | 1.5 | Medium. Heuristics must be sourced or labelled as invented; keep the weights visible |
| 2 | **Preservation and ferments** (PW-744, PW-1441, PW-1141): drying, salting, smoking, pickling, cheese, beer and wine by climate, salt, fuel and tech | Feeds #1; "no beer or wine yet" on every D&D sheet is a visible gap | 1 | Low to medium |
| 3 | **Cuisine through time** (new): the food sheet at three eras in the viewer, with crops arriving, conquest doublets (PW-1644) and calendar dates (v4) | The culinary book is historical; the brief already has era slices (PW-742) | 1 | Low |
| 4 | **Settlement view plus labels** (PW-1659, PW-1655, PW-1656) | Daniel's campaign entry point: click a town, read its kitchen | 2.5 | Low |
| 5 | **Trade goods layer** (PW-1508) only, from the spare/lacking that already exists; the full trade epic (PW-1498) stays later | Shows where spices and salt come from | 1 | Medium: the trade model is thin |
| 6 | **Viewer low-detail mode** (new, tied to the installer stretch) | The installer's "adapt to weaker machines" on the viewer side | 1 | Low |
| 7 | **Signature dishes** (new): 3–5 dishes per culture composed from staples, technique, fuel and flavour, named in its language | High delight; the book's raw material | 2 | High: it can read as gimmicky. Do it only after #1–#3 |
| 8 | **Food calendar** (new): lean season and harvest, from the July/January climate and the culture's calendar | Rhythm of meals and feasts | 1.5 | Medium: only two seasons are stored |
| 9 | **Culture book export** (Markdown per culture, PW-856 / PW-728) | Hands the result to the culinary repo | 1 | Low |

My recommendation for v0.6: #1–#4. #5 and #6 go in if there's room; #7–#9 wait until after 1.0.

## 6. Risks to the date, and what to cut first

**Risks:**
1. **L8 at 2 Myr memory (PW-1691).** The peak is 69.3 GB on a shared ~90 GB machine with per-process caps.
   *Fallback:* run the December world's split history at 1 Myr (35.5 GB).
2. **The LOD tail.** Seams, rivers and falls at edges (PW-1709, PW-1713) and the step-6 judge can each take three passes.
   *Fallback:* ship down to 250 m and keep 25 m as best-effort.
3. **Regressions from live states** (flipped 11-11). The nudge test (PW-1460) is the check. *Fallback:* `POLITIES_LIVE` off,
   since read-out states remain.
4. **Installer surprises.** Wheels for numba, llvmlite and TBB on 3.14, macOS, a first run that takes minutes. Starting in
   v0.5 leaves two milestones to find them.
5. **Owner time.** The December-world pick is due ~12 Nov, D68 and D70 are open, and the walk falls on Thanksgiving weekend.
6. **The shared machine.** Overnight refines and splits compete with other jobs.
7. **Board growth** of about 18 tickets a day. Hold lanes to 3 drafts.

**Cut first, in order:**
1. Section 5 items #4 onward.
2. The flavour profile and cuisine through time (#1, #3).
3. The installer stretch, down to a probe that warns only.
4. macOS support (Linux only).
5. LOD levels finer than 250 m.
6. The December world back to L7 with the L7 history.

**Never cut:** the basic Linux installer, the checklist walk (PW-1439) and the full suite before the tag.
