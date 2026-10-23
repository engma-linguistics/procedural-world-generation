# Resources: ores, coal, oil, salt, gems, stone (PW-155)

Status: **stages 1 and 2 built** (world-level likelihood layers, viewer, summary: `planet/resources.py`; zoom siting:
`planet/zoom_resources.py`, `docs/review/resources/stage2.md`). Owner decisions pending: see section 7.

## 1. Idea

Dwarf Fortress-style resources for game worlds, grounded in the geology the run already simulated. Each
resource follows a named **deposit model** (the way economic geologists explain where deposits form) and is
derived as a coarse **per-cell likelihood** (0..1: "how likely a deposit of this kind lies in this ~60-120 km
cell, within prospecting depth") from the run's record. The zooms then **site** concrete deposits
(points: type, grade, depth, size) consistent with the coarse layer.

**Cost:** labels and likelihoods derived at finish or zoom time, ~0 run time (the PW-155 cost note). The one
history-dependent part reads the stored keyframes back along plate motion (below): 1.5 s at L6, 6 s at L7
for 600 Myr of history. Nothing time-stepped is added to `simulate`; goldens are unchanged.

## 2. What the run records, and the history pass

A world already carries: basement rock (`rock`: ocean, hotspot, arc, sediment-born, orogen, craton,
granite), the exposed stratum and the one below (`strata_top`, `strata_next`, `strata_top_km`), cover
thickness, crust thickness and age (on continents the age since the basement formed or was remade),
landform classes with their ages (arc = youngest volcano's age, fold belt = since folding, rift = since
rifting, shield = basement age), rift strain, the time since ice, plate boundaries, the volcano table,
hotspots, climate, rivers, lakes and soils.

What it does **not** carry is a cell's *past*: how long its ground sat over a subduction zone, how thick its
crust got in a collision, which deposits are buried in its column. The run's record keeps only 3 strata and
the last rift/fold, and keyframes keep only the top two strata names. So `resources.history()`:

1. **Traces each cell's ground back** through the keyframes (every 4 Myr, up to 600 Myr): at each frame it
   finds the cell under the traced point, reads that frame's layers there, then rotates the point back by
   that frame's Euler rotation of the plate under it (`frames[k].omega`). This follows plate
   reorganisations (unlike the soils' memory, which extrapolates today's motion over a few Myr). Sea floor is
   traced only back to its birth (`crust_age`).
2. **Accumulates settings** (Myr spent in each, and how long ago it last held): arc (landform 11, or
   continental crust beside a converging boundary at sea), fold belt, rift, under a plume head (within
   450 km of a frame's hotspot), sea-floor vents (ridges, oceanic arcs), deep tropical weathering
   (T >= 20 C, P >= 1200 mm, below 1500 m; weighted exp(-age/60 Myr) for survival), and the thickest crust
   the ground sat on (and when).
3. **Rebuilds the column** (`_stack_step`, numba, 10 layers, last-in-first-out): each frame's change of
   sediment cover is pushed (gain) or eroded (loss) with a lithology from that frame's setting: coal-bearing
   (peat swamp: warm >= 5 C, wet >= 1000 mm, low < 250 m, forested >= 30%; or the record's coal), source
   shale (shale on continental crust under seas < 1200 m deep, or a closed lake), evaporite, carbonate,
   volcanic, other clastic. Each layer keeps the deepest it has been buried. The result per cell: km of each
   lithology left, its present depth, and how much of it sat in the oil window (max burial 2-5.5 km, ~60-150 C
   at ~27 C/km) or the gas window (4.5-9 km). This is also the **coal-from-buried-peat proxy** PW-212 asks
   for, read off the keyframes instead of computed in the run.

Without a run (the Earth world, generated worlds) the rules fall back to the world's own layers (rock,
strata, landforms and their ages).

## 3. The resources and their rules

All in `planet/resources.py` (`likelihoods()`), each rule next to its code. `sat(x, s) = 1 - e^(-x/s)`.

| key | resource | deposit model | rule (coarse) |
|---|---|---|---|
| porphyry_cu | porphyry Cu-Mo-Au | long-lived arc magmatism, shallow (1-4 km), so young and little exhumed (Sillitoe 2010; Andes, Rockies) | 0.7 sat(arc Myr, 40) e^(-since arc/100 Myr); x0.35 on exhumed granite/shield; continental, cover < 2.5 km |
| epithermal_au | epithermal Au-Ag | hot springs over young arcs and rifts; eroded in tens of Myr | 0.65 max(sat(arc,20) e^(-since/30), 0.6 young rift); x0.15 if exhumed |
| vms | VMS Cu-Zn-Pb | sea-floor vents at ridges, arcs, back-arcs; kept in accreted terranes | land: sat(vent Myr, 25) on arc/orogen basement; sea: today's ridges 0.6 |
| orogenic_au | orogenic (lode) gold | collision belts that thickened crust, 5-600 Myr ago (Goldfarb & Groves 2015); Archean greenstone belts | 0.75 sat(fold Myr,30) ramp(max crust 45-60 km) ramp(since fold 5-25); greenstone: craton >= 2.4-2.9 Gyr, 0.15 (+0.3 near craton margins) |
| sn_w | tin-tungsten | crustal-melt granites of thick collision crust (Cornwall, SE Asia) | exhumed granite 0.55 (x1.4 if crust was > 50 km); exposed orogen ramp(max crust 50-65) |
| bif_fe | banded iron | ancient (>= 1.8 Gyr) shield, mostly at craton margins (Hamersley, Labrador) | craton x ramp(age 1.8-2.7 Gyr) x exposed x (0.15 + 0.55 margin) |
| magmatic_ni | Ni-Cu-PGE | plume melts and flood basalts on continents (Noril'sk, Bushveld) | sat(plume Myr, 30) (0.8 on craton, 0.45 elsewhere), flood basalt 0.6 |
| laterite_ni | laterite nickel | long tropical weathering of mafic/ultramafic rock | tropical weathering x flat x mafic parent (basalt, exposed ocean/hotspot crust, folded orogen) |
| bauxite | bauxite | tens of Myr of uninterrupted tropical weathering of flat, drained, aluminous ground (Guinea, N Australia) | 0.85 sat(longest unburied, unstripped tropical run, 40 Myr) x flat x drained (10-80 m above the lowest neighbour, or a plateau) x parent (sand x0.25, carbonate x0.4); x0.2 if glaciated < 5 Myr |
| sed_pbzn | sediment-hosted Pb-Zn-Cu | carbonates in forelands (MVT), red beds over evaporite in rifts (Kupferschiefer) | carbonate strata near fold belts 0.7, in rifts 0.6; rift sandstone over evaporite/shale 0.5 |
| ree | rare earths | carbonatites where rifts or plumes tap old thick continents | old continent x max(sat(plume,25), 0.8 sat(rift,25)) x 0.7 |
| placer_au, placer_sn | placers | eroding sources upstream, dropped where rivers slow | sources (gold models; tin granites) carried down `downstream` (x0.7 per cell), deposited below 600 m on bigger rivers |
| diamond | diamonds | kimberlites tap craton roots (>= 2.5 Gyr, thick) during plumes or rifts; alluvial below them | root x max(sat(plume,20), 0.5 sat(rift,20)); plus placers carried down rivers (0.6) |
| gem_meta | corundum, emerald, garnet | high-grade rock of deep collision roots, exhumed | exposed orogen x ramp(max crust 50-62 km) x exhumation (max - today's thickness) |
| coal | coal | buried peat (PW-212) within ~1.5 km | sat(coal-bearing km within 1.5 km, 0.15 km); rank from the deepest burial (lignite < 1.5 km < bituminous < 5 km < anthracite; folded bituminous -> anthracite) |
| oil | oil | source shale in the oil window, with traps | sat(source km in oil window, 0.3) x trap (folds/forelands, rifts, salt) |
| gas | gas | source shale or coal in the gas window | likewise, gas window; coal counts 0.8 |
| salt | salt and potash | evaporite beds; salt pans of closed hot basins | 0.9 sat(evaporite km, 0.5) above 6 km of cover; salt pan 0.9, salt lake 0.4 |
| obsidian, flint, clay | stone group | volcanic glass (< 2 Myr vents, young arcs and rifts); flint in limestone/chalk; floodplain mud, shale, kaolin | (simple surface rules) |
| x_mithril | deep-silver **[fantasy]** | the oldest (>= 3-3.5 Gyr), thickest craton roots a plume once rose under | |
| x_adamant | adamant **[fantasy]** | the deepest collision roots (crust once 66-76 km), exhumed | |
| x_star_iron | star-iron **[fantasy]** | seeded impact sites (deterministic from the seed), kept where the surface is older than the impact | |

Plus class layers: `resource` (the most likely metal/gem/energy/salt resource, >= 0.3), `stone` (best building
stone exposed: granite, marble = folded limestone, limestone, sandstone, slate = folded shale, basalt, tuff,
gneiss, quartzite; none under > 3 m of soil), `coal_rank`, `res_depth` (typical depth of the dominant
resource, m).

Fantasy exotics are a separate group (`fantasy`), labelled "[fantasy]" in every name, listed apart in the
hover readout and the summary, and never in the dominant map. A fourth, "aether crystals at ley/arrival sites"
from the lineages work, is left as a draft (the lineages data are not on worlds yet).

## 4. Outputs and how to run

    uv run python -m planet resources <world> [...]        # adds/redoes the layers in place (history if the run is stored)
    uv run python -m planet resources <world> --no-history  # the world's layers only
    PYTHONPATH=. uv run python tools/resources_check.py <world> ... [--earth <earth world>] [--png DIR]

- World layers `res_<key>` (u1, 0.01), `resource`, `stone`, `coal_rank`, `res_depth`; legend `resources`
  (`store.legends()`); meta `resources` (history used, keyframes).
- Summary `summary.resources`: districts (connected cells >= 0.5) per landmass ranked by score x a game-value
  weight, at most two per resource and six per landmass, plus up to two fantasy ones; the world's `.txt` gets a
  `## Resources` section.
- Viewer: layers **resources** (dominant, brightness = likelihood), **resource** (one resource; picker, `?res=`),
  **building stone**; hover rows "resources: top three with likelihoods, the first's depth", "fantasy", "building
  stone".

## 5. Checks

Four stored worlds (L6 119973, 81aced, aa6d61 Earth-like seed; L7 1144ce), % of land at >= 0.5:
porphyry 7-12, epithermal 6-10, orogenic gold 2-5, BIF 4-7, coal 2-3, oil 0.5-1.1, gas 1-2.4, salt 0.1-3,
diamonds 1.3-2.5, metamorphic gems 3-4, bauxite 0.1-2 (>= 0.25: 11-23), clay ~20, fantasy 0-1.2 each.
Porphyry belts follow the active margins and young sutures; BIF the craton margins; VMS the ridges at sea;
coal the old swamp lowlands (speckled: the column inherits the keyframes' 0.1 km cover steps and frame
flicker, PW-134). Maps: `docs/review/resources/maps/`, viewer screenshots `docs/review/resources/viewer_*.png`.

**Earth** (anchor, not target; the Earth world has no record, so this is the no-history fallback on GLiM
parent rock, `tools/resources_check.py --earth`): porphyry >= 0.25 on 14% of Andes cells and 6% of the North
American Cordillera, 0% of the Canadian Shield interior; bauxite mean 0.41 in the Guiana-Guinea tropics vs
0.08 in the Sahara. Salt shows nowhere (Zechstein, Persian Gulf): buried evaporites need the history and GLiM
rarely names evaporite as a cell's dominant rock. BIF, diamonds, gems need basement ages and collision history
Earth's world lacks (PW-132). So on Earth only the climate- and rock-driven rules can be checked; they land
where expected.

## 6. Stage 2: zoom siting (built; as built: docs/review/resources/stage2.md)

`zoom_resources.py`, run with the zoom (labels only, ~0.1 s): for each resource, the zoom's pixels inherit the
parent cells' likelihood (bilinear, as other world fields), then deposits are **sited** as points by the
resource's own fine rule and a deterministic Poisson draw (expected count = likelihood x a per-model density
per 1000 km^2, seeded by zoom id and resource):
- hard rock (porphyry, epithermal, orogenic gold, VMS, Sn-W, Ni): on the zoom's own rock/landform pixels of
  the right kind (arc volcano flanks and eroded volcano roots for porphyry; fold-belt ridges for orogenic gold;
  granite pixels for Sn-W), as points with grade (lognormal, model-specific: porphyry 0.3-1% Cu, orogenic
  gold 2-20 g/t), tonnage class, depth (exposed / shallow / deep);
- placers: on the zoom's river pixels where the gradient drops (below falls, at fan apexes, inner bends of the
  meanders zoom_fine_meander draws), and beach placers on wave-exposed shores;
- seams and beds (coal, salt, oil): as areas (outcrop polygons where the zoom's strata dip brings the bed to
  the surface; a coal seam outcrops along the cuesta scarps the zoom already draws), plus oil/gas fields as
  points on anticline crests (the fold wavelength gives the spacing);
- kimberlite pipes: points 0.1-1 km across, clustered (fields of 10-50);
- shown in zoom.html as markers with a legend and hover (type, grade, depth, size).

Fine zooms would refine the same points (veins and seams as lines) rather than redraw them.

## 7. Decisions (inbox drafts, needs-decision)

1. **When resources are made** (draft-resources-when): A. a separate command only (now); B. automatically at
   every world save from a run (+1.5-6 s); C. lazily in the viewer. Lean **B**, after the owner has looked.
2. **Fantasy exotics** (draft-resources-fantasy): A. keep the three tied to geology, off the dominant map (now);
   B. move them behind a world option; C. drop. Lean **A**.
3. **Absolute geological clocks** (draft-resources-clocks): BIF uses absolute crust ages >= 1.8 Gyr (Earth's
   iron-ocean era) and diamonds >= 2.5 Gyr roots; on a planet whose oxygenation history differs that is an
   Earth assumption. A. keep absolute (the run gives cratons Earth-like ages at set-up); B. scale to the
   planet's own oldest crust. Lean **A** for v2 (PW-443 weird worlds later).
