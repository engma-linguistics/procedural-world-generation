# Zoom batch 5: PW-356, 357, 124, 061, 116 (2026-10-16)

Measured as in pw298.md / batch4.md: world 592f2a (showcase L7 seed 3199 @ 380 Myr), its 8 highlight zooms plus
the plateau -48.48, 60.12, each built with zoom seeds 1-5 (`zoom.build` in memory). "Drops" are `stats.falls` of
kind `drop` >= 100 m; "inland" is `stats.inland_cell_mean_*`; "perched" counts river pixels (>= 100 m^3/s) with
land (< 30 m^3/s) within 2 px lying more than 30 m below every river pixel within 2 px of it (PW-124's metric).

## PW-356: the bed below the sea under grounded ice

Worlds store the true bed (PW-307); the zoom took a sub-sea bed under grounded ice at 1 m (the land view). The
terrain passes still build on that view (`zoom.land_world`, which replaces `zoom_world`): they take land as
ground above the sea (rivers graded to it, lakes, creep), and under a grounded sheet there is no subaerial
landscape for them to shape anyway. After the climate, the bed under the zoom's glaciers sinks by each coarse
cell's depth below the view (interpolated as the coarse heights are, then 12 smooth passes correcting each such
cell's iced pixels to the true bed's mean), and the ice thickens by as much. A load's dip or a marine basin is
hundreds of km wide, so a smooth offset is the right shape at the zoom's scale; the relief is the view's.

World 85922d (finished from time zoom 080df3 @ 950 kyr, sea level -101 m; 2564 cells on a sub-sea bed, -349 m
mean, to -1502 m), zoom -55, -80 (1000 km @ 4 km), seed 1; 48% of its pixels lie in such cells, 98% of them iced:

| | before | after |
|---|---|---|
| bed under the ice in those cells (mean; the cells' -476 m) | +15 m | **-452 m** |
| per full-ice cell: mean bed - true bed (p10 / p50 / p90) | +213 / +397 / +1086 m | **-7 / +1 / +6 m** |
| inland cell bias / RMS against the true bed (against the view before) | +14 / 17 m | **-1.5 / 12 m** |
| ice surface, water layer | | unchanged (max 0.0003 m) |

The remaining large cell errors are coastal cells with sea pixels in them (their sea floor is the coarse sea's).
Bare land in such a cell (0.0% here) keeps the view's ground above the sea. The 592f2a zooms have no such cells:
unchanged. Test: `test_marine_sheet_keeps_its_sub_sea_bed` (a synthetic marine sheet: no sea there, each cell's
bed within 15 m of -500 m, surface, ice outline and water identical to the land view's build).

![bed](pw356_bed.png)
*The bed (ice off) of zoom -55, -80 on world 85922d, before | after: under the marine sheet the bed lies 300-1300 m
below the sea (blue) instead of at ~1 m; the coast and the ice-free land are unchanged.*

## PW-357: tongues fed along their zone's margin

`glacier_flow` counted a tongue's run (GL_MAX_KM = 100 km) from where its biggest feeder left the accumulation
zone. A tongue running along the zone's margin, fed by it pixel after pixel, used up its 100 km there and was cut
at the cap still carrying the 3 km^3/yr GL_F_MAX flux. Now the run counts from the last pixel the zone itself
drains into: along the margin the tongue is the zone's edge (its excess over the cap lost along that margin, as
GL_F_MAX's rationale has it), and it ends where its melt has used up its flux.

The test massif of `test_zoom_ice` (900 km @ 3 km): the 8 biggest tongue ends carried 1.6-2.8 km^3/yr at runs of
97-99 km (6.0 km^3/yr in all cut by the cap); now every end has melted out (flux ~0; longest run 82 km). Ice on
ground with > 12 C summers 0.28% -> 0.47% of the ice (the test allows 0.5%: big maritime outlets do end in
rainforest), ice volume +0.6%. The 592f2a zooms: only the glaciated 49.32,37.38 moves (inland bias / RMS +1.3 / 54.9
-> +1.7 / 55.6 m; ice 30.0 -> 29.9% of the area; drops unchanged). Test: `test_tongue_along_the_zone_ends_by_melt`.

![tongues](pw357_tongues.png)
*The test massif's western margin (3 km pixels), before | after: tongues cut at the run cap now go on down
their valleys until they melt out.*
