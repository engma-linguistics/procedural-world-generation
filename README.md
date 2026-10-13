# procgen_world

Toy procedural planets: a plate-tectonics terrain generator, a
climate / river / biome pipeline, a plain-text world format, and a 3D
browser viewer.

## Quick start

```sh
uv run python -m planet generate --seed 1          # writes worlds/plates-s1-L5.{json,txt}
uv run python -m planet serve                       # opens http://127.0.0.1:8765/viewer/
```

Other things to try:

```sh
uv run python -m planet generate -s 42 -l 6                              # more detail
uv run python -m planet generate --set n_plates=6 continental_fraction=0.5
uv run python -m planet generate --erosion 0                             # skip river erosion
uv run python -m planet show worlds/plates-s1-L5.json --layer elevation  # ASCII map in the terminal
```

`-l/--level` controls grid detail: 4 = 2.5k cells, 5 = 10k (default, ~240 km cells),
6 = 41k (~120 km), 7 = 164k (slow, big files).

## Terrain: plates (`planet/generators.py`)

Cartoon plate tectonics: random plates, each spun around a random axis, with
mountains, trenches, ridges and rifts built where plates collide or separate.
Knobs (`--set`): `n_plates`, `continental_fraction`, `mountain_height`,
`trench_depth`, `ridge_height`, `plate_speed`.

(Earlier `noise` and `faults` generators are in git history at commit 503f101.)

Terrain then goes through the shared pipeline:

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

- `worlds/<name>.json` holds everything. `meta`, `summary` and `legend` come first and are
  human-sized; `layers` has one array per field, indexed by cell id; `grid` has the geometry.
- `worlds/<name>.txt` is the summary plus ASCII maps (biome, elevation, plates,
  rainfall). This is the one to read, or paste into a chat.
- `worlds/index.json` is the list the viewer's dropdown reads.

In the viewer, clicking a cell copies a description to the clipboard, e.g.
`plates-s1-L5: cell 4021, lat 12.3, lon -45.6, elevation 2310 m, …`, so you can
point at a specific place when asking for changes.

Viewer URL options: `?world=x.json&mode=map&layer=plates&pentas=1&arrows=1&outlines=1&relief=40`.
