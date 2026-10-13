# procgen_world

Toy procedural planets: three different terrain generators, a shared
climate / river / biome pipeline, a plain-text world format, and a 3D
browser viewer.

## Quick start

```sh
uv run python -m planet generate --seed 1          # all three methods, seed 1
uv run python -m planet serve                       # opens http://127.0.0.1:8765/viewer/
```

Other things to try:

```sh
uv run python -m planet generate -m plates -s 42 -l 6                    # one method, more detail
uv run python -m planet generate -m plates --set n_plates=6 continental_fraction=0.5
uv run python -m planet generate -m noise --set ocean_fraction=0.4 warp=1.0
uv run python -m planet generate -m faults --set offset=0 --erosion 0     # see the antipode trick
uv run python -m planet show worlds/plates-s1-L5.json --layer elevation  # ASCII map in the terminal
```

`-l/--level` controls grid detail: 4 = 2.5k cells, 5 = 10k (default, ~240 km cells),
6 = 41k (~120 km), 7 = 164k (slow, big files).

## The three generators (`planet/generators.py`)

| method   | idea | tell-tale look | knobs (`--set`) |
|----------|------|----------------|-----------------|
| `noise`  | Fractal (Perlin) noise sampled on the sphere, plus ridged noise for mountains. The industry default. | Pretty, blobby; mountains are speckles, not chains. | `ocean_fraction`, `continent_scale`, `warp`, `mountain_amount` |
| `faults` | Slice the planet with ~1000 random planes; raise one side, lower the other. 1990s demoscene classic. | Very Earth-like fractal coastlines; tends toward one big supercontinent. | `ocean_fraction`, `n_faults`, `offset`, `sharpness` |
| `plates` | Cartoon plate tectonics: random plates, spin each one, build mountains/trenches/ridges where they collide or separate. | Long mountain chains along plate edges, trenches off coasts, island arcs. | `n_plates`, `continental_fraction`, `mountain_height`, `trench_depth`, `ridge_height`, `plate_speed` |

All three then go through the same pipeline:

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
