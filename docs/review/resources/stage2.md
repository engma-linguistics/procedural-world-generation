# Resources stage 2: deposits sited in regional zooms (PW-610)

2026-10-23, lane resources2. Design: `docs/proposals/resources.md` section 6. Code: `planet/zoom_resources.py`,
plus two stage-1 fixes in `planet/resources.py` (bauxite, coal speckle).

## What it does

    uv run python -m planet resources zoom:<id> [...]     # site deposits in saved zooms, in place
    uv run python -m planet resources <world>             # (stage 1, unchanged: the world's likelihood layers)

The command adds `resources` to the zoom's `zoom.json`, holding the deposits, the outcrop belts, a summary and a
legend. It does not touch the zoom's layers or the world. The world's likelihoods are its `res_*` layers when
it has them, otherwise they are made in memory, with the run's history when the run is stored. The cost is
0.2-1.5 s of siting plus the history pass: 6-9 s at L7, about 2 s at L6. Run time is unchanged, and so are the
goldens and the existing zoom outputs.

**Consistency with the world map.** A world cell's likelihood p is read as "the chance that a notable (medium
or larger) deposit of this kind lies in the cell". The number of deposits in the cell is drawn from a Poisson
distribution. The expected number of notable ones is -ln(1 - p), so P(at least one) = p exactly. Small deposits
come on top: notable ones are 30% of all, and the size classes are small 70%, medium 22%, large 7%, giant 1%.
Inside a cell, the deposits go to the pixels whose own ground fits the model. Each pixel's suitability is
normalised over the cell's pixels, so the ground moves deposits within a cell but never changes a cell's count.
Positions are interpolated with the same Gaussian kernel the zoom uses for its world fields. The draw is
deterministic per zoom (its id and seed) and per resource. The summary checks the result: of the world's
district cells (>= 0.5) that lie inside a zoom, the share holding a deposit of their resource was:

| zoom | world | examples |
|---|---|---|
| 7379a5 (500 km @ 1 km) | 91448a L7 | epithermal 29/29, VMS 3/3, placer gold 2/2 |
| 37a60b (1000 km @ 2 km) | 3e0b0a L7 | coal 17/20, gas 9/11, sed Pb-Zn 8/11, oil 3/4 |
| bea8db (500 km @ 1 km) | 1144ce L7 | orogenic gold 26/27, BIF 9/11, Sn-W 3/3, placer gold 2/2 |
| 29250c (500 km @ 1 km) | 91448a L7 | porphyry 8/9, orogenic gold 21/21, Sn-W 27/27 |
| 106461 (2000 km @ 4 km) | 91448a L7 | porphyry 44/52, BIF 92/136 (the 400-per-resource cap bites) |

The expected share at p = 0.5 is about 90%. A cell whose pixels offer no suitable ground (placers with no river,
for example) loses its deposits. That is deliberate, and it is where the misses come from.

**Siting rules per form**, on the zoom's own layers:
- **Hard rock** (porphyry, epithermal, VMS, orogenic gold, Sn-W, BIF, Ni-Cu-PGE, sed Pb-Zn, REE, metamorphic
  gems, obsidian, the fantasy three):
  - porphyry: arc basement, granite and tuff, and within 25 km of the zoom's volcanoes (their roots);
  - epithermal: tuff, arcs, rifts and volcano flanks;
  - orogenic gold: fold-belt, orogen and craton basement, preferring ridges;
  - Sn-W: granite pixels;
  - BIF: exposed shield;
  - obsidian: within 10 km of young volcanoes.
  A deposit under sedimentary cover is 100-600 m deeper ("found by drilling").
- **Laterites** (bauxite, laterite Ni): flat ground (< 3%) that the zoom's soils class as well drained.
  Bauxite avoids quartz sand and carbonate.
- **Placers**: the zoom's rivers (>= 3 m^3/s) where the current slows: a gentle reach, or a reach below a
  steeper one, or the valley floor when the zoom is a fine zoom with `valley_floor`. Each placer is weighted
  by the load the zoom's own drainage (its D8 receivers) carries from the gold or tin ground eroding upstream.
  The load is the world's source likelihood times slope, and loses ~1.5% per km. Beach placers form on coasts
  with waves above 5 kW/m.
- **Kimberlite fields**: field centres on craton pixels, each with 5-30 pipes in a ~5 km cluster, of which
  ~10% are worth mining.
- **Coal seams**: the coal measures' top lies at the history column's depth below a ~cell-wide mean of the
  zoom's ground. In fold belts the bed also follows the zoom's ridges (anticlines under ridges). The measures
  outcrop where the terrain cuts down into them; these outcrop pixels are stored as a belt and drawn as dots.
  Seams are sited where the bed is shallow, three times more often in the outcrop belt. Each seam gets a rank
  from the deepest burial (lignite, bituminous, anthracite; folded bituminous becomes anthracite) and a mining
  method: open-cast below 60 m, drift to 300 m, deeper a shaft.
- **Salt**: salt pans and closed salt lakes in the zoom, beds in the evaporite column, and domes where the
  beds are over 0.5 km thick.
- **Oil and gas fields**: in fold belts on the anticline crests (the zoom's high-pass ridges); elsewhere
  anywhere (fault and stratigraphic traps), twice as likely over salt. Depth comes from the source rock's
  burial. Fields can be offshore.

Each deposit has a type, size class, tonnage (Mt ore, Mm^3 gravel, million bbl, ...), a lognormal grade
specific to its model (porphyry ~0.45% Cu, orogenic gold ~5 g/t, ...), the depth and depth class, the host and
the world cell's likelihood. Each resource keeps at most 400 deposits per zoom (the biggest); the summary
counts the rest.

**Viewer** (`viewer/zoom.html`):
- The "Deposits" overlay has a filter: all, a group, or one resource.
- Marker shapes show the form: circle for hard rock, square for laterite or salt, diamond for placers, a
  hexagon plus pipe dots for kimberlite fields, a bar for coal, an ellipse for oil and gas. Marker size shows
  the size class, and colours follow the resources legend. Fantasy deposits have a magenta outline.
- Coal outcrop belts are drawn as dots.
- The legend lists the resources shown. Hovering or clicking a marker opens a card with size, grade, depth,
  host, rank and mining, the deposit model and the world cell's likelihood.
- The zoom's "about" panel gets a "deposits" row: counts, the biggest, and the share of the world's districts
  that show up.
- New URL parameters: `depsel=coal|g:metal`, `dep=0`, `mark=dep:N` and `at=row,col,magnification`.

`planet export` of a zoom writes the deposits as `deposit` point features.

## Screenshots (scratch-store copies, port 8793)

- `stage2/arc_7379a5_metals.jpg`: an old arc margin (91448a, 500 km). Porphyry Cu (orange) and epithermal
  Au-Ag (yellow) are scattered over the arc, with VMS (teal) on the shelf. The card shows a large porphyry:
  1443 Mt at 0.45% Cu, 285 m down.
- `stage2/coal_37a60b_seams.jpg`: a coal basin (3e0b0a, 1000 km, magnified 2.5x). Coal-measure outcrops
  (dots) follow the valleys that cut down to the measures, and seams cluster on them. The card shows 1036 Mt of
  lignite, 3 seams, 272 m down, drift or shallow shaft.
- `stage2/placer_bea8db_river.jpg`: a fold-belt gold province (1144ce, magnified 3x). Orogenic gold (gold
  circles) sits on the ridges, and placer gold (diamonds) lies on the rivers draining them. The card shows a
  large placer of 84 Mm^3 at 0.27 g/m^3.
- `stage2/overview_37a60b_all.jpg`: the whole coal-basin zoom with all deposits, including the offshore oil
  and gas fields.

## Bauxite: by mechanism (`resources.py`)

Before, bauxite was 0.8 x sat(tropical weathering Myr, 60) x flat x elevation factor, and it lay at 0.25-0.5 on
11-23% of the land. A bauxite profile needs tens of Myr of **uninterrupted** weathering on a surface that is
neither buried nor stripped. The history now records this: for each traced cell, the longest run of keyframes
in which it was tropical-weathering land (the same climate gates as before) and its smoothed cover changed by
less than 10 m/Myr up or down. Each run is discounted by exp(-age/60 Myr) for its survival since it ended; a
run still going counts in full.

The new rule is 0.85 x sat(run, 40 Myr) x flat x well drained x aluminous parent:
- well drained: the cell stands 10-80 m above its lowest neighbour (sea level at most), or is a plateau
  above 100-400 m;
- aluminous parent: quartz sand and quartzite x0.25, carbonate x0.4 (karst bauxite), evaporite 0.

Laterite Ni uses the same run.

| world | % land >= 0.25, before -> after | % land >= 0.5, before -> after |
|---|---|---|
| 119973 L6 | 22.7 -> 8.4 | 1.26 -> 4.40 |
| 81aced L6 | 19.2 -> 6.4 | 0.06 -> 1.56 |
| 1144ce L7 | 20.6 -> 9.4 | 0.86 -> 2.87 |
| 91448a L7 | 9.2 -> 8.4 | 0.01 -> 3.60 |

The broad mid-range is gone. Bauxite now sits in coherent belts on long-stable tropical surfaces (map:
`stage2/bauxite_1144ce_before_after.jpg`, top before, bottom after), and their cores reach "likely".
91448a's tropics were already narrow, so its >= 0.25 share hardly moves.

## Coal speckle (PW-134): partly fixed

The column's speckle came from the keyframes' 0.1 km cover steps flickering up and down: each flicker eroded
and redeposited the column's top. The swamp flag flickered too. The history now takes a 5-keyframe (20 Myr)
running mean of each traced cell's cover, and a majority vote of the swamp flag over the same window, before
rebuilding the column. Oil, gas and salt are rebuilt from the same smoothed column.

| world | coal cells >= 0.5 | isolated (no neighbour >= 0.5) | patches | mean neighbour difference |
|---|---|---|---|---|
| 1144ce L7 | 1849 -> 2114 | 24% -> 17% | 702 -> 605 | 0.061 -> 0.055 |
| 119973 L6 | 289 -> 360 | 25% -> 22% | 116 -> 118 | 0.036 -> 0.035 |
| 81aced L6 | 453 -> 661 | 25% -> 16% | 179 -> 173 | 0.056 -> 0.058 |
| 91448a L7 | 461 -> 709 | 36% -> 23% | 232 -> 260 | 0.013 -> 0.017 |

Coal is a little more widespread, because less of it is eroded by flicker: 2.2-3.3% of land at >= 0.5 becomes
2.7-4.7%. The isolated share drops by a third, but the map is still visibly speckled
(`stage2/coal_1144ce_before_after.jpg`). The rest comes from neighbouring cells tracing back to different
keyframe cells. That needs a spatial pass, not a temporal one (inbox: draft-resources-coal-speckle-residual).

Other shares moved with the smoothed column: oil >= 0.5 rose from 0.5-0.7% to 1.1-1.7% of land, and gas from
1.1-1.5% to 1.5-2.7%. Salt barely changed.

## Open (inbox drafts)

- `draft-resources-snw-granite-spread`: Sn-W covers every exhumed granite, so zooms get hundreds of tin
  deposits.
- `draft-resources-coal-speckle-residual`: the spatial half of the speckle.
- `draft-resources-zoom-deposits-auto-and-3d` (needs-decision): when deposits are made (command, every zoom,
  or lazily); none in the 3D view; fine zooms don't inherit them.
- `draft-resources-zoom-bed-geometry`: beds fold with a high-pass proxy, not the fold belt's stored structure.
