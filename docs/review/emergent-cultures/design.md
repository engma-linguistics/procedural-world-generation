# Emergent cultures, first cut (PW-670): design note

Lane 107, 2026-10-31. Code: `planet/lineages/cultures.py`. Screenshot of the Cultures tab on run 622c00: [cultures-tab-622c00.png](cultures-tab-622c00.png).

## In plain words

When part of a people moves into new country and learns to live there, or lives apart from the rest long enough, it
becomes a culture of its own. Each culture starts with what its parent culture had, then drifts toward what its own land
rewards. A seafaring people's inland daughters lose their boats over a thousand years or so. Sister cultures of one people
that border each other can merge again, but only once that people has states able to rule both (cities, then written
law). There is no cap on how many cultures there are. The species tree stays as it is. Cultures get their own tab.

## What a culture is

The unit is the deme (PW-981, `demes.py`): a regional population of one people, with a dated tree of splits. A culture is
a deme, or a run of demes along that tree, that counts as its own culture:

- **Founding culture.** A people's first demes in the window (`first`, or `from_people` for a new kind born of another
  people's deme) are its founding culture. Demes founded in the same frame form one culture. Its parent is the culture of
  the deme it arose from (another people's), if there is one.
- **Adapted.** A deme split off because it learned new country (`split_adapted`, PW-1155: tundra elves, desert aarakocra)
  is a new culture straight away. That split already had to hold for PERSIST frames.
- **Apart long enough.** A deme cut off by a gap, a sea crossing or distance (`split_gap`, `crossing`, `split_distance`)
  is a new culture if it lived apart for at least `T_APART_KYR` = 1 kyr. A deme that fuses back sooner was never a culture
  of its own. Its cells stay with its parent's culture.
  Grounding: in lexicostatistics (Swadesh, Lees 1953; read on Wikipedia's "Glottochronology" page) a 100-word list keeps
  r ≈ 0.86 of its words per millennium (Lees: 0.805 on the 200-word list), so two daughters share about r^(2t). The usual
  line between "dialects of one language" and "separate languages", about 81% shared, is from memory and not re-read here.
  On those numbers the line is crossed after about 0.5–0.7 kyr. 1 kyr (two frames of the recent pass) is a **judgement**
  that leaves some margin. Speech is a proxy for culture here, nothing more.
- Every other child deme belongs to its parent's culture.

A culture is the set of its demes. On the map, a cell belongs to the culture of the deme that leads it (`layers/demes.bin`).
A culture ends when its last deme ends. If that deme died out, the culture died out. If it fused into a deme of another
culture, it merged into that culture.

**Groups (authored ways of life)** such as human seafarers or steppe orcs are not cut into demes: their land is counted in
their people's land. A culture records the group that led most of its cells when it was founded (`founded_by`, from
`groups_best`). So "a culture of an authored group" is a culture of the people whose founders were mostly that group.

## Inheritance

At its first frame a culture copies its parent culture's state at that moment: its way of life (shares of its people's
groups, and the people's own old ways, read from `groups_best`) and its two drifting skills (below). A founding culture
starts from its people's spec. Sea craft starts at the people's `sea_share`. Open-country lore (herding and moving over
steppe, desert and savanna) starts at 1 for a `nomadic` people and 0 otherwise. Body traits (flies, swims, mountain, hardy,
subterranean, denning) are the kind's own and never drift. They are listed as inherited only.

## Drift (PW-670: the inland descendants who "can barely tell a skiff from a canoe")

Each skill moves toward what the culture's country rewards, frame by frame (exact exponential steps):

    v <- fit + (v - fit) * exp(-dt / tau),   tau = TAU_LOSE (1 kyr) if fit < v, else TAU_GAIN (3 kyr)

- Sea craft: fit = min(1, coast share of its cells / `COAST_FULL` 0.25). Coast share means land cells with a sea
  neighbour.
- Open-country lore: fit = min(1, share of its cells in the steppe, desert or savanna classes / `OPEN_FULL` 0.5).
- A skill counts as held at 0.5 or more. It counts as lost if it was held at the founding and is under 0.25 now. It counts
  as gained the other way round.

Grounding (read: Henrich 2004, *American Antiquity* 69:197, full text). The Tasmanians were cut off 10–12 kyr ago. Their
bone tools declined from 8 to 3 kyr ago and then vanished. They gave up fish about 3.8 kyr ago and never took it up again
in four millennia. Henrich, citing Rivers 1912, describes the Torres Islanders: they lost the seaworthy canoes they had
arrived in, though they still lived on islands. The Banks Islanders "gradually" re-acquired canoes, and these were still
cruder than before. So a craft can be lost even where it is useful, and it comes back slowly or not at all.
`TAU_GAIN` > `TAU_LOSE` follows that. The values, 1 kyr to lose (a culture inland for 2 kyr keeps about 14% of its craft)
and 3 kyr to gain, are **judgements**. Tasmania's losses were slower, but Tasmania was a small isolated population. The
coast and open-country scales (0.25, 0.5) are **judgements**. Henrich's main point is that a small pool of learners loses
skills faster. That is not modelled here (follow-up draft).

Way of life drifts on its own in the history: the groups compete for land cell by cell (PW-665, PW-1205). The culture
records its way of life at the founding and now, e.g. "founded by human seafarers, now mostly human farmers".

## Name

The placeholder is "[adaptation] <people> of <place>". For example, "desert dragonborn of the west of Kesh" or "humans of
Tenar". The place is the place of the culture's largest deme (`demes._place`). A founding culture is "first <people> of
<place>". If two names clash, the second gets " (2)". Real names wait for PW-972 and PW-767.

## The counterweight (PW-676): merging, with no cap

1. Deme fusions (demes.py `_fuse`) already merge small touching populations. A culture whose last deme fused into
   another culture's deme ends as "merged into" that culture.
2. Unifying states. Two cultures of one people merge when all of these hold:
   - they share a land border (neighbouring cells on the demes layer);
   - they have the same adaptation and the same main way of life;
   - the people knows a unifying technology (`meta.techtree.known`), whose reach caps the two cultures' combined area:
     `cities` 1 Mkm², `law` (written law) 5 Mkm²;
   - they have been in contact under that reach for `MERGE_KYR` = 1 kyr.

   The older culture keeps its name. The reaches are **judgements**: early states up to about a million km², the largest
   territorial empires a few million (Rome and Han at their height, from memory; Taagepera 1978's table was not read in
   this lane).
   Chiefdoms do not merge cultures. Different peoples never merge here: that is mixing and assimilation (PW-904, PW-906),
   a later step.

## Output side, not in the history

It is built post-run, like demes and settlements. It reads `demes.json`, `layers/demes.bin`, `groups_best`, the terrain
frames and `meta.techtree`, and writes `cultures.json` plus `meta.cultures`. Nothing in the history changes. Why:
- The pieces it needs (demes, learned country, groups, techs) are all post-run already. Building it costs seconds, so it
  can be tuned without re-running histories.
- Lane 101 is editing `planet/lineages/history/`.
- Putting it in the history would mean a culture's skills feed back into the people's fit (a culture that lost its boats
  stops crossing seas). That is the real PW-670 and a v3 system. This cut is the record it will grow from.

## Not in this cut

Cultures of other peoples' minorities (the demes layer keeps only each cell's leading people). Pool-size effects on loss
(Henrich). Merging across peoples. Cultural traits beyond sea craft, open-country lore and way of life (diet, gods,
attitudes). Real names.
