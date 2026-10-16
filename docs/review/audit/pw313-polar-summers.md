# PW-313 / PW-112: polar summers and Antarctica at dT 0 (not fixed: what it takes)

Branch `worktree-agent-aa87b215cc4ac7911`, on main 6392e18. **No model change is merged.** PW-313's acceptance (the probe keeps ~3% at dT 0) can't be met from the temperature side. Every sound temperature fix I found leaves the probe decaying, because Antarctica's margins get too little snow. The fixes that make the probe hold do so by overcooling, which is the compensation PW-112 complains about. Measurement tool: `tools/ice_probe.py` (8 climate updates on Earth's L6 bed from the real ice), plus the station and band comparisons below (NCEP 2 m temperature via `tools/earth_data.py`).

## Short answer
- **Earth's real ice-free polar lowlands were 1-4 °C too warm in summer, and the cause is the frozen sea's summer air.** The land's air carried the open sea's seasonal swing on top of the freezing point (+4 °C over the pack ice at 80°). The sea's own summer air had the winter's sea-ice cold (-11 to -12 °C over 75-90N; observed +0.8). One definition fixes both: the sea's summer surface as `ocean.open_share` already sees it, floored at freezing. Every coastal band from 70 to 85N then matches NCEP within 1 °C (table 1). But it dries the poles: the warmer air over the polar seas condenses less onto the coasts. Antarctica gets 66 -> 55 mm and Greenland 212 -> 192 mm at dT -6, and the probe's dT -6 ice falls from -44 to -30 m.
- **Antarctica's bed summer (+13 °C) can't be checked against Earth.** No ice-free polar continent exists. Reshaping `temperature()`'s polar end to Earth's ice-free land, which it was never fitted to poleward of 65° (it sits 4-8 °C above it), does fix Antarctica's ice surface. But it cools the Siberian Arctic coast and Yakutia summers by 3-4 °C against observations that the current curve gets right. Rejected.
- **The observable error is the ice surface.** Antarctica's ice-surface summer is 5 °C too warm at the median, and 12-18 °C too warm on the plateau (PW-039). The sheet's own air mass is only a local damping of each ice cell (`icemass.sheet_cover`). The air that reaches the margins, ice shelves and WAIS still comes off a bare +13 °C ground. Letting the winds carry the ice's own summer air (katabatic outflow) brings the Antarctic coast and WAIS to within 0-4 °C of stations, and halves the plateau error. It costs Greenland's interior ~3 °C (table 2).
- **With Antarctica's surface summers right, the probe still decays.** Its losing margins sit at the observed summer temperature (-4.0 vs -4.7 °C) and get ~100 mm/yr of snow, a fifth of what it takes there. The ice shelves get 20-60 mm against ~100-250 observed, and Antarctica 70-80S gets 193-200 mm against GPCP's 412. So **the remaining driver is the margins' snowfall (PW-013's rain transport)**. With the carried sheet air and Antarctic snowfall x2.5 (a diagnostic), the probe holds at ~2.6% (-50 m) over 8 updates. The snowfall alone, or the temperature alone, doesn't hold.
- **PW-226 is already fixed** (by PW-276). The `-95 °C` bound is back in `tests/test_invariants.py`. In the ticket's L4 sweep the coldest land months are -61 to -83 °C on thin (340-380 m) caps over 5.2-6.8 km ranges. A new, separate finding: over the sea in a deep L4 icehouse (dT ~-12), the sea-ice air reaches **-114 °C**, because `3 x (t_sea_air - freezing)` amplifies without limit.

## 1. The frozen sea's summer air (ready, not merged)
`climate._air_temps`: the land's summer air over a sea was `sst + sea_half` (sst floored at -1.8), and the sea cells' own was `sst + sea_half + 3 x frozen`. Both become `max(sst + frozen + sea_half, FREEZE)`, with `frozen = min(t_sea_air - t_sea, 0)`. That is the seasonal sea surface `ocean.open_share` uses, and it can't be colder than melting ice.

Table 1. Ice-free land, 55-85N, by band: warmest month model / NCEP, °C (no vegetation feedback).

| band | coast (≤1 cell), before | coast, after | inland (≥300 km), before -> after (obs) |
|---|---|---|---|
| 60-65 | +9.3 / +11.1 | +9.3 | +14.3 -> +14.2 (+15.1) |
| 65-70 | +8.0 / +9.3 | +7.7 | +12.2 -> +12.1 (+13.2) |
| 70-72.5 | +7.1 / +6.0 | +6.1 | +12.0 -> +11.8 (+11.7) |
| 72.5-75 | +6.1 / +4.3 | +4.5 | +12.2 -> +11.7 (+10.5) |
| 75-80 | +4.4 / +1.3 | **+1.9** | - |
| 80-85 | +3.4 / -0.6 | **+0.4** | - |
| Arctic Ocean air 75-90N | -7 .. -12 / +0.8 | **+0.3 .. -1.3** | |

(An annual-sst clip, `swing x clip((sst+1.8)/4)`, tried first, also got 75-85N right. But it cooled the 60-70N coasts by 3 °C, because their seas freeze only in winter.)

earth_check (with vegetation), before -> after: land T 80-90N -19.2 -> -20.5 (obs -21.0), 70-80N -17.8 -> -18.3 (-16.4); land rain 80-90N 139 -> 108 mm (GPCC 168), 70-80N 247 -> 223 (227), Antarctica 70-80S 200 -> 193 (GPCP 412). Köppen group agreement 70-80N 82 -> 81%, 60-70N 79 -> 78%. Global P and T unchanged; rain elsewhere moves ≤ 3 mm.

Probe: dT 0 0.10 -> 0.12% (no help), dT -6 -44 -> -30 m, dT -9 -104 m. The drying is right in itself: the old -12 °C summer air over the polar seas wrung out vapour that real ~0 °C air keeps. But merged alone, it makes cold eras poorer in ice. It belongs with the snowfall fix (draft `draft-frozen-sea-summer-air.md`).

## 2. What is wrong over Antarctica, and what isn't
Bare-ground ("ground") and ice-surface climate on Earth's real ice (L6, dT 0), medians by bed height. Model / NCEP, °C:

| bed km | surface T | surface Tw | surface Tc | ground Tw | snow mm |
|---|---|---|---|---|---|
| 0-0.5 (847 cells) | -25.1 / -29.6 | -7.6 / -12.3 | -46.3 / -42.2 | +13.9 | 53 |
| 0.5-1 | -32.1 / -38.6 | -13.7 / -18.8 | -52.9 / -49.6 | +10.3 | 31 |
| 1-1.5 | -31.9 / -38.3 | -12.8 / -20.2 | -52.9 / -48.1 | +6.9 | 24 |

The ground's summer is `temperature()` at the pole (-10 °C) plus the continental half-swing (24 °C x 0.98): +14 °C for land the sea's air doesn't reach. `evap_cool`'s dry-ground term adds 0 at the median over Antarctica (±1.5). At Earth's real polar coasts this land summer is right once the sea air is fixed (table 1). Siberia and Yakutia at 60-72N confirm it inland. The bare polar continent beyond 75° has no analogue. I looked for a physical limiter: snow lying into the summer (the spring snow-albedo delay) melts away before the sinusoid's warmest month on a dry continent, and the insolation doesn't argue for a smaller polar swing. So I left the ground alone.

Diagnostics on the probe at dT 0 (after 8 updates; base 0.10%, -0.5 m):

| variant (diagnostic only) | ice share | sea level |
|---|---|---|
| ground summer -4 °C poleward of 60° | 1.24% | -12 m |
| ground summer -8 °C | 4.35% | -57 m, steady |
| polar snowfall x2 / x3 | 1.92% / 5.92% | -21 / -102 m |
| `SUMMER_DAMP` 0.8 | 0.22% | |
| full air-mass cover on Antarctica's margins | 0.81% | |
| both (Antarctic ice-surface Tw then within 1-2 °C of NCEP at every bed height) | 1.74% | -19 m |
| polar land curve reshaped (-8 °C at the pole) | - | Siberia 4 °C too cold: rejected |

So with the ice surface right, it still decays. Probe update by update (that variant), Antarctic cells 946 -> 848 -> 755 -> 679 -> 621. The first rebuild thins the kept ice by 560 m (the Nye surface from the margins, x0.82 for the dry sheet). After that, every lost cell is one with a negative balance: the Ross and Ronne shelves (82-85S) at -7 °C with 22 mm of snow.

## 3. Carrying the ice sheet's own summer air (the measured option)
The design. `climate.compute` gives the air over land ice the ice's summer: its warmth above the mean x (1 - `SUMMER_DAMP` x the sheet's air mass, the old `sheet_cover` formula). The summer carry (`_air_temps`) takes that air on along the winds. `icemass.sheet_cover` becomes just the surface's own share (`LOCAL`) in the run, the time zoom (whose 10 kyr full climate passes its ice) and the zoom alike, so the air mass isn't counted twice. About 40 lines in climate.py / icemass.py / timezoom.py. The ground under Antarctica's bed then has summers of +0..+4 °C at sea level, the "0 to +5" PW-112 asked for, but through the air rather than the bare ground.

Table 2. Stations, model at the station height (lapse rate from the cell's surface) vs climatology, warmest month °C:

| station | base | carried air (air-mass weighted) | carried air (full damping) | obs |
|---|---|---|---|---|
| South Pole | -9.9 | -18.7 | -20.6 | -28 |
| Vostok | -14.4 | -22.8 | -24.6 | -32 |
| Dome C | -18.2 | -21.3 | -24.0 | -30 |
| Byrd (WAIS) | -7.8 | -10.3 | -13.7 | -14 |
| Halley (shelf) | +5.2 | -2.8 | -5.8 | -4 |
| McMurdo | -2.7 | -0.6 | -1.9 | -3 |
| Mawson | +1.7 | -0.1 | -3.2 | 0 |
| Summit, Greenland | -13.3 | -16.6 | -23.2 | -12 |
| NEEM | -11.9 | -12.5 | -18.9 | -11 |
| Swiss Camp | -4.2 | -6.5 | -8.4 | 0 |
| Danmarkshavn (bare) | +2.1 | -0.1 | -2.7 | +4.2 |

| probe (after 8 updates) | dT 0 | dT -6 | dT -9 |
|---|---|---|---|
| base | 0.10%, -0.5 m | -44 m | |
| carried air, air-mass weighted | 1.18%, -14 m (Greenland decays too: 145 -> 96 cells) | -55 m | -131 m |
| carried air, full damping | **2.96%, -48 m, steady** | -87 m, growing | |
| air-mass weighted + Antarctic snowfall x2.5 (diagnostic) | 2.55%, -50 m, near steady | | |
| frozen-sea air only + Antarctic snowfall x2.5 (diagnostic) | 1.73%, -28 m | | |

The full-damping variant passes the probe, but only by putting Greenland's summit 11 °C too cold. It is the "ice right through a compensating error" pattern, so I didn't take it. The air-mass-weighted variant is the sound one. It needs the snowfall to hold Antarctica, and it trades Antarctica's plateau (+9 °C better) against Greenland's interior (~3 °C colder; its margins lose some damping, so Greenland too decays in the probe). That is a judgement call (draft `draft-ice-sheet-air-carried.md`).

## 4. PW-226
`tests/test_invariants.py::test_values_sane` has asserted `-95 < t_cold.min()` again since PW-276 (the sheet's surface rises from the bed at its edge, so a cap on a high range is thin). The ticket's sweep (L4, seeds 1-5, 300 Myr, main 6392e18) gives coldest land months of -69, -80, -83 and -61 °C on seeds 1, 2, 4 and 5, all on 340-380 m caps over 5.2-6.8 km of bed. Seed 3's coldest is **-114 °C at sea** (elevation -3954 m, no ice) in a deep icehouse (60 Myr: global 2.5 °C, 14% ice, sea level -513 m). Over sea ice, `_air_temps` uses `t_cold = sst - sea_half + 1.5 x 3 x (t_sea_air - t_sea)`, which grows without limit as the latitude's would-be sea temperature falls. Draft `draft-sea-ice-air-unbounded.md`.

## Inbox drafts
- `draft-frozen-sea-summer-air.md`: the fix in section 1, to land with the Antarctic snowfall (it dries the poles).
- `draft-ice-sheet-air-carried.md` (needs-decision): section 3's options.
- `draft-antarctic-margin-snowfall.md`: the probe's remaining driver, for PW-013.
- `draft-sea-ice-air-unbounded.md`: the -114 °C sea-ice air of deep icehouses.
