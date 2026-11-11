---
id: PW-1719
title: "Installer: one-command uv bootstrap with a launcher, a data folder outside the code, and an offline viewer (Linux first)"
type: story
status: done
parent: null
milestone: v1.0
subsystem: infra
effort: l
impact: high
found_by: plan-v1-lane
blocked_by: []
relates: [PW-1439]
refs: [docs/review/plan/milestones-to-v1.md, pyproject.toml, uv.lock, .python-version, "planet/store.py::root", planet/__main__.py, viewer/index.html, README.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: owner 2026-11-11: v1.0 needs an installer. Today the project runs only from a git checkout with uv by hand, and the viewer pulls three.js from jsdelivr, so it breaks offline. Proposal: docs/review/plan/milestones-to-v1.md section 4 (pick: a uv bootstrap script over pipx, PyInstaller/briefcase and Docker). Planned for v0.5.0 (start) and v0.6.0 (done).

If it is never done, v1.0 can't be installed by anyone but a developer. The v1.0 walk (PW-1439) also runs on the dev checkout, not on what ships.

What the script (`install.sh`, Linux x86-64; macOS best effort; Windows via documented WSL2) does:
- Installs a pinned uv privately (`~/.local/share/procgen-world/uv`), fetches the tagged release into `app/<version>` with a `current` link, and runs `uv sync --frozen --no-dev`. uv fetches Python 3.14 itself (`.python-version` 3.14+gil).
- Writes `~/.config/procgen-world/config.toml` with `PLANET_DATA` (default `~/procgen-world-data`; `planet/store.py::root` already honours it), port and jobs.
- Vendors three.js r160 (`cdn.jsdelivr.net/npm/three@0.160.0`) into `viewer/vendor/` and points the imports there.
- Adds a `procgen-world` command and a `.desktop` entry that run `planet serve` with the config's port (a free one if 8765 is taken) and open the browser.
- Testing never touches Daniel's server on 8765 or his data: use a throwaway user or HOME, another port and another PLANET_DATA.

- [ ] On a clean Linux user, one command installs; the launcher opens the viewer; the network can be off after install
- [ ] Code and data are in separate folders; the app folder holds no runs, worlds, zooms or tiles
- [ ] README has an "Install" section (Linux, macOS best effort, WSL2)

## Updates
- 2026-11-11: Status todo -> done. merged (lanes 304/306)
- 2026-11-11: Created from inbox draft draft-installer-uv-bootstrap.md (found by plan-v1-lane).
