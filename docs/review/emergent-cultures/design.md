# Emergent cultures (PW-670): design note

Lane 107 (first cut) and lane 108 (round 2), 2026-10-31. Code: `planet/lineages/cultures.py`, with the reach by kind in
`planet/lineages/demes.py`. Report: [report.md](report.md). Screenshot of the Cultures tab (round 1) on run 622c00:
[cultures-tab-622c00.png](cultures-tab-622c00.png).

## In plain words

When part of a people moves into new country and learns to live there, or lives out of reach of the rest long enough, it
becomes a culture of its own. "Out of reach" is measured by the kind's own legs: a walker's, a sailor's craft, a dragon's
wings. "Long enough" is 600 years in the stone age, down to 150 years by the renaissance. Each culture starts with what its
parent culture had, then drifts toward what its own land rewards. A seafaring people's inland daughters lose their boats
over a thousand years or so. Some kinds hold together across distance: dragons strongly (one tongue, shared mores per
colour), giants somewhat (a council that meets, then everyone goes home). Sister cultures of one people that live side by
side merge again after about a thousand years, sooner for a cohesive kind, or once a state can hold them both. There is no
cap on how many cultures there are. Cultures get their own tab.

## What a culture is

The unit is the deme (PW-981, `demes.py`): a regional population of one people, with a dated tree of splits. A culture is
a deme, or a run of demes along that tree, that counts as its own culture:

- **Founding culture.** A people's first demes in the window (`first`, or `from_people` for a new kind born of another
  people's deme) are its founding culture. Demes founded in the same frame form one culture. Its parent is the culture of
  the deme it arose from (another people's), if there is one.
- **Adapted.** A deme split off because it learned new country (`split_adapted`, PW-1155: tundra elves, desert aarakocra)
  is a new culture straight away. That split already had to hold for PERSIST frames.
- **Apart long enough.** A deme cut off by a gap, a sea crossing or distance (`split_gap`, `crossing`, `split_distance`)
  is a new culture if it lived apart for at least `t_apart` (below). A deme that fuses back sooner was never a culture of
  its own. Its cells stay with its parent's culture.
- Every other child deme belongs to its parent's culture.

A culture is the set of its demes. On the map, a cell belongs to the culture of the deme that leads it (`layers/demes.bin`).
A culture ends when its last deme ends. If that deme died out, the culture died out. If it fused into a deme of another
culture, it merged into that culture.

**Groups (authored ways of life)** such as human seafarers or steppe orcs are not cut into demes: their land is counted in
their people's land. A culture records the group that led most of its cells when it was founded (`founded_by`, from
`groups_best`).

## Reach: who is apart (round 2, in `demes.py`)

Daniel (2026-10-31): a culture holds together over the distance its members can meet and mate, and that is what the demes
already are. So the reach scaling lives in the demes, and `cultures.py` has no distance logic of its own. Before round 2
the demes used one set of thresholds and land travel costs for every people, so the dragons were cut by sea and terrain
they fly over.

- **Walkers** keep the thresholds as they were (sea gaps up to `SEA_KM` 150 km and necks of others' land up to `NECK_KM`
  120 km crossed as one population; `SPLIT_KM` 7,000 and `FUSE_KM` 4,000 easy km). These are a walker's: it moves
  `JUMP_KM` 800 km per jump in the history (`history/params.py`).
- **Megafauna kinds** (dragons and giants) move `LINK_KM` 1,500 km, over land and sea alike (`history/megafauna.link_km`:
  dragons fly, giants roam and wade straits, PW-936). **Fliers** (aarakocra) move `spec.HOPS['flies']` 700 km. For both,
  terrain costs nothing (1 easy km per km, land or sea). Sea and neck gaps up to that reach are crossed as one population.
  `SPLIT_KM` and `FUSE_KM` are scaled by reach / `JUMP_KM` (dragons and giants x1.875).
- **Seafarers.** A people with sea craft at the time (`animal_defs.craft_for_people`: canoes 300 km from 60 kyr ago,
  planked boats 1,500 km from 6 kyr ago, sailing ships 2,500 km from 3 kyr ago) crosses sea gaps up to the craft's reach x
  min(1, sea share / `BOATS_FULL` 0.6), at least `SEA_KM`. Its sea costs what a coast costs (1, not `SEA_COST` 2).
  Scaling the reach by the sea share is a **judgement**: a people that rarely puts to sea is not kept in touch by its craft.
- **Sea peoples** (marine realm) are as before: their own sea costs 1.

The megafauna flag comes from the stored tree (`meta.tree`, with spec's inheritance).

## Time apart, by era (`t_apart`)

| era (the people's, when it split) | stone age | bronze age | classical | medieval | renaissance |
|---|---|---|---|---|---|
| `T_APART_KYR` | 0.6 | 0.45 | 0.3 | 0.2 | 0.15 |

A people's era at a time is the latest era of which it knows `ERA_SHARE` (a quarter) of the techs (`meta.techtree`, each tech
has an era). The stone age holds from the start.

Grounding. All read this round through web fetches (Wikipedia pages unless noted; a fetch returns a summary of the page):
- **Renaissance end (150 years).** Settler colonies were told apart within 120–175 years. Afrikaans: "Eastern Border
  Afrikaans developed around 1775 into a stable and comparatively homogeneous Dutch dialect form", 123 years after the 1652
  Cape settlement; the earliest imitation of the colonists' speech is 1795 (*History of Afrikaans*). American English:
  descriptions of a distinct, fairly uniform American speech "became common after the mid-18th century", about 150 years
  after the first settlers (*American English*); Witherspoon coined "Americanism" in 1781, 174 years after Jamestown (seen
  only on secondary pages, not verified). Quebec: "with the onset of British rule in 1760, the French of Canada became isolated
  from that of Europe", 152 years after 1608 (*Quebec French*). New Zealand English formed faster, "focused around 1900"
  from settlement in the 1840s (LINGUIST List review of Trudgill 2004), but that was a new mixed dialect, not a split.
  Daniel's own judgement was that 250 years "feels too long".
- **Stone age end (600 years).** Lexicostatistics (Swadesh, Lees 1953; Wikipedia's *Glottochronology*, read in round 1)
  puts two daughters' speech at separate languages after about 0.5–0.7 kyr.
- **The premise that it shortens with tech (Daniel: "possibly incorrectly").** Partly right, read this round:
  - *Material culture: supported.* Bigger, better-connected populations keep and build more skills (Henrich 2004; Kline &
    Boyd 2010, Proc R Soc B 277:2559, Oceanic toolkits grow with population; Powell, Shennan & Thomas 2009, Science 324:1298,
    demography sustains complexity). The deep past was slow: "over one million years of 'stagnation' of the Acheulean handaxe"
    (Finkel & Barkai 2018, Proc Prehist Soc, abstract). Kline & Boyd and Powell et al. were read as abstracts and snippets only.
  - *Language: not supported.* Basic vocabulary changes at a roughly steady rate that varies by word and lineage, not by era.
    Greenhill et al. 2017 (PNAS 114:E8822, read) reject a strict clock but find no era trend. Bromham et al. 2015 (PNAS
    112:2097, read) find population size changes gains and losses but not the net rate. Atkinson et al. 2008 (Science 319:588,
    snippet only) find bursts of change at splits, which speeds up divergence just after a split in any era.
  - So the stone-age value rests on speech, which does not speed up, and the renaissance value rests on colonies being *told
    apart* (a name, an identity, a noticed dialect) in literate, connected societies. The values in between are a
    **judgement**. The drift rates (below) are not scaled by era: their grounding (Tasmania, the Torres and Banks Islands) is
    already stone age, and no source read gives a faster loss in later eras.
- **Frame resolution.** The frames are 0.5 kyr apart near the present and 4 kyr in the glacial pass, coarser than every
  value above. A deme's life is measured between frames, so in practice a split counts once it spans one frame gap (two in
  the stone age near the present; one in the glacial pass at any era). Gap splits also need PERSIST frames in the demes
  first, so for them the time apart is already met; it decides only crossings and distance buds that fuse back quickly.

## Cohesion: a kind's normalizing pull

Daniel (2026-10-31): for dragons, "a very diffuse population is figuring out some sort of way to meet and mate ... If
draconic is a single language ... then something needs to be a normalizing force for them"; for giants, "almost like
United Nations of giants ... but that they all just go back to their own lands and concerns", allowing distinct cultures.

`cohesion` (0..1) is a per-line key in the tree, inherited down it (spec's rule: a line inherits what it leaves out from its
first parent). Defaults, both **judgements**, in `samples/dnd.toml` and `samples/seven_meals.toml`: `chromatic_dragon` and
`metallic_dragon` 0.9 (so every dragon kind; not `draconic`, so dragonborn and kobolds stay at 0), `true_giant` (dnd) and
`giant` (Seven Meals) 0.5. Everyone else 0. It does three things, none of them states:

1. **Drift pull.** Each frame, a culture's target for sea craft and open-country lore is `(1 - c) x its own country's fit +
   c x its kind's mean` (the cells-weighted mean over the kind's living cultures). A dragon culture drifts a tenth as far
   from its kind as a people's would.
2. **Re-merging on contact.** Sister cultures side by side merge after `MERGE_CONTACT_KYR x (1 - c)`: 0.1 kyr for dragons,
   0.5 kyr for giants, 1 kyr for peoples.
3. **One record across gaps in sight.** The frames keep only each cell's two leading peoples, and dragons and giants rarely
   lead a cell, so their pockets drop out of the frames and come back as new "first" demes (one red dragon kind had 64 of
   them). For a cohesive kind those are the same folk, and they rejoin its first culture. (Removed by lane 109: the frames
   now store every people's presence, so the pockets no longer drop out; PW-1259.
   With the full record a dragon kind comes out as one to
   five living cultures, split by gaps wider than its reach.)

With these, each dragon kind comes out as one culture without a special case (the round 1 `one_culture` hard-code is gone).
A kind can still split when it is truly cut off beyond its reach: on cc22df the green dragons have three cultures apart
that died out, and the white dragons two. The giants keep distinct cultures where seas part them: six living storm-giant
cultures on each run, on four landmasses. Honestly, the reach scaling in the demes does little for the dragons' count on these
runs: the third point does most of it. The reach scaling matters for the giants (storm giants 19 demes before, 9 now).

A run made before the key existed (cc22df, 622c00) reads the cohesion of the preset with the same tree name.

## Inheritance

At its first frame a culture copies its parent culture's state at that moment: its way of life (shares of its people's
groups, and the people's own old ways, read from `groups_best`) and its two drifting skills (below). A founding culture
starts from its people's spec. Sea craft starts at the people's `sea_share`. Open-country lore (herding and moving over
steppe, desert and savanna) starts at 1 for a `nomadic` people and 0 otherwise. Body traits (flies, swims, mountain, hardy,
subterranean, denning) are the kind's own and never drift.

## Drift (PW-670: the inland descendants who "can barely tell a skiff from a canoe")

Each skill moves toward what the culture's country rewards (pulled toward its kind by cohesion), frame by frame:

    v <- fit + (v - fit) * exp(-dt / tau),   tau = TAU_LOSE (1 kyr) if fit < v, else TAU_GAIN (3 kyr)

- Sea craft: fit = min(1, coast share of its cells / `COAST_FULL` 0.25).
- Open-country lore: fit = min(1, share of its cells in the steppe, desert or savanna classes / `OPEN_FULL` 0.5).
- A skill counts as held at 0.5 or more, lost if it was held at the founding and is under 0.25 now, gained the other way.
- A skill is gained only once the people knows its technology (boats; herding).

Grounding (read in round 1: Henrich 2004, *American Antiquity* 69:197, full text). The Tasmanians were cut off 10–12 kyr ago.
Their bone tools declined from 8 to 3 kyr ago and then vanished. Henrich, citing Rivers 1912, describes the Torres Islanders
losing their seaworthy canoes though still on islands; the Banks Islanders "gradually" re-acquired cruder ones. So a craft is
lost faster than it is gained. The values (1 kyr, 3 kyr) and the coast and open scales are **judgements**. Henrich's
pool-size effect is not modelled.

## Name

The placeholder is "[adaptation] <people> of <place>", e.g. "desert dragonborn of the west of Kesh"; a founding culture is
"first <people> of <place>"; a clash gets " (2)". Real names wait for PW-972 and PW-767.

## The counterweight (PW-676): merging, with no cap

1. Deme fusions (demes.py `_fuse`) merge small touching populations. A culture whose last deme fused into another culture's
   deme ends as "merged into" that culture.
2. **Side by side** (round 2). Two touching sister cultures (one people, the same adaptation, the same main way of life)
   merge after `MERGE_CONTACT_KYR` = 1 kyr of touching, x (1 - cohesion). 1 kyr is a **judgement**: longer than any time
   apart, so a brief meeting does not undo a split. A new mixed dialect forms within a child generation or three when people
   live together (Kerswill & Williams 2000, *Language in Society*, abstract: "substantial but not complete focusing occurs in
   the child generation"), but neighbouring cultures that keep their own lands converge more slowly than a mixed town.
3. **Unifying states.** Two touching sister cultures merge once the people knows a unifying technology whose reach caps their
   combined area (`cities` 1 Mkm², `law` 5 Mkm²), after `MERGE_KYR` = 1 kyr of touching. The reaches are **judgements**.

The older culture keeps its name. Different peoples never merge here: that is mixing and assimilation (PW-904, PW-906).

## Output side, not in the history

Built post-run, like demes and settlements, in about 2 seconds (14 s with `--redemes`, which cuts the demes afresh in
memory). Nothing in the history changes. Settlements do not read the demes (only two naming helpers), so the demes change
leaves them as they were.

## Not in this cut

Cultures of other peoples' minorities (the demes layer keeps only each cell's leading people). Pool-size effects on loss
(Henrich). Merging across peoples. Cultural traits beyond sea craft, open-country lore and way of life. Real names. Drift
rates by era.
