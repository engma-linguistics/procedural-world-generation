# Emergent cultures (PW-670): report

Lane 107 (first cut) and lane 108 (round 2), 2026-10-31. Written by the coordinator from the lanes' text (they could not write
report files). Design: [design.md](design.md). Code: `planet/lineages/cultures.py`, and the reach by kind in
`planet/lineages/demes.py`. Tests: `tests/test_cultures.py`, `tests/test_demes.py`.

## In plain words (round 2)

- **The time apart is shorter, and it depends on the era.** A part of a people cut off from the rest becomes its own culture
  after 600 years in the stone age, falling to 150 years by the renaissance. It was 1,000 years for everyone. The 150 years
  comes from settler colonies: Cape Dutch, American English and Quebec French were each told apart within 120 to 175 years.
- **Daniel's premise about eras is partly right.** Tools and crafts changed much more slowly in the deep past, and faster in
  bigger, better-connected populations (Henrich 2004; Kline & Boyd 2010; Powell et al. 2009; the handaxe barely changed for a
  million years). Speech is different: basic vocabulary changes at a roughly steady rate in any era (Greenhill 2017; Bromham
  2015), with bursts right after a split (Atkinson 2008). Several were seen only as abstracts. So the stone-age figure is set
  by speech, the renaissance figure by when colonies were seen as distinct, and the steps between are a judgement.
- **Apart means out of the kind's own reach, and the demes measure it** (Daniel: demes already are "the folk who can meet and
  mate"). Walkers are as before. Seafarers cross wider seas with their boats (canoes 300 km, sailing ships 2,500 km, times
  their sea share). Dragons and giants cross 1,500 km of land or sea whatever the terrain; aarakocra 700 km.
- **Each kind has a cohesion setting in the tree: dragons 0.9, giants 0.5, everyone else 0.** It pulls a culture's drift
  toward its kind's average, lets sister cultures that live side by side merge sooner, and rejoins a kind's scattered pockets
  to its first culture when they reappear in the record. With it each dragon kind comes out as one culture without a special
  rule. To be plain: that rests mostly on the rejoin rule, because the record keeps only each cell's two leading peoples.
- **The giants keep their cultures:** six storm-giant cultures alive on each run, on four landmasses.
- **The count went down, not up.** Sister cultures of any people that live side by side for 1,000 years now merge, without a
  state. That outweighs the shorter time apart.

## Runs (read only; `planet cultures RUN --out DIR --redemes`)

| run | round 1: cultures / alive | round 2: cultures / alive | merged (side by side, under a state) | demes before → now |
|---|---|---|---|---|
| cc22df | 367 / 156 | 336 / 130 | 122 (114, 8) | 706 → 662 |
| 622c00 | 362 / 133 | 331 / 111 | 141 (131, 10) | 702 → 646 |

Round 1's totals left out the dragon kinds; round 2's include them. Living per people (cc22df / 622c00; round 1 in brackets):
humans 32 / 28 (36–40); kobolds 24 / 22 (26–30); dragonborn 14 / 8 (11–22); kenku 12 / 9 (12–15); storm giants 6 / 6 (13);
each dragon kind 1; frost, fire, cloud and hill giants 1–2 each; most other peoples 1–3.

## Examples (622c00 unless noted)

- **The skiff-and-canoe case still holds.** "temperate humans of Drama (2)" moved inland 17 kyr ago and lost the sea craft of
  its founders (1.00 → 0.00). It then merged side by side into its sister cultures 3 kyr ago.
- **Merged side by side.** "elves of the east of Tholosas" merged into "first elves of Tholosas" after 1 kyr. Two storm-giant
  cultures merged after only 0.5 kyr: the giants' cohesion halves the time.
- **Merged under a state.** "temperate humans of the west of Rilun" merged into "temperate humans of Rilun" (1.84 Mkm²).
- **The giants keep cultures.** Storm giants live on Tholosas, Tenar, Gugiki and Drama, each apart for 280–296 kyr. "frost
  giants of the south of Tholosas" lost the sea craft of its founders (0.70 → 0.00).
- **Dragons.** On cc22df every dragon kind has one living culture. The green dragons had three cultures cut off beyond
  1,500 km that died out. The red dragons used to churn through 64 short-lived cultures; now they are one.

## Round 1 (lane 107), for the record

A part of a people became its own culture when it learned new country (niche learning's `split_adapted`) or after 1 kyr cut
off. Each culture starts with its parent's skills and drifts with its land: sea craft follows the coast share, herding lore
the open dry country; a skill fades over about 1 kyr and is gained over about 3 kyr (Henrich 2004; Rivers 1912 via Henrich).
Sister cultures merged under cities (1 Mkm²) or written law (5 Mkm²); those sizes are judgements.

## Daniel's runs and settlements

The viewer works cultures out from each run's stored demes. Settlements do not read the demes, so they are unchanged.

## Known limits

- The time apart is shorter than the frame gap (0.5 kyr near the present), so a split counts once it spans one frame gap.
- Drift rates are not scaled by era. Merging side by side needs only a shared border, however short.
- The record keeps only each cell's two leading peoples, so dragons, giants and third peoples are underseen. The plan for
  overlapping demes (a sparse per-people presence table per frame) is an inbox ticket.
- Names are placeholders, and different peoples never merge.
