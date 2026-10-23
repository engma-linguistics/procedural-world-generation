# Lineages showcase 4: lingering hybrids, hobgoblins by the orcs, peoples on their land (lane 4, 2026-10-23)

This uses the code at lane 4's head. Each world ran `planet lineages <world> --tree dnd --tries 2`, about 2–3 min a world with 4 in parallel; working out the land's goods takes ~10 s of that. The screenshots show the flat map at the present on the `peoples` layer, with origins and tracks. Lane 3's runs (3cf7fe, 2c70d9, 13cf30, 5cdd4a) were deleted; their screenshots stay in `showcase-3.md`. Design notes: `docs/proposals/lineages.md`, "Lane 4 additions".

| world | run | wish score (lane 3) | hobgoblin near orc (lane 3, recomputed) | goblin near orc | lost (lane 3) | half-elf / half-orc Mkm² (of it their own land) | mixing | screenshot |
|---|---|---|---|---|---|---|---|---|
| 1144ce | 364010 | **0.81** (0.73) | 0.91 (0.50) | 0.12 | none (half-elves) | 0.16 (0.0) / 6.9 (1.6) | 21% | showcase4_1144ce.png |
| 31926a | 4e2000 | **0.70** (0.56) | 0.57 (0.00) | 0.00 | none (none) | 0.19 / 1.8 (0.4) | 15% | showcase4_31926a.png |
| 91448a | 176619 | **0.75** (0.73) | 1.00 (1.00) | 0.00 | none (none) | 10.7 (0.3) / 2.1 (1.1) | 15% | showcase4_91448a.png |
| 3e0b0a | 345bb4 | 0.59 (0.62) | 0.15 (0.78) | 0.00 | half-orcs (half-orcs) | 0.64 (0.1) / — | 10% | showcase4_3e0b0a.png |

Lane 3's scores use the old preset, with "goblin near orc" in place of "hobgoblin near orc". So the "hobgoblin near orc" column recomputes the new wish on lane 3's stored presence.

## Contact hybrids (PW-613)
No contact hybrid that appeared was lost. On 1144ce lane 3 lost the half-elves; here they hold 0.16 Mkm².

Half-orcs live on as a people of their own where humans and orcs no longer meet: 1.6 Mkm² on 1144ce and 1.1 Mkm² on 91448a. There the `peoples` layer shows them as a people, not an overlay.

On 3e0b0a the half-orcs never appeared, because humans and orcs never met in either try. The orcs hold the far south-west (36°S 84°E origin) and the humans stay north of the dragonborn deserts. That is not the loss PW-613 is about. A contact hybrid still waits for its parents to meet, as specified.

## Hobgoblin near orc (PW-614)
The wish is met at 0.91 and 1.00 on 1144ce and 91448a, and at 0.57 on 31926a, against 0.00 there for lane 3's "goblin near orc". The geography lines up: savanna borders steppe.

On 3e0b0a it is 0.15. Lane 3's run on 3e0b0a scored 0.78 for the same pairing with a different try. With 2 tries this is seed luck. Goblins keep the jungle (0.56–0.70).

## Land use and homeland notes
"Enrichment" is a good's mean over a people's land (presence ≥ 25%) against its mean over the world's land:

| people: good | 1144ce | 31926a | 91448a | 3e0b0a | lane 3 (same four worlds) |
|---|---|---|---|---|---|
| dwarves: gold | 2.1 | 1.8 | 2.1 | 2.6 | 2.0, 1.8, 1.8, 1.7 |
| humans: fertile | 1.27 | 1.67 | 1.44 | 1.70 | 1.20, 1.54, 1.29, 1.49 |
| halflings: fertile | 1.64 | 2.18 | 1.40 | 2.38 | 1.51, 1.76, 1.39, 1.32 |
| humans: harbour | 1.29 | 2.87 | 1.30 | 1.39 | 0.98, 2.92, 1.10, 2.57 |
| gnomes: gems | 2.7 | 0.3 | 5.9 | 0 | 1.1, 0.1, 2.0, 1.7 |
| aarakocra: cliff | 5.4 | 81 | 2.3 | 1.8 | 3.6, 0.7, 1.9, 4.8 |
| elves: timber | 3.6 | 0.15 | 1.6 | 1.6 | lost, 1.6, 2.2, 0.8 |

Most move the intended way, some by a lot. The effect is a nudge (pull 0.5; see `draft-lineages-land-pull-strength`). Mountain peoples already sat near ores, because mountains and ores go together. Peoples confined to a few lands (the 31926a elves, the 3e0b0a gnomes) can't pick their goods.

On the four L7 worlds, pasture is ~0 even on the steppes. Their vegetation has no grasses: see inbox `draft-l7-worlds-have-no-grasses`. Orcs have nothing to graze, and the orc steppe wish still holds at 0.5–0.78.

Example homeland notes, from the stories in run.txt and `meta.present.homeland`:
- 1144ce: "The dwarves hold the world's richest mithril and adamant (fantasy) district, in the 2,000 km mountain range at 9°N 39°W; and they work 15 of the world's 389 iron districts (the best in the largest plateau at 7°N 40°W)."
- 1144ce: "The tortles hold three of the world's five richest coral coast districts (…); and they hold 12% of the world's best lagoons behind barrier islands (…)."
- 1144ce: "The aarakocra hold the world's fourth richest seabird cliffs district, in the 2,000 km mountain range at 9°N 39°W."
- 31926a: "The humans hold two of the world's five richest natural harbours districts (the best in the country at 42°N 61°W); and they hold 23% of the world's best farmland (12 Mkm², …)."
- 31926a: "The sea elves hold two of the world's five richest coral coast districts (the best in the country at 7°N 171°W)."
- 1144ce: "The gnomes (from the feywild) hold the world's fourth richest gems district, in the country at 44°S 98°E; and they hold 5% of the world's best timber (…, the heart of it in the wine country at 41°S 89°E)."

The worlds have no place names, so the notes use the nearest highlight feature that covers the place (mountain ranges, plateaus, great forests, wine country), or directions.

## Rough edges
- 3e0b0a has an empty 40 Mkm² continent at 52°N 145°W (PW-603).
- On the L7 worlds, "goblin near orc" (no longer a wish) is 0.0–0.12: goblins live in the jungle, away from the orcs, as intended.
- District counts at L7 can be large ("15 of the world's 389 iron districts"). A district is any connected patch at ≥ 0.5, as in `resources.deposits`.
