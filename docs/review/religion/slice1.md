# Religion, first slice (lane 117): faith techs, the god tree, food taboos

Tickets: PW-1304 (faith tech nodes), PW-1306 (god tree + individuation, folds in PW-907), PW-1305 (food taboos), under epic PW-1308.
PW-1307 (moral ledgers) is not started: it waits on Daniel. All of this is a readout: it is computed after a peoples run from what the
run stores and never changes a history.

## In plain words: what a reader sees

Run b4d502 (a dnd peoples run, level 7, read only; outputs went to a scratch copy, nothing was written into the run).

**Faith steps.** The tech tree has two new nodes. "A moralizing high god" sits on the social track behind temples + kingship. "Divine magic"
(clerics) sits on the arcane track behind temples, and exists only when the world's gods mode is `faith_made` (the default) or `absolute`,
never `belief_only`. In b4d502, rebuilt in memory: 21 of 66 peoples (lines and groups) got the high god, between 1.75 kyr ago (humans, who
invented it) and 0.05 kyr (orcs); the rest never did. At the first setting (rate 0.4, spread 1) all 38 peoples with kingship had it within
1 kyr: one invention swept every neighbour. That is a law, not a hazard, so the rate was cut to 0.08 and the spread to 0.3.

**Gods.** Every culture whose people has learned spirit ritual has 3 to 15 beings, each with a mix of domains (sea, river, rain, flood, sky,
sun, storm, mountain, fire, forest, desert, herd, hunt, harvest, fertility, hearth, smithing, death, war, ancestors) and an individuation from
0 (a spirit bound to one feature) to 1 (a person-god). In b4d502: about 4,500 beings were ever made and about 1,800 are alive now. Examples:

- *First humans of the west of Talatos* (a farming and herding culture, kingship and temples): "god of sky and storm" (individuation 0.61, grants
  spells), "power of forest and fire" (0.47), "power of harvest and herd" (0.47), "power of sea and rain" (0.47), then three later powers born
  as the land and the craft changed: "hearth and death" (0.40), "flood and sea" (0.39), "smithing" (0.34, born 3.5 kyr ago when bronze came).
  The four oldest each stand for a dozen-odd beings of its daughter cultures that merged back into it (syncretism).
- *Tortles of the south-west of Ratukham*: "god of sea and rain" (individuation 0.52, grants spells), powers of sky and storm, of forest and
  fire, and of hunt and fertility (0.48), and two later ones for smithing and for death (0.34). Each is a cousin of the same being in the sister
  tortle cultures of Talatos: copied when the cultures split, drifting apart since (the Talatos forest power is 0.63 forest, here 0.53).
- *Black dragons of Razukum*: spirits of the great river, the forest, the hunt and the storm, bound to Razukum (individuation 0.2: the dragon peoples know
  burial but no temples or kingship in this run). Dragon peoples learned ritual early (white dragons 750 kyr ago, tortles and lizardfolk ~910 kyr), but this
  readout starts at the window's start (300 kyr ago), so "the oldest gods" cannot yet be told apart; each culture's `ritual_since_kyr` is in
  the file for when it is.
- The largest family: a spirit of the fire mountain from the first window frame has 228 descendants in 211 cultures, now mostly forest, fire
  and mountain powers.

**Food taboos.** Every living culture gets 3-5 rules. Examples from b4d502:

| culture | taboo | who | why |
|---|---|---|---|
| tortles of the south-west of Ratukham | whales and seals; shellfish | everyone | divine: the sea domain of its "god of sea and rain" |
| same | swarming insects | everyone | purity: flies but goes on many legs |
| first humans of the west of Talatos | waterfowl | everyone | divine: the sky domain of its "god of sky and storm" |
| same | wheat and barley | priests | divine: the harvest domain of a lesser power |
| same | fowl | a lineage | symbolic: the fowl it relies on is kin to one lineage |
| humans of the west of Hizam (3) | wild swine | priests | divine: the hunt domain of "power of hunt and fertility" |
| same | whales and seals; hares | everyone | purity (straddles its categories) |

In all 298 living cultures: 549 divine, 428 purity, 89 identity (the staple of a people it fears or despises), 32 symbolic, 0 practical.

## What was built

- `planet/lineages/samples/techtree.toml`, `techtree.py` (PW-1304): the nodes `moralizing_high_god` and `divine_magic`; `build(..., gods_mode=)`
  drops a tech marked `gods = true` in `belief_only`; `rebuild(run_dir)` builds a stored run's tree in memory without writing it.
  Source: Norenzayan 2013, *Big Gods* (the hypothesis; Princeton UP). The Whitehouse et al. 2019 Seshat paper (Nature) was **retracted in July 2021**
  after Beheim et al.'s critique about missing data (Retraction Watch, 2021-07-07); the authors' 2021 "retake" says the main findings stand, and
  Beheim et al.'s reanalysis reversed the result. So the order (big societies first, or moralizing gods first) is contested and the node is a
  soft hazard with no dated Earth anchor. Found by web search, not read in full: treat the status line as a pointer.
- `planet/lineages/gods.py` (PW-1306): `Pantheons` (pure core), `derive` / `write` -> `gods.json`.
- `planet/lineages/taboos.py` (PW-1305): `culture_taboos` (pure core), `derive` / `write` / `write_religion` -> `taboos.json`.
- Wiring: `planet religion RUN [--out DIR] [--mode M] [--rebuild-techtree]`; a new run writes both files after its cultures
  (`output.py`); `GET /api/gods?run=` (the file, else computed in memory, never written); the viewer's Cultures table has a "gods" column
  (the leading being, +n, hover for the rest, with their individuation, spells and domains); the brief (`BRIEF_VERSION` 16) lists each
  culture's gods and food taboos where the run has the files.
- Tests: `tests/test_gods.py` (15), `tests/test_techtree.py::test_faith_nodes_and_gods_mode`.

## How the god tree works (every number marked JUDGEMENT in the code is a first guess)

Beings belong to a culture (cultures.py), not a deme: a culture is the unit that has a land and a way of life, and the demes inside it share it.
Per frame (the run's frames: 0.5 kyr recent, up to 4 kyr deep; the doc's 25-year step is finer than the stored frames, so drift is scaled by
the frame gap) each culture's land gives a salience per domain (coast, river, mountain, desert, forest, wetness, open country, tundra,
volcanic ground, from the same tags and rivers the demes use; plus herding, farming and metal from the techs it knows, war from its traits and
kingship). A being's weight moves toward the salient domains **of its own group** (water, sky, land, life, human) with e-folding 6 kyr, so an
inland-sea god turns to rain slowly and never to a forge. A salient domain with no being (>= 0.45 for 1 kyr) is born one. A culture born of
another copies its beings; merged cultures fuse alike beings (cosine >= 0.6) and carry the rest; beings that have come to be the same
(cosine >= 0.97) fuse; a being that no longer fits its land (devotion < 0.05) fades; a culture that dies out takes its beings with it
(`absolute` mode: they stay `dormant`). Individuation follows the faith techs the people holds (spirit ritual 0.1, burial 0.2, temples 0.45,
kingship 0.6, high god 0.9, as a ceiling); only the most devoted being goes to the top tier, the rest stop at kingship's. Above 0.5 a being
grants spells (not in `belief_only`). Names wait for PW-986: a being is labelled by domains and rank.

## Judgement calls (also filed as drafts for Daniel where they are his)

- Culture-level beings, not deme-level (a culture is the unit with a land and way of life).
- The moralizing-high-god rate 0.08 / spread 0.3 and divine magic 0.2 are guesses; checked only that the high god is neither universal nor absent.
- The purity weight is a seeded placeholder per culture (0.1-0.6) until PW-1307's ledger exists.
- The ITEMS table of wild kinds and what each "straddles" is my reading of Douglas 1966 (I did not have the book to hand); the Leviticus
  examples (swine, hares, shellfish, eels) are named in the ticket only as "on Leviticus". Sourcing it properly is a follow-up.
- "Practical" (poison, parasites) is not modelled, so none is emitted (the ticket: only if ever modelled).
- Rivers/lakes/hydrology-bound spirits are bound to a feature class and the culture's place name, not to a named river.

## Limits and follow-ups

- The window is 300 kyr (the demes' window), so dragons' gods are not shown as the oldest. A pre-window seed from `ritual_since_kyr` would do it.
- A stored run's tech tree predates the faith nodes: use `--rebuild-techtree` (new runs have them). Rebuilding also redraws the tree's random
  numbers, so other techs' dates can shift slightly against the stored tree.
- No world-creation control for `gods_mode` yet (the viewer has the mode only through `?mode=` on the API): draft filed.
- Gods and taboos do not feed back into the history; the taboos do not change the culinary diet yet (the brief carries them for the book).
