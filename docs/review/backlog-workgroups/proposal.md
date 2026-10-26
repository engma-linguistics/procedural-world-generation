# Backlog workgroups (PW-900 proposal)

Date: 2026-10-26. Read-only review: no ticket was changed. Board snapshot: 380 open tickets (v1 41, v2 178, v3 17, later 74, unscheduled 70; `board.py milestones`). Note that state.md still says "2 open in v1", but the board shows 41 open v1-milestone tickets (most are the v1-finish audit findings); state.md should be refreshed.

**Lead.** The open board is really about fifteen bundles of work. Four finish v1 (Earth-like physics): the carbon and star balance, the finish moment and its checks, Earth-likeness of the geology, and a short zoom and viewer tail. Seven make v2: a peoples refactor plus ice-age-aware ranges, cultures and mixing, the history zoom with tech, the culinary brief, domestication, the resources layer, and zoom/coast quality. Three more are v2 enablers: viewer for peoples, speed and memory, and a tectonics quality pass. The ice-age physics (PW-470) and base-climate (PW-570/013) piles are large, parked, and best treated as late-v2 lanes with their own review. Weird worlds and civilizations beyond the first steps are v3. Each group below is meant to end on a merge with a refactor pass, named in the last column. Counts are open tickets I assigned; sets are approximate and a few tickets could sit in two groups.

## Workgroups

Viewer column is what the owner sees when the group ships. "Refactor" is the module that probably needs a split or a shared-helper pass.

| # | Name | Goal | Milestone | Tickets | Depends on | Owner sees in viewer | Refactor checkpoint |
|---|---|---|---|---|---|---|---|
| A | Carbon and star balance | Make the end-anchored carbon/star balance sound and documented so 1 Gyr runs hold ~70% passing | v1 | 791, 809, 810, 812, 813, 814, 815, 816, 819, 822, 865, 872, 873, 874, 875, 880, 881, 894, 895, 896, 897, 898, 899 | nothing (serial physics lane) | Runs stay habitable; temperature and CO2 readouts honest; star anchor shown in the run page | `climate.py` (2.8k lines): split greenhouse/weathering from the temperature solver; `tectonics/earth.py` carbon source |
| B | Finish moment and v1 checks | Take the finished world at a human-habitable moment and prove it on several seeds | v1 | 807, 808, 821, 823, 824, 825, 828, 829, 866, 892 | A (needs the settled balance) | Finished worlds that look like "now": Earth-like temperature, trees in wet tropics, ice-age bar documented; Earth anchor world rebuilt | `finish.py` and `timezoom/sim.py`: one place for the finish-moment pick |
| C | Geology realism tail | Fix the Earth-scale geology misses the owner asked about | v1 | 817, 818, 826, 827, 846, 849 | none (independent lane) | Iron deposits on young land, believable shelves, no half-planet plate, taller mountain ranges, waterfall count | `tectonics/` plates and relief; `surface.py` |
| D | Zoom and polish tail | Last visible zoom defects plus the geological brief export | v1 | 844, 847, 848, 882 | none | Harbours show in the south polar zoom; deltas stop looking like a hand; a downloadable zoom brief | `zoom.py` (3.7k lines) and `zoom_fine.py` (2k): peel off delta/coast code |
| E | Peoples refactor and ice-age ranges | Split history.py, then make ranges follow the last ~300-400 kyr of climate and sea level, origins by habitable area | v2 | 900 (this), 901, 902, 903, 888, 889, 868, 698, 656, 654, 664, 602, 748, 771 | A and B for a stable world; 901 first | Peoples maps that change with sea level; land bridges used; insular vs exploratory peoples; refuges behind ice | `lineages/history.py` (1.6k lines) into origins/dispersal/contact/events (PW-901); `spec.py` (910) |
| F | Cultures, settlements, mixing, attitudes | Make the culture the unit of the book: settlements, mixing preset, attitudes, folklore, light gods | v2 | 856, 910, 904, 905, 906, 907, 666, 704, 752, 758, 759, 751, 756, 773, 757 | E (needs ranges and the split) | Culture layer: settlement species shares, city quarters, attitude map, gods per culture | New `lineages/culture` package; `brief.py` (1.1k) |
| G | History zoom and tech | History from a per-region farming onset at 25-yr steps, a visible tech tree, polities in first steps | v2 | 908, 909, 913, 675, 713, 714, 661, 670, 676, 785, 794, 832, 833 | F, E; D for fine zooms | A time scrubber for the last ~12 kyr; a tech-tree tab (global and per civ) with a mid-1400s stop | Needs its own package; share stepping code with `timezoom/sim.py` |
| H | Culinary brief and salt | The end-goal export per region, people and era, with salt, fuels, regional foods | v2 | 692, 728, 730, 744, 747, 753, 755, 772, 793, 796, 797, 800, 804, 805, 820, 870 | F, I (domestication), J (resources) | Brief page per culture and place; salt works and mines on the map | `lineages/brief.py`, `salt_reach.py`, `mining.py`: unify the "good" tables |
| I | Domestication, herds and diet | Crops, herds, dairy, ruminant diets and food fit as stocks the brief can read | v2 | 691, 719, 207, 724, 774, 834, 835, 836, 862 | E | Herd and crop ranges on the peoples view; diets differ by species | `vegetation.py` (1.5k) grazing code; `lineages/landuse.py` |
| J | Resources layer | Ores, coal, building stone grounded in the run record, kept honest at the zoom | v2 | 155, 098, 474, 606, 608, 617, 642, 715, 212, 631 | C for iron (817); a run-record spike (608) | Resource overlay that re-sites at fine zoom; a dig-down rock column | `resources.py` (874): split run proxies from zoom siting |
| K | Fine zoom, coast and rivers quality | Fine zooms read as real terrain; coasts and river detail finished | v2 | 516, 485, 486, 487, 511, 523, 530, 532, 541, 542, 544, 539, 097, 094, 502, 503, 619, 621, 641, 716, 717, 403, 404, 411, 413, 420, 433, 370, 391, 394, 419 | D (v1 tail) | Beaches, spits, lagoons, meanders, oxbows; no box cuts | `zoom_fine.py`, `zoom_landforms.py` (2k), `zoom_coast.py`; share edge helpers |
| L | Viewer for peoples and phones | Owner-facing controls for peoples, history zooms, phone width, faster paint | v2 | 483, 651, 671, 672, 673, 674, 679, 685, 687, 795, 624, 518, 400, 401, 399, 410 | E/F for new layers | Make-a-peoples-zoom button; phone-usable globe; smooth repaint | `viewer/` JS and `server.py` (482): page state and layer cache |
| M | Speed, memory, infra | Cut run and zoom cost; fix memory growth, restart and estimates | v2 | 247, 252, 259, 508, 535, 749, 801, 571, 572, 444, 445, 386, 500 | none (parallel lane) | Faster runs; accurate time estimates in the make dialog | `climate._stommel`, `parallel.py`, shared cell-area helpers (444/445) |
| N | Tectonics quality | Fix long-run plate behaviour: rifts, basins, churn, flicker | v2 (late) | 565, 051, 054, 056, 134, 135, 165, 170, 171, 242, 243, 359, 430, 431, 025, 047, 049, 289, 130, 136 | A (shares the carbon source) | Longer supercontinent cycles; fewer pits and closed basins | `tectonics/` modules; `grid.py` resample code |
| O | Base climate (rain, ocean) | Overturning, the sea's air, rain patchiness, regional biases | v2 (late) | 013, 015, 016, 017, 018, 019, 026, 038, 039, 041, 112, 228, 232, 233, 290, 304, 353, 377, 396, 414, 558, 563, 570, 575, 577, 581, 582, 583, 585, 590, 592, 593, 594, 595, 625, 626, 633, 639 | A | Better Nordic winters, Gulf Stream, monsoons; rain with no streaks | `climate.py`, `ocean.py` (1k): split the sea-air carry from the solver |
| P | Ice ages done properly | Run ice as cycle average; time zoom as a window; one ice model | v2 (late) / later | 470 (epic), 555, 462, 464, 465, 467, 469, 513, 526, 556, 461, 459, 460, 030, 104, 241, 295, 398, 422, 427, 434-436, 439, 447, 448, 452, 453, 566-569, 584, 637, 644, 647, 648 plus the later-milestone 470 children | O, A; the holistic review (PW-526 ruling) | Real 100 kyr cycles in the time zoom; embedded ice-age episodes | `icemass.py`, `timezoom/`: share the duplicated ice helpers (PW-445) |
| Q | Other planet kinds | Water, hothouse and orbit presets; extend a run to 4 Gyr | v2 late / v3 | 481, 557, 790, 798, 799, 811, 443, 802 | A, B and the v1 tag | New planet form with orbit, sun, ocean fraction | `make.py` presets |
| R | v3 world extras | Moons and tides, weather generator, whole-world L8/L9, magic, named individuals | v3 | 156, 216, 217, 218, 490, 696, 911, 912 | v2 done | Animated weather; configurable moons; deep zoom of the whole world | Own epics; no checkpoint yet |
| S | Docs and wiki | Human wiki, overview refresh | v2 late | 792, 814, 816 | all | none | docs only |

Not assigned above and fine to leave: the `later`-milestone viewer, store and tide items under PW-649 (quality pass), and the geologic items under done parents (118, 132, 147, 175, 177, 383).

## Close or merge

Stale or superseded:
- PW-735 (one icehouse seed): the 2026-10-20 and 2026-10-25 rulings allow outliers; close as wontdo.
- PW-313 (run ice rule cannot hold Antarctica at dT 0): blocked on PW-015, superseded by the ice redesign; fold into PW-462.
- PW-526 (ice batch fails): a result record; keep as a note under PW-555 and close.
- PW-556, PW-461, PW-513: the coast_loss series PW-526 shows failing; merge into PW-465 (one ticket) under PW-555.
- PW-030 (no real 100-kyr sawtooth): covered by PW-462/469; merge into PW-469.
- PW-810 (thermostat unmeasured): PW-865 now keeps the thermostat off by ruling; close unless the owner wants it measured.
- PW-417 (retire flicker diagnostic URL switches): do it or drop it; tiny and old.
- PW-535 (time estimates scaled): fold into PW-247.

Duplicates:
- PW-658 and PW-659 are the same forest-test eligibility story; merge into one.
- PW-875 and PW-898 are both plume degassing; merge PW-898 into PW-875.
- PW-812, PW-811 and PW-815 are three star-anchor re-measure tickets; keep PW-812 for v1 and move 811 to the water/hothouse group (Q).
- PW-913 (tech tree tab) overlaps PW-675 (tech epic): make 913 a child of 675.
- PW-912 (crops by trade) overlaps PW-744 (cuisine plants are markers only): merge or link.
- PW-661, PW-670, PW-676 overlap the PW-856 civilizations work; make 856 the parent and keep 661 as a v3 remainder.
- PW-413, PW-420, PW-433 (fine-zoom detail, `later`): one ticket per symptom is fine, but link them under PW-516.
- PW-714 and PW-713 (known deposits / found-not-given): one ticket.

## Wrong parent or milestone

Milestone looks wrong:
- PW-692 (culinary epic): v3, but about 40 children are v2 and it is the project's end goal; set to v2.
- PW-744, PW-785, PW-796 (children of 692, v3): they are culinary first-pass items; v2.
- PW-713, PW-714 (v3 under 675): the owner ruled "deposits found, not given" in v2; v2 or later, not v3 with the tech epic unscheduled.
- PW-889 and PW-800 (children of 692, no milestone): set v2.
- PW-900 to PW-910 have no milestone: v2; PW-911, PW-912 should be v3 (their titles say so).
- PW-873, PW-874, PW-896 (unscheduled coupling findings, same audit as 875/880): v1 group A.
- PW-871, PW-878, PW-879, PW-883, PW-884 (zoom/time-zoom findings, unscheduled): v2 group P or K.
- PW-470 children in v2 whose subject is base climate (PW-575 to 595, 625, 626, 633, 639, 558, 563, 611): v2 late, reparent below.
- PW-811, PW-790, PW-798, PW-799 (v2 water/hothouse): the 2026-10-24 scope ruling puts them after the v1 tag; v2 late or later.
- PW-481 (new planet form): v2 under the v1 epic 244.

Parent looks wrong:
- v2 tickets under the v1 epic PW-244: 247, 481, 483, 535, 735, 811 (reparent to group epics, e.g. 247 stands alone, 483 under 103).
- Under PW-470 but not ice: 575, 577, 581, 582, 583, 585, 590, 592-595, 625, 626, 633, 639 (base-climate; reparent to PW-570), and 451, 454, 455, 644, 647, 648 (weathering and vegetation; PW-184 or the climate group).
- Under done parents: 284, 304 (PW-245), 494, 496 (PW-037), 499 (PW-092), 502, 503, 518 (PW-099), 118, 383 (PW-001), 132, 147, 175 (PW-005), 704 (child of 689). Give them a live epic or standalone status.
- PW-207 has no parent; belongs under PW-691. PW-820 belongs under PW-692.
- PW-097, PW-098, PW-094, PW-093, PW-096, PW-101 sit under PW-090 (an unscheduled epic); either schedule PW-090 as v2 or promote the children.
- PW-017, PW-018, PW-019, PW-228 (children of 013, unscheduled): v2 late.
- PW-509, PW-529 (v2) under PW-649 (the `later` quality pass): milestone and parent disagree.

## Suggested order

Serial physics stays one lane; the rest run beside it as the project's lane rules already say.
1. **A then B** (v1 lane): carbon and star balance, then the finish moment. This gates the v1 tag.
2. **C and D** in parallel with A/B (they do not touch the climate): geology tail and zoom tail. Then tag v1 and rebuild showcases (PW-202 done; recheck).
3. **E first step** now, in parallel with A: PW-901 (split `history.py`) is behaviour-neutral and lets F and G start cleanly. Then ice-age ranges (902) and origins (888).
4. **F, then G**: cultures and mixing, then the history zoom and tech tree. These are the civilizations rulings (PW-856, 900-913).
5. **I and J** beside F/G (domestication and resources both feed the brief), then **H** (the culinary brief, the end goal).
6. **L** with each of F/G/H so every new capability has a viewer control (owner uses the viewer, not the CLI); **M** whenever a lane is idle.
7. **K** (fine zoom/coast) as the standing second parallel lane after D; **N** after A.
8. **O and P** late v2, under a holistic review first (the 2026-10-21 ruling); **Q** after the v1 tag; **R** and **S** last.

Refactor checkpoints, in the order they land: `history.py` (before F), `climate.py` split (after A), `zoom.py` / `zoom_fine.py` (after D/K), `brief.py` (after H), `resources.py` (after J), `icemass.py` plus the time zoom (after P).
