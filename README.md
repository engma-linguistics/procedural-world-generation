# procgen_world

Toy procedural planets: a plate-tectonics terrain generator, a
climate / river / biome pipeline, a plain-text world format, and a 3D
browser viewer.

## Quick start

```sh
uv run python -m planet simulate --seed 1                 # 500 Myr of plate tectonics -> runs/run-s1-L5/
uv run python -m planet slice runs/run-s1-L5 --at 300     # full world (climate, rivers, biomes) at 300 Myr
uv run python -m planet serve                              # opens http://127.0.0.1:8765/viewer/
```

In the viewer, pick a timeline from the dropdown and press play (or space;
arrow keys step frames). Click an event in the list to jump to it. The panel
shows the exact `slice` command for the moment you're looking at.

Other things to try:

```sh
uv run python -m planet simulate -s 7 --myr 1000 --set start=scattered n_plates=16
uv run python -m planet simulate -s 3 --set erosion_timescale=200   # mountains last longer
uv run python -m planet report runs/run-s1-L5                       # re-render run.txt
uv run python -m planet generate -s 42 -l 6                         # one-shot (no time) plates world
uv run python -m planet show worlds/run-s1-L5-t300.json --layer elevation
```

`-l/--level` controls grid detail: 4 = 2.5k cells, 5 = 10k (default, ~240 km cells),
6 = 41k (~120 km), 7 = 164k.

## Time-stepped tectonics (`planet/tectonics.py`)

Each plate keeps its crust on a private copy of the grid plus a rotation saying
where that copy currently sits. Every step (default 2 Myr):

1. plates rotate by their angular velocity;
2. every world cell asks every plate whether it has crust there. Nobody has any:
   new ocean floor (a ridge). Several do: continental beats oceanic, young ocean
   beats old (subduction); continent vs. continent is a collision;
3. ocean floor sinks as it ages (~sqrt(age)), subduction builds arcs, collisions
   build big ranges, continents slowly wear down (`erosion_timescale`, a stand-in
   until real erosion runs in the loop);
4. velocities are *solved* from forces (no momentum): slab pull, ridge push,
   collision resistance, plus a slowly wandering mantle-drag term (meandering);
5. events: long collisions weld plates (suture), big continents rift, slivers
   get absorbed.

Main knobs (`--set`): `n_plates`, `start` (`supercontinent`|`scattered`),
`continental_fraction`, `slab_pull`, `ridge_push`, `collision_drag`,
`mantle_noise`, `mantle_timescale`, `mobility`, `max_speed`, `arc_uplift`,
`collision_uplift`, `erosion_timescale`, `suture_after`, `rift_timescale`,
`rift_min_continent`, `big_plate`, `max_plates`. Defaults live in `Params`.

Runs are deterministic: `slice` replays from t=0 (a few seconds) and checks
itself against the stored keyframe.

## One-shot terrain (`planet/generators.py`)

Cartoon plate tectonics: random plates, each spun around a random axis, with
mountains, trenches, ridges and rifts built where plates collide or separate.
Knobs (`--set`): `n_plates`, `continental_fraction`, `mountain_height`,
`trench_depth`, `ridge_height`, `plate_speed`.

(Earlier `noise` and `faults` generators are in git history at commit 503f101.)

Sliced and one-shot terrain then go through the shared pipeline:

1. **Climate** (`climate.py`): temperature from latitude and altitude; Earth-style
   wind bands carry moisture off the oceans; air rains out as it cools, which
   gives wet windward coasts and rain-shadow deserts.
2. **Erosion and rivers** (`hydrology.py`): priority-flood drainage, flow
   accumulation, then stream-power erosion that cuts valleys. `--erosion 0` skips it.
3. **Biomes**: a Whittaker-style lookup on temperature and rainfall.

Shared knobs: `--erosion <strength>`, `--set erosion_iterations=12 equator_temp=28 pole_temp=-22`.

## Why the pentagons

See the docstring in `planet/grid.py`. A sphere can't be tiled with hexagons
alone. Euler's formula forces **exactly 12 pentagons** (not 1), like the black
patches on a football. In the viewer, tick "Highlight the 12 pentagons".

## Files

- `runs/<name>/run.json`: settings, per-keyframe stats, plate velocities and the
  event log. Small and readable.
- `runs/<name>/frames.bin`: keyframe arrays for the viewer (raw binary; layout in run.json).
- `runs/<name>/run.txt`: the one to read or paste into a chat. It has the event log,
  stats over time, ASCII elevation maps at five moments, and a plate table.
- `worlds/<name>.json` / `.txt`: a full world (from `slice` or `generate`). The
  `.txt` has the summary and ASCII maps.
- `grids/L<level>.json`: grid geometry shared by all runs at that level.

All of these are generated output (git-ignored) and reproducible from seed + settings.

In the viewer, clicking a cell copies a description to the clipboard, so you can
point at a specific place when asking for changes.

Viewer URL options: `?run=run-s1-L5&t=120&layer=plates&arrows=1` or
`?world=x.json&mode=map&layer=biome&pentas=1&outlines=1&relief=40`.
