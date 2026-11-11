# Mac install checklist (PW-1760): for Daniel's Apple Silicon Mac (24 GB)

About 15 minutes, most of it waiting. Paste each block into **Terminal** (Applications → Utilities → Terminal). After
each step, compare with "you should see". If anything differs, copy the Terminal text into a note for the coordinator.
Nothing here needs `sudo`. Nothing is installed outside `~/.local/share/procgen-world`, `~/.config/procgen-world`,
`~/.local/bin/planet`, `~/Applications/Procgen World.command` and `~/procgen-world-data`.

## 1. The Mac is one the installer supports

```sh
uname -m; sw_vers -productVersion
```

You should see `arm64`, then `14.x`, `15.x` or newer. (macOS 13 or an Intel Mac is refused: the libraries the
simulation needs publish no Python 3.14 builds for them.)

## 2. Get the code

The repository is not public yet, so the one-line `curl … | sh` cannot reach it. Use the branch the coordinator names
(a `ci/…` branch): on GitHub, open that branch, then **Code → Download ZIP**. Then:

```sh
cd ~/Downloads && ls -d procedural-world-generation-*
```

You should see one folder, e.g. `procedural-world-generation-ci-pw1760`. Go into it (use the name it printed):

```sh
cd ~/Downloads/procedural-world-generation-ci-pw1760
```

(No git is needed. The Mac's `git` would ask to install the developer tools; the installer does not use it here.)

## 3. Install

```sh
sh install.sh --yes --no-starter
```

You should see, in about 2 to 5 minutes:

```
procgen_world installer
    version  0.x.y-local   (from /Users/<you>/Downloads/procedural-world-generation-…)
    install  /Users/<you>/.local/share/procgen-world
    data     /Users/<you>/procgen-world-data
==> uv 0.12.7 (private to this install)
    downloading uv 0.12.7 (aarch64-apple-darwin)
==> Installing Python 3.14 and the dependencies (uv sync --frozen --no-dev)
==> Launcher, config and app-menu entry
    note: /Users/<you>/.local/bin is not on your PATH. …
==> Sizing the app to this machine (cores, memory, disk, graphics)
      machine   … cores, 24… GB RAM, … GB free disk, GPU Apple M…
==> First run: compiling the simulation (numba) on a tiny level-4 planet
    | [100%] done
    compiled in … s
    no starter world now; make one any time with: planet make --seed 7 --level 6
Start it with:  planet self open
```

**Write down** the "done in … s" and "compiled in … s" numbers. A red `error:` line ends the step: copy it.

## 4. The `planet` command

```sh
export PATH="$HOME/.local/bin:$PATH"
planet self status
planet machine show
```

You should see `current  0.x.y-local` and `config …/.config/procgen-world/config.toml`. `planet machine show` should
say about 24 GB of RAM and an Apple GPU. (To keep `planet` in new Terminal windows, add the `export` line to `~/.zprofile`.)

## 5. Free memory and the threading layer (the two macOS-specific readers)

```sh
A=$(cd ~/.local/share/procgen-world/app/current && pwd -P)
PYTHONPATH="$A" "$A/.venv/bin/python" -c "from planet import api, parallel; print('free GB', round(api.free_ram_gb(), 1)); print('layer', parallel.pin_threading_layer())"
```

You should see `free GB` followed by a number between about 2 and 24, with **no** `warning:` line, then
`layer workqueue` (or `tbb`). Either layer is fine; write down which.

## 6. Open the viewer by double-click

In Finder, open your home folder → **Applications** → double-click **Procgen World.command**.

You should see a Terminal window print `Viewer at http://127.0.0.1:8765/viewer/ …`, then your browser open the globe
page. The warm-up world was deleted, so the list may be empty: that is expected. Leave it open for step 7.

(If macOS says the file "cannot be opened", right-click it → Open → Open. Write that down: it means the installer
should sign or un-quarantine it.)

## 7. Make a small world from the viewer's terminal

In a **second** Terminal window:

```sh
export PATH="$HOME/.local/bin:$PATH"
time planet make --seed 7 --level 5 --name mac-l5
```

You should see progress lines ending in `[100%] done` and a `view: http://127.0.0.1:8765/viewer/?world=…` line. Reload
the browser: the `mac-l5` world is listed and opens. Write down the `real` time. Then close the first window (Ctrl-C
stops the server).

## 8. Uninstall

```sh
planet self uninstall
```

Answer `Y` to "Uninstall?" and `N` to "Also delete your data folder". You should see `Kept your data folder
/Users/<you>/procgen-world-data (…)` and `procgen_world is uninstalled.` Then:

```sh
ls ~/.local/share/procgen-world ~/Applications/"Procgen World.command" 2>&1 | head -2
```

You should see two `No such file or directory` lines. Delete `~/procgen-world-data` yourself if you want the space back.

## Report back

The numbers from steps 3, 5 and 7, the threading layer, and any line that differed.
