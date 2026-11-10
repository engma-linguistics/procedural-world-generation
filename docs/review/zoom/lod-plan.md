# Level-of-detail zooming for v1.0: globe -> 4,000 km section -> finest zoom (build plan)

Lane 282, 2026-11-10. Tickets: PW-1198 (space-to-ground globe), PW-1299 (land zoom at 4,000 km sections), PW-1296 (the
sweep). Owner 11-10: "zoom down into a 4k larger area then on down from there to even the littlest zooms we have... a
requirement for 1.0" (tag 1 Dec 2026, three weeks from today). Nothing was built or measured by this lane except the
disk sizes of existing zooms (`du`, marked "measured 11-10"); every other figure names its source, and anything worked out
here is marked *estimate*.

## In plain words

Most of the pieces exist. A regional zoom can already be 4,000 km across (up to 4,096 px), there is a fixed cut of the
planet into 54 such sections, and inside a zoom the 3D view already draws nested fine zooms (down to 25 m/px) blended into
their parent. What is missing is the **path between them**: the globe still offers only 250-2,000 km zooms at 500 px, a
zoom opens in a separate tab with no camera continuity, the server cannot build a section by its cell, nothing stops four
heavy section builds running at once, and the rung between a 4,000 km section and a 50 km fine zoom has never been tried.

**Recommendation:** explicit clicks with smooth camera flights, not tile streaming. On the globe, click anywhere: the
camera flies down to the 4,000 km section that holds that spot (one of the fixed tiling sections), built at **2 km/px**
the first time (about 4-5 min, *estimate*) and instantly after that. Inside it, double-click to fly down a rung: a
~500 km piece at 0.5 km/px, then a ~30 km piece at 25 m/px, each made by the existing fine-zoom pass (which keeps its
parent's heights and rivers, so the rungs agree by construction). Zooming out past a level flies back up. Five pieces of
work of 1-1.5 lane-days each; two pairs can run side by side, so it fits before 1 Dec with room for a judging round.

Streaming tiles that load as the camera moves (the "true" level-of-detail globe) needs a tile pyramid store and a new
renderer for the sphere; PW-1198 already puts that at v3, and it cannot hide the fact that unbuilt ground takes minutes to
make, not milliseconds.

## 1. Where we are

### The chain that exists today

| Level | What | Size, resolution | Cost to make | On disk | Source |
|---|---|---|---|---|---|
| Globe | a run's keyframe or a sliced world | L7 (~1.15 M vertices), L8; L9 opens slowly | slice: seconds to minutes | L7 elevation view ~336 MB (~96 MB gzipped) | overview.md §4; PW-1360 |
| Regional zoom (viewer default) | `planet zoom`, from a world | 250 / 500 / 1,000 / 2,000 km at **500 px** (0.5-4 km/px) | ~10-15 s at L7 (overview §2.13); 1-7 s (§4) | ~11-12 MB | overview.md §2.13, §4; `viewer/globe/zoom.js` `ZOOM_PX = 500` |
| Regional zoom, largest | same code, CLI or API | 10-5,000 km, at most 4,096 px across | see the section table below | see below | `planet/zoom/regional.py::zoom` (lines 1685-1688), `planet/api.py::parse_zoom_request` |
| Tiling section | a regional zoom on a fixed cube-sphere cell, turned to the face's "up" | 4,000 km; 54 cells, 47 hold land on dba204; neighbours overlap >= 197 km | as a 4,000 km zoom | | `planet/zoom/tiling.py`, `docs/review/land-zoom/tiling.md` |
| Matched section | a section built to agree with an already built neighbour (`--match`) | as above; exact at the owner line, 80 km blend ramp | +~10% over a lone build (*estimate* from 27 vs 30 min under load) | | `planet/zoom/match.py`, `docs/review/land-zoom/seams-round2.md` |
| Fine zoom | `zoom.fine`, from a **zoom**, not a world | each step 2-20x finer than its parent; parents of 0.1-4 km/px; at most 1,200 px across. Defaults: 50 km at 100 m from a regional zoom, 25 km at half the parent's resolution from a fine zoom | ~10 s, ~18 MB at 500 px (*design estimate* in `docs/proposals/nested_fine_zoom.md` l.21; not re-measured) | | `planet/zoom/fine.py` (`MAX_STEP`, `MIN_STEP`, `PARENT_RES`, `MAX_PX`, `default_size`, `check`) |

**4,000 km section costs** (one section; `/usr/bin/time -v` peaks):

| Resolution | Pixels | Wall time | Peak RAM | On disk (measured 11-10) | Browser: decoded layers (*estimate*) | Source |
|---|---|---|---|---|---|---|
| 4 km/px | 1,000 x 1,000 | 2.5-4.5 min (five at once) | 6-8 GB | 127 MB (d904d6, a3a793, fe600a) | ~160 MB + 11 MB satellite | seams-round2.md l.47 |
| 2 km/px | 2,000 x 2,000 | build 194 s alone (save not timed: ~4-5 min in all, *estimate*) | 23.1 GB | 497 MB (7b69a9) | ~630 MB + 45 MB | land-zoom/cost.md (after lane 122's fixes) |
| 1 km/px | 4,000 x 4,000 | 16 min 16 s alone; 27-30 min under load | 85.9 GB alone; 104-108 GB under load (budget ~110) | 2.0 GB (ce39ed, 34d0a5, 8f5874) | ~2.5 GB + 183 MB | land-zoom/cost.md; seams-round2.md l.145-148; rivers-round1.md l.131 |

The browser column is worked out from each zoom's `zoom.json` layer list (71 layers; scaled layers become float32 in
`zoom.html::fetchZoom`) and the three satellite images as RGBA; it leaves out the 3D mesh, which is one vertex per pixel
at full detail (`zoom3d.js` `opts.step: 1`): ~8 M triangles at 2 km, ~32 M at 1 km (*estimate*). For scale: three
nested tiles of 500 px drew 1.37 M triangles at 0.76 ms a frame (overview §2.15).

### Can a zoom nest inside another?

- **Fine inside regional, fine inside fine: yes**, any depth (PW-129, PW-393). A fine zoom takes its parent's ground,
  rivers, lakes, falls and volcanoes, adds detail below the parent's pixel and keeps each parent pixel's mean; the 3D view
  places each child by reprojection, cuts a hole in the parent and blends the outer 8 px (seam 0.4 m mean, 6 m max on
  3e74b0 in 97b3e7; overview §2.15). Not redrawn at the fine scale: glacier outlines, landform overlays, deltas and reef
  forms, which are the parent's interpolated (`nested_fine_zoom.md` l.192). Open quality tickets: PW-541 (box-shaped
  carving, high), PW-404, PW-391, PW-485, epic PW-516.
- **Regional inside regional: no.** A regional zoom is built from the world, so a 500 km regional zoom inside a 4,000 km
  section is a second, independent landscape: two overlapping zooms built alone differ by tens of metres on plains and
  hundreds in mountains (`match.py` docstring; `seams-round1.md`).
- **Fine inside a turned section: works but drawn wrong in 2D.** Tiling sections are turned (`up`); fine zooms are always
  north-up, and the 2D map draws their outlines unturned (PW-1341). The 3D view places them correctly.
- A fine zoom's resolution is capped by its parent: from a 4 km section the finest child is 200 m, from 2 km 100 m, from
  1 km 50 m (`MAX_STEP = 20`).

### How the viewer moves between them

- Globe (`viewer/index.html`, `viewer/globe/`): pick a cell, choose 250-2,000 km in the zoom box, press Zoom: `POST
  /api/zoom` runs a job (ids are deterministic, so an identical zoom is reused, `api.py::zoom_job`); when done, the
  **Regional zoom tab** swaps in `zoom.html` in an iframe (`globe/tabs.js::showTab`). The globe draws existing zooms'
  outlines (turned ones too). Camera: orbit, closest 1.15 planet radii (`globe/scene.js`), roughly the height at which a
  4,000 km section fills the view (*estimate*).
- Zoom page (`viewer/zoom.html`): 2D map, and a 3D view (`zoom3d.js`) entered by a button or `&view=3d&cam=...`. "Fine zoom
  here" (or shift-double-click on the 3D ground) posts a fine zoom job and adds the tile in place; the Fine zooms list
  flies to children. It loads **every layer of the zoom whole** before drawing.
- Server: 4 job workers at once (`server.py` `JOBS = 4`). Refine jobs check free RAM first (`api.py`
  `REFINE_RAM_SPARE_GB`); zoom jobs do not. The API takes `lat, lon, size_km, res_km`, not a tiling section or an `up`.

## 2. The target

The owner's flow: on the globe, pick a spot -> a ~4,000 km section opens at fine detail -> zoom further inside it, down to
the finest zoom we make (25 m/px is the finest the viewer offers today).

What "seamless" can mean by 1 Dec:

- **A. Streaming tiles** (Google-Earth style): a pyramid of tiles per level, loaded for what the camera sees, finer
  tiles replacing coarser ones as you descend, one continuous camera. Needs: a tile pyramid store, a renderer that drapes
  flat azimuthal squares onto the sphere and blends levels, and every level built in advance (a build takes minutes, so
  nothing can be made "as you fly"). PW-1198 puts this at v3. Not doable well in three weeks.
- **B. Explicit clicks with smooth transitions (recommended).** Each level is a whole zoom, opened by a click (or
  double-click) and reached by a camera flight: the globe flies down onto the section and hands over to the section's 3D
  view at a matching camera; inside, a double-click flies down to the next rung (built on first visit, a minute or less,
  *estimate*), which the 3D view already draws inset into its parent. Zooming out past a level's farthest distance flies
  back up. A breadcrumb (Globe > section > 500 km > 30 km) climbs out.

Why B: every piece except the hand-overs exists (nested tiles, `cam=` parameter, deterministic ids, the tiling); the
data stays one file per layer per zoom, so no store change; builds are cached so a second visit is instant; and it can
grow into A later (the rungs it builds are the tiles A would stream).

**The rungs** (each made from its parent by the fine pass, so heights and rivers agree by construction):

| Rung | Size | Resolution | Px | Made from | Step |
|---|---|---|---|---|---|
| Section | 4,000 km (tiling cell) | 2 km/px | 2,000 | the world (regional zoom, `--section`) | |
| Rung 1 | ~500 km | 0.5 km/px | 1,000 | the section (`zoom.fine`) | 4x |
| Rung 2 | ~30 km | 25 m/px | 1,200 | rung 1 (`zoom.fine`) | 20x |

Width ratios 8x and ~17x, so each double-click is a real dive without a jarring jump. Both rungs are inside today's
`fine.check` rules (0.5 km parent allowed; 1,000 and 1,200 px within `MAX_PX`). Rung 1's quality from a 4x step over
500 km has never been looked at: that is build step 2.

## 3. The gaps

### Generation
1. **Section by cell from the API.** `--section` exists on the CLI (PW-1338); `/api/zoom` has no `section`/`up`.
2. **The middle rung is untried.** Fine zooms have been made at 50 km from 0.5-2 km parents; a 500 km fine zoom at 4x from
   a 2 km section is legal but unmeasured (time, memory, and how it looks: the fine pass does not redraw landform overlays,
   glaciers, deltas or reefs, so a 500 km rung may look like a sharpened copy of the section rather than new landforms).
   Default sizes (`fine.default_size`) assume a 20x step, so they need a rule for this rung.
3. **Fine zooms in turned sections** are north-up (PW-1341). Building them in the parent's orientation is the simpler fix
   and also squares them with the parent's pixels.
4. **No RAM check on zoom jobs.** Four 2 km section jobs at once would want ~92 GB (4 x 23.1); one 1 km request from the
   viewer would want 86-110 GB. Refine already has the pattern (`free_ram_gb`, a spare margin).
5. **Neighbouring sections don't join** unless built matched (PW-1301/1302 done; mosaic discharge PW-1355 open). In the
   click flow only one section is on screen, so this is not needed for v1.0; it matters only if sections are shown side
   by side (PW-1359) or the sweep (PW-1296) is wanted.

### Storage
- Today: one flat `.bin` per layer, whole (`zooms/<id>/layers/`), gzipped on the wire by the server. **No pyramid is
  needed for B.** Disk per world if every land section is pre-built: 47 x 497 MB = ~23 GB at 2 km, ~6 GB at 4 km, ~94 GB at
  1 km (*estimate* from the measured per-section sizes).
- A pyramid (or at least a half-resolution copy of the drawn layers for first paint) becomes necessary for 1 km sections in
  the browser and for any later streaming; leave it to v2.

### Server
- `section` in `POST /api/zoom`; `GET /api/sections?world=` (cells with centre, `up`, corners, land share and the built
  zoom id at each resolution, if any) so the globe can draw the grid and know what is ready.
- A RAM guard on zoom jobs (refuse with a plain message when MemAvailable minus the expected peak is below a margin;
  peaks by pixel count from the table above) and one heavy section job at a time.

### Viewer
- Globe: draw the tiling cells (built / not built), click -> fly down -> hand over to the section's 3D view with a matching
  camera, without a tab change that resets the view; fly back out when zoomed out past the section.
- Section: double-click -> fly to the spot; draw the rung if it exists, else build it (progress on screen) and inset it;
  a breadcrumb; outlines of children turned correctly in 2D (PW-1341's viewer half).
- Memory: `zoom.html` decodes every layer up front (~0.63 GB for a 2 km section, ~2.5 GB at 1 km, *estimates* above). Load
  the layers the view draws first and the rest when asked; unload a rung's data when you leave it.

### Cost of a 4,000 km section, by candidate resolution

| | 4 km/px | 2 km/px (lean) | 1 km/px |
|---|---|---|---|
| First visit (build) | 2.5-4.5 min | ~4-5 min (*estimate*: 194 s build + save) | 16-30 min |
| Peak RAM | 6-8 GB | 23.1 GB | 86-110 GB: night only (shared-machine rule) |
| Disk per section / per world (47) | 127 MB / ~6 GB | 497 MB / ~23 GB | 2.0 GB / ~94 GB |
| Browser, layers only (*estimate*) | ~0.17 GB | ~0.68 GB | ~2.7 GB (above what L9 worlds already find slow, PW-1360) |
| Finest fine-zoom child (20x) | 200 m | 100 m | 50 m |
| All 47 land sections of a world, one at a time | ~2.5 h | ~3.5-4 h (*estimate*) | ~12.5 h alone (cost.md) |

## 4. Build steps

Each is 1-1.5 lane-days. **Steps 1 and 2 run side by side first; then 3 and 5 side by side; then 4; step 6 is an
overnight job any time after 1.** Total ~6 lane-days, ~4 calendar days with two lanes, leaving time for Daniel to judge
and for a fix round before 1 Dec.

1. **Sections and rungs in the API (zoom/server, 1 day).** `POST /api/zoom {world, section, res_km}` (Frame with the
   cell's `up`); `GET /api/sections?world=`; RAM guard on zoom jobs and one heavy section job at a time; fine zooms built
   in their parent's orientation (fixes PW-1341's generation half). *Done when:* the API builds or reuses `px.1.1` of a
   showcase world at 2 km; the sections listing marks it built; a 1 km section request on a busy machine is refused with
   a message naming the RAM it needs; a fine zoom of a turned section has the parent's `up`; `uv run pytest -q` passes.
2. **The rung chain, measured and judged (zoom, 1 day; CLI only, parallel with 1).** On one land section of a v1.0
   showcase world at 2 km: rung 1 (~500 km at 0.5 km) and rung 2 (~30 km at 25 m) by `zoom.fine`, at three places
   (a mountain range, a river plain, a coast). Measure wall time, peak RAM, disk per rung; check parent-mean bias and river
   continuity at each rung's edge; compare rung 1 with a regional 500 km zoom at 0.5 km of the same spot for what it lacks
   (landform overlays, glaciers, deltas). Fix `fine.default_size` for the rung sizes. *Done when:*
   `docs/review/zoom/lod-rungs.md` has the numbers and pictures and a yes/no on rung 1's quality (no means question Q3
   below goes to Daniel with pictures).
3. **Globe to section and back (viewer, 1.5 days; after 1).** The globe draws the world's tiling cells; a click flies the
   camera down to the cell's section, builds it if needed (progress shown), and hands over to the section's 3D view at a
   matching camera (`cam=` already exists); zooming out past the section flies back to the globe. *Done when:* on a
   showcase world Daniel can go globe -> section -> globe with no page reload and no jump of the camera visible to the eye
   in a screen recording.
4. **Down the rungs (viewer, 1-1.5 days; after 2 and 3).** In a section, double-click flies to the spot and opens the rung
   that covers it (building it if needed, with progress), drawn inset as today; again from rung 1 to rung 2; a breadcrumb
   climbs out; children's 2D outlines turned with the section. *Done when:* from the globe, three clicks reach a 25 m
   tile and the breadcrumb (or zooming out) climbs back to the globe; fine tiles sit right in a turned section in 2D and 3D.
5. **Viewer memory (viewer, 1 day; parallel with 3).** `zoom.html` loads the drawn layers first, the rest on demand; a
   rung's buffers are freed when you leave it. Measure with `tools/viewer_perf.py`-style stages (heap, renderer RSS).
   *Done when:* globe + 2 km section + both rungs open stays under ~1.5 GB of renderer memory (target, to be confirmed by
   the first measurement), and opening a 2 km section takes under ~5 s on a warm server.
6. **Pre-build the showcase worlds' land sections (overnight, 0.5 day of setup).** All land sections of the v1.0 showcase
   worlds at the chosen resolution, one at a time, at most 8 cores, logged. *Done when:* every land cell of those worlds
   opens instantly, and the log has time, peak and disk per section.

Steps 1-4 are the requirement; 5 is needed if the section is 1 km or if step 3's measurements show the browser struggling;
6 is a comfort (without it the first click on each section waits a few minutes).

### Questions for Daniel

**Q1. How sharp is the 4,000 km section?** It is the first thing you see after the globe.
- A. 4 km per pixel: ready in ~3-4 min the first time, light everywhere, but only 1,000 px across (a bit soft when it
  fills the screen), and the finest zoom under it can only be 200 m without the middle rung.
- B. 2 km per pixel: ~4-5 min the first time, 23 GB while building (fine by day, one at a time), 2,000 px across. (lean)
- C. 1 km per pixel ("4K" across, 4,000 px): the sharpest, but 16-30 min and ~110 GB per section, so only overnight, ~2 GB
  of disk each and ~3-4 GB in the browser, which needs step 5 and probably a pyramid.
- Lean **B for 1.0**, with C as an "overnight sharpen this section" option after the tag.

**Q2. Where does the section sit when you click?**
- A. The fixed grid section (one of 54 per planet) that holds your spot: built once and reused by every later click
  there, its neighbours line up with it, and the whole land can be pre-built overnight. Your spot may be off-centre
  (always at least ~100 km inside the edge). (lean)
- B. A new section centred on exactly where you clicked: the spot is in the middle, but every click is a new 4-5 min
  build, and two sections never line up.
- Lean **A**.

**Q3 (only if step 2 says rung 1 looks thin). What fills the 500 km rung?**
- A. The fine-zoom pass (as planned): agrees with the section exactly, cheap, but carries the section's landforms,
  glaciers and deltas sharpened rather than redrawn at 0.5 km.
- B. A new "regional zoom held to its parent" mode that redraws the landforms at 0.5 km but keeps the section's heights
  and rivers: richer, ~3-5 lane-days and riskier (*estimate*), probably not before 1 Dec.
- C. Skip the middle rung: from the section straight to a ~100 km piece at 100 m (the 20x step today's code allows), so a
  bigger jump between levels but nothing new to build.
- Lean **A for 1.0**, B as a v2 quality ticket if the pictures show it is needed.

Not a question, a note for the board: the owner's flow does not need the whole-planet sweep with matched seams
(PW-1296) or the mosaic discharge pass (PW-1355): one section is on screen at a time. Their v1.0 milestone can go back
to later unless Daniel wants side-by-side sections (PW-1359) for 1.0.

## 5. Risks

- **Memory under the shared cap (all lanes <= 32 cores, ~90 GB by day; no 1 km zooms by day).** A 2 km section peaks at
  23.1 GB and uses ~7 cores (1 km ran at 713% CPU, cost.md); with the server's 4 job workers, two clicks plus a lane's sims
  could pass 90 GB, hence step 1's RAM guard and one section job at a time. 1 km sections are night-only (86-110 GB).
  Rungs are fine zooms of <= 1,200 px: small (*estimate*, measured in step 2). Pre-building (step 6) runs overnight,
  one at a time, at most 8 cores. The memory floor ticket PW-1337 (target <= 40 GB at 1 km) would make 1 km sections
  possible by day; it is not needed for 2 km.
- **Consistency at seams.**
  - Globe -> section: the section keeps each coarse cell's mean height (inland bias -3 to +2 m on the showcase zooms,
    overview §2.13), but its satellite colours differ from the globe's palettes; the hand-over should cross-fade, not cut.
  - Section -> rungs: by construction (parent pixel means and rivers kept; 3D seam 0.4 m mean, 6 m max measured).
    Known flaws at the finest rung are quality tickets, not seams: PW-541 (box-shaped cuts, high), PW-404, PW-391
    (fine rivers can carry less water than the parent's).
  - Section -> neighbouring section: built alone they disagree in their overlap (tens of m on plains, hundreds in
    mountains; seams-round1.md). Invisible when one section is shown at a time; matched builds (match.py) exist if
    pre-building wants them, at ~10% more time.
  - A spot near a cell edge is still >= 97 km inside its section (tiling.md), more than the fine pass's edge margin
    (3 parent px = 6 km at 2 km), so a rung always fits.
- **Browser memory.** The globe stays loaded under the section (an L7 elevation view is ~336 MB of layer files,
  overview §4); a 2 km section adds ~0.7 GB of decoded layers plus an ~8 M-triangle mesh (*estimate*), rungs ~0.1 GB each
  (*estimate*). Fine for 2 km; 1 km (~2.7 GB layers + ~32 M triangles) would sit where L9 worlds already open slowly
  (~4 GB, PW-1360). Step 5 is the guard.
- **Untried rung.** If rung 1 looks like a blurred section, the flow still works (Q3 C) but feels thin; step 2 finds out
  in the first two days, before any viewer work depends on it.
- **Schedule.** Six lane-days of work over three weeks with two lanes is comfortable only if each step lands in one
  pass; the three-strikes rule applies to steps 2 and 3, which carry the unknowns.
