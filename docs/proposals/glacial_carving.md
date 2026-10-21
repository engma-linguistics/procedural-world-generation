# Glacial carving: design note (PW-037, 2026-10-16; ported onto the glacial index 2026-10-20)

Owner's wish: "great lakes and glacial escarpments and smoothed-out landscape, or whatever ancient
retreating/advancing glaciers did": scoured shields with many lakes, overdeepened basins and great lakes
at ice-sheet margins, moraines, drumlin-smoothed ground, escarpments; U-shaped valleys and fjords.

## Where it lives

Two scales, two homes:

- **Coarse imprint: the glacial time zoom** (`planet/timezoom/`, 56 km cells at L7, 110 km at L6). It is the only place
  where ice sheets flow, advance and retreat through orbital cycles, so it is where the imprint is
  made. The ice erodes its bed as it slides, carries the debris with the flow and drops it where it
  melts or calves; the bed it flows on is the carved one (troughs focus flow; carving feeds back). Each
  frame stores the cumulative erosion and till, and the frame's `elevation` already holds the carved,
  till-covered bed. Basin-scale features come out here: overdeepened basins where fast ice crossed soft
  rock (Great Lakes on the shales and carbonates beside a shield), stripped shields, till and moraine
  belts at long-lived margins, troughs under outlet streams (fjord *systems*, trough-mouth fans).
- **Fine imprint: the regional zoom** (PW-092, after this ticket). A finished world (`planet finish
  <timezoom> --kyr N`) carries the imprint as world layers (`glacial_erosion`, `glacial_till`,
  `ice_max`; `glaciated_myr` = 0 where the time zoom's ice reached), so the zoom can synthesise the
  sub-cell forms: U-shaped valleys, cirques, fjords, drumlins and eskers along the flow, kettle and
  finger lakes. This ticket does what is cheap and sound at the coarse level and hands the rest on.

The main run is untouched (its long-term glacial erosion is `earth.py`'s ×3 under temperate ice).

## Model (per 500-yr step)

- **Basal temperature** (is the bed thawed, so the ice slides?): Robin's (1955) steady column with
  the heat into the base G and the step's accumulation rate a: the bed is
  T_s + (G/k)·L·(√π/2)·erf(H/L) warm, with L = √(2κH/a) (pure conduction where a ≤ 0). Thawed where
  that reaches the pressure-melting point (−0.00087 °C/m × H), a 2 °C ramp to frozen. G is the
  geothermal flux (65 mW/m²) plus the flow's own heat at its bed, τ_b·u (the work of sliding and of
  the shear concentrated near the bed; Cuffey & Paterson 2010 ch. 9: 0.1–1 W/m² under fast ice). So
  slow, thick, cold domes are frozen to the bed (little erosion, preserved landscapes, as under the
  Keewatin dome) and fast outlets and wet margins slide. (Without the flow's heat, Robin's column
  alone froze 80–95% of the northern sheets' beds and Earth eroded ~5 m/Myr on average: attempt 1.)
- **Sliding speed** u_b = `slide_share` (0.5) × the shallow-ice depth-averaged speed (the time zoom's
  enhancement already stands in for sliding) × the thawed share, the speed taken at a basal shear
  stress of at most `tau_y` = 100 kPa (Nye's plastic bed; ice sheets' basal stresses are 50–150 kPa).
  The shallow-ice speed goes as τ_b³ H, and τ_b = ρ g H |∇s| passes the bed's yield stress only on
  the grid's cliff-like margins (a 1–2 km step across one cell) or on a sheet far from balance,
  collapsing or piling up (a run moment's drift); there the extra fall is unresolved margin, not
  faster abrasion, so the speed is scaled by (τ_y/τ_b)³. This is the limiter PW-418 asked for
  (its option a, made physical): the extreme D|∇s|/H values (p99 ~1.8 km/yr on Earth) sit there.
- **Erosion** Ė = K_g · erodibility · u_b^l with l = 1 and K_g = 4e-6 (Hallet 1979's abrasion law;
  Herman et al. 2015 fit l ≈ 2 on one valley glacier, Cook et al. 2020's compilation gives l 1–3; at
  cell-mean speeds the linear law with the observed range, ~1 mm/yr at 250 m/yr of sliding, is the
  robust choice). Erodibility is the rock table's (`surface.ROCK_K`):
  the cover (km of sediment in the run's record) first, then the basement under it once the cover is
  stripped (shield 0.3, shale 1.6), so soft basins are scooped out to their hard floors.
- **Overdeepening limit** (Alley et al. 2003): where the bed rises downstream more steeply than
  `adverse` (1.5) × the ice surface's fall, meltwater supercools and freezes, so the basin stops
  deepening. This is the physical bound on great-lake depth (no clamp).
- **Debris**: the eroded rock is carried in the ice (a debris column advected with the ice flux in
  `sia_flow`) and released where the ice thins by melt (in proportion), floats off or calves. So till
  sheets and moraine belts build where margins stand for long, ice-marginal stillstands make ridges,
  and the sea floor off marine fronts gets trough-mouth fans. Volume is conserved (erosion = till +
  debris still in the ice).
- **Isostasy of the rock**: removing or adding rock unloads or loads the lithosphere: ρ_rock/ρ_mantle
  ≈ 0.82 of the net change spread over the same flexural scale as the ice load (~150 km), relaxing with
  the ice's `iso_tau`. A shield-wide planation is mostly compensated; a single carved trough is not.
- **Sea level** keeps counting only the ice (the bed's reference moves with the carving).

## In the finished world

- Bed = the frame's carved bed, so the world's hydrology fills the hollows with lakes on its own
  (great lakes behind till belts and in overdeepened basins; proglacial lakes against the ice as now).
- The sub-cell texture's low-relief noise is planed where the ice eroded: exp(−E / 180 m) of it stays
  (ice sheets smooth lowlands: drumlinised, scoured ground); the mountains' ridged part stays (alpine
  ice sharpens peaks; arêtes are the zoom's).
- The sediment cover loses what the ice stripped and gains the till, so stripped shields expose their
  basement (the zoom's shield landform then scours them, `glaciated_myr` = 0).

## Not here (follow-ups)

Fine-scale forms (PW-092); outwash plains and loess (PW-096, merged into this ticket: needs the
meltwater routing); eskers; proglacial-lake termination of the 100-kyr cycle (PW-030); shelf-scale
fjord carving (cells too coarse).
