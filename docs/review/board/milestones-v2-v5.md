# Milestones v2 to v5, then v1.0 on 1 December

*Lane 162, 2026-11-03. Builds on lane 161's December plan (`december-plan.md`, its workflow table) and lane 156's
triage (`triage-2026-11-03.md`), under Daniel's 11-03 framing: v1.0 on 1 December, v0.x milestones on the way, no
expensive physics in the mainline, states and empires a must. The board moves below are applied (the coordinator
places tickets; every move is one update line on the ticket and can be reversed).*

## In plain words

Four short milestones, one a week, then the release:

| tag | target | what you get |
|---|---|---|
| **v0.2.0** (milestone v2) | Tue 10 Nov | **Write your own faiths, read what a culture cooks, and see dates in years.** |
| **v0.3.0** (v3) | Tue 17 Nov | **States and war, first cut:** who rules where at any year, empires as states that rule several cultures, and invasions you schedule. |
| **v0.4.0** (v4) | Mon 23 Nov | **History that moves:** states fight and change hands inside the history, empires rise and fall, cultures found their own calendars, and every culture, faith, state and place has a name slot for the languages work. |
| **v0.5.0** (v5) | Sat 28 Nov | **Your December world:** pick it from three candidates, refine it from L7 to L8 (owner 11-10), every Seven Meals people right, the food sheet complete. |
| **v1.0.0** | Tue 1 Dec | Freeze, walk the checklist, tag. Seven Meals campaign work starts. |

Everything in the four milestones is non-physics work: viewer, peoples, culture and food. These rebuild in seconds or
minutes, not in day-long simulations, so they don't fight your jobs for the machine.

**Physics goes on a side track** that holds back no tag: up to six tickets, ranked, each a 1-3 pass lane with its own
agent, taking about half the coordinator's attention. D47 (the stability fix you approved) is first. Whatever lands,
lands. Nothing on the side track gates v2-v5 or v1.0.

**Languages** stay in your own worktree. v2 makes culture ids stable so your lects can key on them, and v4 adds the names
slot your names plug into. Until then everything carries plain descriptive glosses.

**Calendars:** v2 gives every readout in "1,400 years ago" form, with an optional "the present is year N" so you can type
"year 1400". v4 adds emergent calendars: a culture that lives through something it treats as important (founding a
faith or a state, an invasion, a flood) may start counting from it. Neighbours may or may not take that calendar up, and
it can die out with the state.

**The board after the moves:** v2 has 12 open tickets, v3 5, v4 6, v5 15, 11 "new" items not yet filed, and the
backlog (`later`) has 523. Counts are at the end.

---

## v2 (tag v0.2.0): faiths you write, a culture's food, dates in years

**Theme:** the two December jobs you can't do today (write in a religion, read what a *culture* cooks), plus years.

**Target:** Tuesday 10 November. **Size:** about 5 agent-days in three parallel lanes.

### Must-haves

| item | tickets | effort | notes |
|---|---|---|---|
| Years everywhere | new: "X years ago" in every readout (brief, workbench, settlements, religion, globe time slider), with an optional "the present is year N" so dates can also be typed and read as years | s | the fallback calendar; the invasions in v3 and the faiths here use it |
| Faiths you write | new: an authored-faith row (name, founding people or culture, place, year, named gods and their domains, spreads or stays closed), fed into the existing faith rules; an editor in the Religion tab; rebuilds in seconds without re-running the peoples. Parent PW-1308 (only this slice) | m-l | lane 161 item 4 |
| Gods mode control | PW-1309 | s | picks faith-made, belief only or absolute in the viewer, saved with the run |
| Dead gods shown as living | PW-1313 | xs | |
| A culture's food sheet | PW-1391 (parent PW-856), PW-728 | m | the brief takes a culture: fuel, staple, drink, who eats together, what outsiders get wrong |
| What a culture won't eat | PW-1312 | m | taboos in the food sheet |
| Visibly wrong dairy | PW-834, PW-793, PW-1372 | s, xs, s | foragers with dairy herds; antelope-kin and cervid-kin milking; humans' lactase |
| Workbench readable | PW-841 | m | tree and timeline overlap, can't scroll sideways (your 10-26 complaint) |
| Stable culture ids | PW-1283 | s | so your language worktree can key lects on culture ids |

**Needs your answer soon:**
- PW-1391 is still marked needs-decision. Your D44 answer ("food first", decisions.md 11-03 19:45) looks like the yes it
  asks for; the coordinator can record that and move it on.
- PW-841 is needs-decision only because the last fix was never confirmed by you in Firefox. The v2 lane re-fixes it and
  you check it once.

### Done when (in the viewer)

1. Religion tab: switch the gods mode. Add "the Forge Faith, founded by the dwarves in the northern hills in year 300,
   gods Mardun of the forge and Esk of the deep roads". Within seconds it is on the faith map, the faith timeline and
   in the dwarves' taboos. No god of a dead culture is shown as living.
2. Globe, Culinary brief: pick a *culture* and a year. The sheet names its fuel, staple, drink, who eats together and
   what outsiders get wrong, and lists what it won't eat. Foragers keep no dairy herds; antelope-kin don't milk.
3. Every date on the brief, the workbench and the religion tab reads in years ago, or in "year N" if you set the present.
4. Workbench, Tree & timeline: no overlapping labels, and you can scroll sideways to the earliest split in Firefox.

### Lane order (three lanes in parallel)

- **Lane A, religion:** years everywhere first (small; merge it the same day so the other lanes rebase onto it), then
  faiths you write with PW-1309 and PW-1313. Files: `viewer/religiontab.js`, `planet/lineages/gods.py`, `taboos.py`,
  `spec.py`; the years pass also touches the readouts in the viewer.
- **Lane B, food:** PW-1391 with PW-1312, then PW-834, PW-793, PW-1372. Files: `planet/lineages/brief.py`, the brief
  panel in `viewer/globe/colours.js`, the food data and `samples/seven_meals.toml` (milking only). Keep out of
  `gods.py`; taboos are read, not changed.
- **Lane C, workbench and ids:** PW-1283 first (cultures and demes code), then PW-841 (`viewer/lineages.html`). Start
  PW-841 after lane A's years pass has merged, since both touch the workbench's era readouts.

A and B share only the years helper; C waits on A for one file. No lane runs a long simulation; peoples runs are minutes.

---

## v3 (tag v0.3.0): states and war, first cut

**Theme:** who rules where, at any year; empires as states that rule more than one culture or people; invasions you
write in.

**Target:** Tuesday 17 November. **Size:** about 7 agent-days, three lanes.

### Must-haves

| item | tickets | effort | notes |
|---|---|---|---|
| Civilization epic (parent) | PW-661 | - | |
| Pull the stand-in war and state formulas behind one seam | PW-1280 | s | no change to results; polities swap in through it |
| Village experiment | PW-1281 | s | the polities proposal runs it before polities read the settlement ledger |
| Polities v0 | new: chiefdoms, states and empires from the settlement ledger, technology and hemmed-in land (proposal round 2 section 3.3, `docs/review/cultures-proposal/proposal-r2.md`); reach by travel time; one map per century step; dragon realms; a "Polities" globe layer with the time slider and a state card (ruler culture, subjects, founded, fell) | l | read after the run, so a rebuild is cheap |
| War v0 | new: war as a change of owner between neighbouring states (proposal 3.3: armies break, the cells change hands, farmers keep farming) | m | read after the run; deaths and refugees come in v4 |
| Invasions you schedule | new: an invasion row (who, whom, year, how long, from where, light or strong) that nudges the history in that window and place, an editor in the workbench, and an "it happened / it didn't" read-out from the existing incursion detector (`planet/lineages/contacts.py`); builds on PW-756 | l | lane 161 item 5; the sim decides how far it gets |
| Seven Meals empires | PW-785 | m-l | the antelope-kin empire today and the fallen cervid-kin empire; emergent if they come, back-filled as polity anchors if not |

### Done when (in the viewer)

1. Globe, Polities layer at year 1000 and at the present: states and empires drawn with borders; scrub the time slider
   and watch them change. Click one: its ruling culture, its subject peoples, when it was founded and when it fell.
2. On a Seven Meals world, an antelope-kin empire stands at the present and a cervid-kin empire lies fallen.
3. Workbench: add "antelope-kin invade the humans around year 1400, from their border, strong". Run. Results say whether
   it happened, where, and how much land changed hands; the Polities layer at 1400 and 1600 shows it.
4. Re-run with one wish weight changed: the states are recognisably the same.

### Lane order

- **Lane A (Opus), polities:** PW-1280 and PW-1281 (one day), then polities v0, then war v0.
- **Lane B, invasions:** PW-756 and the invasion row, editor and read-out. It touches the history's competition step
  (`history/competition.py`); lane A is read-after-the-run only, so they don't collide.
- **Lane C, Seven Meals empires:** PW-785, after polities v0 has a first merge.

---

## v4 (tag v0.4.0): history that moves, calendars, names

**Theme:** states inside the history (they win and lose land while the run goes, not only in a read-out after it);
empires that rise, merge cultures and fall; calendars that cultures found; a names slot.

**Target:** Monday 23 November. **Size:** about 7-8 agent-days; the riskiest milestone.

### Must-haves

| item | tickets | effort | notes |
|---|---|---|---|
| Polities in the history | new: polities v1, the v0 rules run inside the history behind PW-1280's seam; the loser's people fare by the winner's tolerance (kept, expelled, thinned) | l | proposal 3.3, "War is mostly a change of owner" |
| War's toll on land | PW-1172, PW-1243 | l, m | war empties land where peoples are crowded, stateless or ringed by enemies; one dial per era |
| Brake on fast breeders | PW-1169 | xs | **needs your answer before v4 starts**: land, not deaths, holds the fast breeders down |
| Empires merge cultures | PW-676 | l | the counterweight to cultures fracturing |
| Sacked and walled towns | PW-1108 | l | war as a cause of a site's fall; ruins for the campaign |
| Calendars cultures found | new: a culture that lives through a notable event (a faith or state founded, an invasion, a great flood) may start a count from it ("year 212 of the Forge"); the calendar spreads with the state or faith and can fade; any readout can show a date in a chosen culture's calendar, "X years ago" stays the default | m | |
| Names slot | new: every culture, faith, state and place carries a name field the brief and viewer read; your language worktree fills it when it lands | s | |
| Gloss names until then | PW-1249 | s | today's culture names repeat ("temperate humans of the south of Gugiki (7)") |

**If v4 runs long:** the core is polities in the history, the calendars and the names slot. PW-676 and PW-1108 go to
`later` first.

### Done when (in the viewer)

1. Run Seven Meals: on the Polities layer states grow, fight and fall over the last few thousand years, and the
   antelope-kin empire's land history shows its conquests.
2. A state's card says which peoples it kept, expelled or thinned when it took land.
3. A culture's card lists its calendar(s), if it founded one, and the event behind each; set the brief to "that
   culture's calendar" and its dates change; set it back to "years ago".
4. Cultures have distinct names (glosses, or your languages' names if they have landed); no "(7)".
5. The nudge test from v3 still holds.

### Lane order

- **Lane A (Opus):** PW-1169 answered, then polities v1 with PW-1172 and PW-1243 (the history's counter-pressure code).
- **Lane B:** calendars, names slot and PW-1249 (read-out side, no history code).
- **Lane C:** PW-1108, then PW-676 after lane A has merged (both touch the history).

---

## v5 (tag v0.5.0): your December world

**Theme:** the world you will run the campaign on, refined to L9, with every Seven Meals people and the food sheet right.

**Target:** Saturday 28 November (Thanksgiving is Thursday 26). **Size:** about 6 agent-days, plus overnight compute.

### Must-haves

| item | tickets | effort | notes |
|---|---|---|---|
| Three candidate worlds | new: three L7 Earth-like Seven Meals planets made overnight; you pick one | s + overnight | ~1 h each at L7 (lane 161) |
| Refine from the viewer | new: a "Refine to L8 / L9" control on a finished world (`planet refine` exists on the command line only) | s-m | L9 took 38 min and 39 GB (PW-1262): run it overnight |
| L9 opens at all | PW-1209 | m | today's JSON format can't hold an L9 world in the browser |
| Peoples on the refined world | PW-1265 | m | |
| Refined lakes | PW-1263 | s | 6x the source's lakes at L8; check which are real |
| Landform terrain at L9 | PW-1264 | l (or none) | **needs your answer**: options A-C on the ticket |
| Water thresholds in real units | PW-820 | m | fish runs, salt and lake fisheries are in cell units, wrong on a refined world |
| Every Seven Meals people right | PW-1257, PW-1184, PW-888, PW-758, PW-1400 | ~2 days | half-orcs founded, splits near parents, origins across continents, half-elves as a contact hybrid, rungs in order |
| Food sheet complete | PW-835, PW-905 | m, m | the missing herd animals; food fit per species |
| Seven Meals preset and canon | PW-730, PW-755, parent PW-692 | xs-s | re-read the canon disagreements on your world |

### Done when (in the viewer)

1. Three candidate worlds sit on the start screen; you picked one.
2. On it you pressed "Refine to L9"; next morning the L9 world opens on the globe, with peoples on it.
3. Workbench Results lists every Seven Meals people as living, near its parents (half-orcs included; half-elves where
   elves and humans meet).
4. A culture's food sheet names its herd animals (pigs, reindeer, camels, llamas, buffalo, yak where they belong).

### Lane order

Lane A: the refine chain (PW-1209, the viewer control, PW-1263, PW-1265, PW-1264 per your answer). Lane B: the Seven
Meals peoples fixes (peoples code). Lane C: PW-820, PW-835, PW-905 (food). The candidate worlds run overnight early in
the week so the refine has a world to work on.

---

## v1.0 (tag v1.0.0): 1 December

**Theme:** freeze and walk. Nothing new starts after Saturday 28 November.

- new: an agent walks the v2-v5 "done when" lists headless on your chosen world, then you walk them.
- Bug fixes only, and only for something that breaks a "done when" line.
- Tag v1.0.0. The Seven Meals campaign starts on that world.
- Anything found in the walk that breaks nothing goes to `later`.

---

## Physics side track (no milestone, gates no tag)

**How the board marks it:** side-track tickets sit in `later`, each with the update line "Milestones 11-03: ... physics
side track, ranked N; gates no tag". Find them with `grep -l "physics side track" issue-tracking/tickets/*`. A ticket that
lands simply closes; one that fails three times in a row goes to the back, as before.

Each is meant as a 1-3 pass lane with its own agent, using the diagnosis-first and small-screens routine. Daytime
compute stays under half the machine while your jobs run.

| rank | what | tickets | why this rank |
|---|---|---|---|
| 1 | **D47, planet stability**: one carbon-cycle yardstick per grid level; "frozen over" means it ends frozen, not that its worst moment crossed 40% | PW-1424, PW-1425, PW-1404 folded in | you approved it; "not prone to exploding when nudged"; lane 160 is checking it |
| 2 | **Mountains too low**: tallest peak 5.7 km, few Himalaya- or Andes-scale ranges | PW-846 | visible on every campaign map; no failed attempts yet, only a first look (no clamp found; peaks reach 5-8.5 km per frame on run 6b48f5) |
| 3 | **Wet forest and grass growth**: wet tropical forest grows ~0.55x measured; the wild herds 2-3x thinner than Africa's | PW-1331, PW-1261, PW-1332 | feeds the herd and dragon numbers in the food sheet; PW-1261 has one strike (lane 140) and PW-1332 waits on D47's weathering change |
| 4 | **Hot low-latitude summers**: warmest month 3-4 C above Earth's | PW-1279 | PW-1325, PW-1326 and PW-1327 (its causes found by lane 121) are done; first pass is a re-measure, which may close it |
| 5 | **Rain inland**: interiors like the Great Plains about 1.7x too wet | PW-1363, PW-015 | most likely to put wrong crops in the food sheet, but three strikes (five failed arms) sent it to the back; only with the plan written on PW-1363 (where the vapour rains) |
| 6 | **Warm finishes and frozen spells**: some worlds end +3.5 to +5.3 C; CO2 can't pile up under the ice | PW-1161, PW-558, PW-1156 | re-check after D47, which may settle them |

Other physics that was in v2 (the star-anchor chain PW-807, 809, 812, 815; the star thermostat PW-791, 865 and the plan
PW-570; the ice-age v2 plan PW-555; PW-212, 836, 894, 1120, 1170, 1329) went to `later` without a rank. A physics lane
that finishes its pick early takes the next rank, not one of these.

---

## Backlog stays backlog

The backlog (`later`) now holds **523** open tickets: climate 98, peoples 95, time zoom 49, zoom 46, viewer 42, culture
33, tectonics 29, food 25, surface 19, ocean 19, highlights 18, infra 14, docs 14, coast 12, store 6, hydrology 4. It
includes what v3 and v4 used to mean: weather, moons, weird worlds, planet settings, the tech-tree epic, magic, named
individuals, export targets, the whole-planet land zoom and the walkable setting. None of it is promised before 1
December. The 136 unscheduled tickets stay unscheduled and count as backlog. In November every new draft is `later`
unless it breaks a "done when" line above.

## Counts and moves

| milestone | open before | open after |
|---|---|---|
| v2 | 90 | 12 |
| v3 | 25 | 5 |
| v4 | 1 | 6 |
| v5 | - | 15 |
| later | 444 | 523 (13 of them ranked on the physics side track) |
| unscheduled | 137 | 136 |

123 tickets got one "Milestones 11-03" update line each (two side-track tickets, PW-1363 and PW-015, were already in
`later` and only got the rank). No status changed. In-progress tickets moved milestone only.

- **Into v2:** PW-1308, PW-1309, PW-1313, PW-1283. **Stayed in v2:** PW-728, PW-793, PW-834, PW-841, PW-856, PW-1312,
  PW-1372, PW-1391.
- **v3:** PW-661 stayed; PW-756 from v2; PW-1280, PW-1281, PW-785 from later.
- **v4:** PW-676 from v3; PW-1169 from v2; PW-1172, PW-1243, PW-1108 from later; PW-1249 from unscheduled.
- **v5:** PW-692, 730, 755, 758, 820, 835, 888, 905, 1184, 1257, 1264, 1400 from v2; PW-1209, 1263, 1265 from later.
- **Everything else open in v2, v3 and v4 went to `later`**, each with its reason on the ticket.

**Must-have tickets waiting on Daniel:** PW-1391 and PW-841 (v2, see above), PW-1169 (v4), PW-1264 (v5).

**New items listed above but not filed** (the coordinator files them when a lane starts): years everywhere, faiths you
write (v2); polities v0, war v0, invasions you schedule (v3); polities in the history, calendars cultures found, names
slot (v4); three candidate worlds, refine from the viewer (v5); the checklist walk (v1.0).

## v1.0 milestone (owner 2026-11-10)
`milestone: v1.0` holds everything required for the v1.0.0 tag that has no earlier milestone of its own. Tags may run v0.6.0 … v0.10.0 before v1.0.0; new milestones are cut out of v1.0 as it is groomed. Required so far:
- the L7 → L8 refine with the split history (PW-1265, done);
- the glacial time zoom at 2 Myr instead of 1 Myr (PW-1661);
- level-of-detail zooming: from the globe into a ~4,000 km section, then down to the finest zooms (PW-1198, PW-1299, PW-1296).
