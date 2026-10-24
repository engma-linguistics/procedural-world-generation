# Culinary-dnd intake: what procgen_world must enable for the culinary ethnography

*Proposal, 2026-10-24. Read-only intake of the owner's `culinary-dnd` repo (engma-linguistics/culinary-dnd, at 545624f)
against procgen_world main (9af3c9f). The epic this serves is PW-692. Nothing in procgen_world changes yet. The
items with no ticket are filed as inbox drafts (listed in §6).*

**The finding in one paragraph.** The culinary repo stalled on its map. A month ago (2026-09-24) the owner deleted
every prose draft to "focus on the facts of the world and people and foods first". In the same session the lineages,
frame, drink, crops, giants and tiefling history were settled, and two world maps were drafted. Since then there has
been one commit, a stray note. Backlog item B-22, the map, is filed under "Foundations — unblock the most", and nearly
every open fact waits on it: the adjacency table "is only as good as the geography", goliath neighbours, where the
abyssal tieflings live (B-02), the kobold homeland (B-23), where stone, cloud and storm giants live, Table II's prices
(which are distances), the itinerary, the Jangwa cattle peoples (B-08) and "who lives where sugarcane comes from". The map draft itself had to break
the Spine in two to satisfy written constraints that fight each other. The problem is that the geography was authored
top-down, and that is the problem procgen_world exists to solve. Fuels follow vegetation, vegetation follows climate,
and climate follows the map. Who lives next to whom follows the history. **The single most useful thing
procgen_world can do for the book is to become its map and its deep history, and to hand the culinary side a
per-region, per-people, per-era brief it can write from.**

---

## 1. What the culinary repo is

### Structure

| Path | What it is | Status |
|---|---|---|
| `docs/culinary-ethnography-master-reference-v3.md` | **the single source**: frame, geography, roster, the two tiefling peoples, dragonborn, drink, stimulants, crops, timeline, teleportation, haloclines, tables | settled-unless-revisited |
| `docs/genetics.md` | one tree of life, split depths, the interfertility tiers T0–T3, ★ overlays, the ✦ half-elf exemption, contact-zone adjacency | tree ruled 2026-09-24 |
| `docs/decisions/` | five dated rulings: half-elves (08-15); lineages; narrator and book form; drink, crops and names; tiefling history and Mora (09-24) | ruled |
| `docs/01–03-fact-sheets-*.md` | per-culture sheets: ecology → fuel → staples → techniques → drink → who eats together → implements → etiquette → what outsiders get wrong, plus "the one physical fact" and **Decide** prompts | v2-era; v3 wins |
| `docs/giants.md` + seven giant sheets | body plan and energy budget (Kleiber), one-way hospitality, six kinds and their food systems | first pass |
| `docs/world-map.md`, `docs/world-map-2-continents.md` | a written one-continent map with an origins overlay and image prompts, and a two-continent spitball (Jangwa as the reptile continent, "the Inner Sea is the milk line") | proposals: **the stall** |
| `docs/04` naming, `05` implements, `06` foods table, `07` open questions, `08–11` archived prose | | 05/06 deferred "very late, needs the map" |
| `data/cultures.yaml`, `docs/backlog.md` | status of each culture; everything trackable (B-01…B-26) | |
| `.claude/skills/` | `narrator-voice`, `setting-canon`, `naming` (phonologies, name registry) | |
| `random_notes_to_incorporate.md` | 2026-10-24: a culture whose food words are all synonyms for other words, so a meal can be a poem | idea |

### The peoples (about 30)

- **Terrestrial clade (mammals):** goblinoids (goblins, hobgoblins, bugbears), giants (hill, stone, fire, frost,
  cloud, storm), dwarves, halflings, goliaths, orcs (Arha of the steppe, Anja of the forest), humans (forager root,
  grain belt, Jangwa cattle peoples).
- **Other mammalian branches:** cat peoples (leonin, tabaxi), and the aquatic clade (merfolk; deep folk, whom
  outsiders call "sea elves").
- **Reptilian line:** lizardfolk (Sun Flats and delta, one people), dragonborn, kobolds (not yet placed), tortles. The
  avian branch: aarakocra (raptor-highland, granivore-lowland, piscivore-coastal, sailor).
- **Fae arrivals:** elves (Inheritance and Ephemeral), gnomes.
- **Overlays and exemptions:** kenku (aarakocra under a divine curse, ★), infernal and abyssal tieflings (planar
  overlays on humans, ★; **changed by the owner, §4**), half-elves (✦, no population), half-orcs (a country).
- **Cut or absorbed:** warforged, changelings, yuan-ti, locathah, gnolls, firbolgs (absorbed into pastoral
  peoples), aasimar and genasi (individuals).

### The core premises as I read them

1. **Implements are downstream of food; food is downstream of ecology, fuel, staple and social structure.** Every
   entry answers: what's the fuel, what's the staple, what do they drink, who eats together, what do outsiders get
   wrong.
2. **One people is not one cuisine.** Outsiders lump; the ethnographer splits. The flagship case is the Arha steppe
   orcs: a dung fire cannot sear, so the barbecue assumption is backwards.
3. **Bodies set the menu.** Cats taste no sweet. Birds feel no capsaicin. Aarakocra cannot suck. Dragonborn have
   conical teeth and a scent organ. Deep-steppe orcs digest fresh milk badly, so their dairy is fermented.
4. **One tree of life, with convergence on people-shapes as the premise.** Interfertility falls out of split depth,
   in tiers. Only the Fae are outsiders. The "gods did it" exemption is spent, once, on half-elves.
5. **"What ferments follows what's stored."** A people's drink is a readout of its staple.
6. **Three crop exchanges, each a story of spread:** the potato is forgotten (out of the dwarven terraces, ~8 kya),
   the peppers are storied (out of the jungle, spread by wing before road), and sugarcane is happening now (dried paste
   by sail, fresh cane only by circle).
7. **The book is written at a rupture.** Teleportation circles make distance optional. Preservation cuisines lose
   their point, chokepoint cities die and hub cities boom. The infernal strait empire is the emotional centre, and
   the narrator's own patron is the cause.
8. **Contact zones are cuisines in their own right ("haloclines"),** and culinary mixing is independent of genetic
   mixing.

### Where it got stuck, and why

The commits tell the story:
- 08-15: genetics and the half-elf ruling.
- 09-24 morning (`6b75d03`): the owner's notes (#DSB / DANIEL'S NOTE) answering the flight pack. All 25 chapters
  were deleted because "there's too much to determine at this time". The owner wanted world facts first.
- 09-24 (`fefc47f`): the rulings above, plus two map drafts.
- 10-24 (`545624f`): one stray note.

Every ruling since then has needed the map, and the map cannot be ruled by taste alone, because it decides who evolved
next to whom: "once a variant is chosen, some basics may need redoing, because the map fixes who evolved near whom"
(B-22). The two-continent spitball shows the owner wants deep-time consequences, such as no native dairy on a reptile
continent, and those cannot be authored consistently by hand at that depth.

---

## 2. Tier 1, solid: build into procgen_world

"Solid" means ruled in the culinary repo, or physics or biology that holds on any world, or something the owner asked
procgen_world for directly. The table is in rough build order; the order of work is §6.

| # | Item | Why it's solid | Ticket | Effort |
|---|---|---|---|---|
| 1 | **The owner's world as a lineages preset** (`samples/seven_meals.toml`): the tree from `genetics.md`, groups for the split peoples, bodies, niches and wishes; `dnd.toml` untouched | the tree and tiers are ruled; the owner asked for it | new: `draft-owner-world-lineages-preset` | m |
| 2 | **More body keys**: suction, teeth, gut, salt craving, display organ (horns, antlers, shed cycle), activity hours, ectothermy, fire use | the culinary repo's "one physical fact" is usually a body fact, and PW-694's keys miss most of them | new: `draft-body-keys-for-the-culinary-world` (PW-694 follow-up) | s |
| 3 | **Fuels by region** (wood, charcoal, dung, peat, crop straw, grass, driftwood, seaweed, **rendered fat**, coal) | the book's organizing fact ("a fire that cannot sear") | **PW-722**, plus fat and oil for treeless cold coasts (goliaths) | s |
| 4 | **Crops**, with the canon's rows (below) and **crop-exchange events**: when a crop reached each region, and by what route (wing, road or sea) | the three exchanges are spread stories, which is exactly what the model does | **PW-721**, extended | m |
| 5 | **Animals as stocks and food goods**, the dairy form (fresh or fermented, from the lactase share), and new rows: pig, reindeer, camel, bees, giant-scale stock | Arha dairy, Jangwa cattle wealth, giant herds, forest-orc mast pigs | **PW-719**, **PW-724** | m |
| 6 | **Salt and sea-food goods**: salt sources and distance to salt; fish (shelf, upwelling, reef, kelp, river runs, lakes), shellfish, sea mammals | the salt-lake grievance; fish sauce; the fiends' salt craving (§4); pit-oven islanders | new: `draft-salt-and-sea-food-goods` | s–m |
| 7 | **Contact history and interfertility tiers**: per pair of peoples and per epoch, the border, the mixing, the first contact and the corridor; the tier from split depth; the **substrate** (who held a cell before its present people); Tier-1 clines carrying body shares across a border | genetics.md's whole adjacency section; the substrate-vocabulary premise; "the milk line runs through the orc side" | new: `draft-contact-history-and-interfertility-tiers` | s–m |
| 8 | **Marine peoples**: lines whose habitat is the sea (deep folk on the trench and the vents, merfolk on the tidal interface, storm giants offshore) | today every line lives on land cells | new: `draft-marine-peoples` | m–l |
| 9 | **The culinary brief**: an export per region, people and era (§7) | the interface the owner asked for | new: `draft-culinary-brief-export` | m |
| 10 | **Reputation and exonyms**: what neighbours call a people and why, set by conquest and contact history, kept apart from what the people is | the owner's fiend change (§4); the book's "outsiders lump" thesis | new: `draft-reputation-and-exonyms` | m (v0), l (with PW-661) |
| 11 | **Finding a world for a setting**: score candidate worlds on a written list of setting requirements (rain-shadow steppe, inner sea with a strait, desert belt, volcano coast…) and keep the best | "find a planet with cool continents"; whichever way Q1 (§5) goes, a world has to be chosen | new: `draft-world-fit-for-a-written-setting` | m |

### 2.1 The owner's world preset

It lives beside `dnd.toml`, which stays as the traditional template with every normal playable race. Its source is
`genetics.md` and the decisions directory. When the two disagree, the culinary repo wins for people facts and
procgen_world wins for where and when. The tree, with the culinary split depths:

| Line | Origin | At | Notes |
|---|---|---|---|
| `life` | root | ~320 Myr | "one tree of life": the mammal–reptile split is as deep as Earth's. The run's deep epochs are plate-moved, so this only says which old landmass each line began on (answering the two-continent question by simulation). Worlds sliced before ~320 Myr clamp, as now |
| `mammalian` / `reptilian` | split | ~320 Myr | |
| `feline` → `leonin`, `tabaxi` | split | ~60 Myr; T1 sisters | wish: island (the Near Isles) |
| `ruminant` → `antelope_folk`, `cervid_folk` | split | ~50 Myr; ~25 Myr apart | **new, §4**: the infernal and abyssal "fiends" |
| `aquatic` → `merfolk`, `deep_folk` | split | ~15 Myr; deep folk ~3 Myr | marine (item 8) |
| `terrestrial` → `goblinoid` (6 Myr) → `bugbear` (2 Myr), `goblin`/`hobgoblin` (250 kyr) | split | | **culinary topology**: bugbears split first. dnd.toml has hobgoblins and bugbears together |
| `giant` (3 Myr) → hill, stone, fire, frost, cloud, storm (300–500 kyr) | split | | the kinds are T1 with each other and almost never interbreed; storm giants marine-coastal |
| `dwarf`, `halfling` | split | ~1–1.5 Myr | T2 with humans and each other (dnd.toml has halflings 100 kyr off archaic humans) |
| `human_line` → `goliath` (400–500 kyr), `orc` (300 kyr), `human` | split | | **goliaths are not giant-kin**: "giant-kin" is an exonym (item 10) |
| `orc` groups: `arha` (steppe), `anja` (forest) | group | ~9 kyr (Anja: the "returnees", B-03, possibly later) | Arha `milk` ≈ 0.1 (fermenters), not dnd.toml's 0.7 |
| `human` groups: forager, grain-belt farmer, Jangwa cattle herder (milk, separately arisen), seafarer, arctic | group | | the forest–steppe margin herders carry milk ~0.6 |
| `draconic` (5 Myr) → `dragonborn`, `kobold` (2 Myr); `lizardfolk` (groups: desert, delta); `tortle` (deeper) | split | | kobold homeland left to the sim (B-23) |
| `avian` → `aarakocra` (groups: raptor-highland, granivore-lowland, piscivore-coastal, sailor) | split | | **sweet = true** (Tier 2, §3.7) |
| `kenku` | template on aarakocra | 1–5 kyr | "the curse always takes": a share that only grows where the two live together (small spec change) |
| `elf` (groups Inheritance, Ephemeral), `gnome` | arrival, separately | ≥ 30 kyr | two portals ("two separate places") |
| `half_elf` | contact hybrid | | **no population**: needs a `linger = false` switch, since PW-613 otherwise makes a people of them where their parents last met |
| `half_orc` | hybrid, `contact = false` | ~10 kyr | "a country ten thousand years old", at the margin |
| off | drow, sea elves, tritons, firbolgs, aasimar, genasi, troglodytes, the tiefling template | | cut or absorbed in the canon |

Wishes come from the canon's adjacency table:
- **near:** halflings and humans; the margin (humans, Arha, Anja); hobgoblins, goblins and bugbears; delta lizardfolk
  and piscivore aarakocra; dwarves and gnomes; the Jangwa three (hobgoblins, cattle humans, granivore aarakocra);
  tortles and sailor aarakocra; storm giants and deep folk; cervid folk and humans (§4).
- **place:** cats on islands; tortles on an island chain; goblins in the jungle; dragonborn on a delta with farmland;
  Arha on the steppe; gnomes on wet mountains.

Two things the canon has that the model cannot yet do. Both go in the same draft:
- **Culture-only groups** (Inheritance and Ephemeral elves share one forest) need no niche difference. They are
  listed for the brief and roll up into their people, but they take no land of their own.
- **Dated historical events** (the old cervid polity, the antelope conquest) are `[[event]]` anchors, §4.5.

### 2.2 Crop rows the canon names (for PW-721)

Each crop gets a wild range and a homeland chosen by the sim, not authored:
- a **highland tuber** (the potato), out of terraced cool mountains;
- **chilies**, wild in the wet tropics. **Bird-dispersed: their spread rides the flying peoples' ranges and crossings,
  so they reach highland valleys before ports when fliers live there.** The "by wing, not road" gap then falls out of
  the world;
- **sugarcane**, wet tropical islands. Two forms: the dried paste travels by ship, fresh cane travels nowhere (circles
  are authored);
- **sorghum and millet** (savanna); **rice** (wetland, delta); **wheat and barley** (Mediterranean winter rain);
- **grape** (Csa/Csb with warm summers: the cool forest elves cannot grow it, which is why the elves' cellars hold wine bought from the south); **olive**;
- **agave** (hot desert); **tea** (wet tropical highland); **coffee** (tropical highland margin); **tomato** (warm,
  rich soils; the canon has it native to the volcanic coast);
- **wild staples:** acorn and chestnut mast (oak country, from the vegetation), honey (everywhere temperate and
  warm), the numbing-spice shrub (an endemic of wet alpine meadow: one district).

Output per cell: crops known and the date and route each arrived by. The crop events ("chilies reach the highland
valleys at 15N 40E by wing ~0.5 kyr ago, the ports by sea ~0.38 kyr ago") are the exchanges.

### 2.3 What already exists and only needs exporting

- Biome, Köppen, soils, fertility, fresh water, rivers and harbours.
- The goods: `fertile`, `grazing`, `foraging`, `timber`, `fuel`, `seals`, `seabirds`, `coral`, `mangrove`; resources
  `salt` and `coal`; peat depth.
- Peoples' composition per cell and their bodies.
- Animals known and dairy.
- Land use, neighbours and mixing zones. **Mixing zones are the canon's haloclines.**
- The recent pass's droughts and cold spells: "the bad years". The giant sheet says every popular monster is a food
  system in a bad year.

The brief (item 9) is mostly a reader of these.

---

## 3. Tier 2: wishy-washy premises, conflicts with simulated worlds, and recommended edits to the culinary repo

Each item gives a direction for the culinary side. None of these edits is made here: that repo is read-only for this
intake.

**3.1 The written map should become a list of requirements.** Some of the canon's geography is robust physics on any
Earth-like planet:
- a desert belt near 20–30° (the Hadley cells), then savanna, then equatorial forest;
- a dry steppe in the lee of a north–south range under westerlies;
- the wet windward mountain flank as the most varied strip.

The rest is specific and must be found, not assumed: an enclosed sea with a narrow strait into a second sea, a volcano
on its shore, a great river from tea highlands to an eastern delta, an island arc off the west coast at desert
latitudes, an island chain with a trench beyond. **Direction:** rewrite master reference §3 as "setting requirements"
(must, nice to have), drop "the Spine broken by the Inner Sea", and let procgen_world find a world that scores well on
them (item 11). Whatever the chosen world gives, the canon adopts. B-22 then dissolves, because the map is the world.

**3.2 Deep-time origins and placements should be simulated, not authored.** `world-map.md` contains:
- the origins overlay: the terrestrial cradle in the southern highlands, the aquatic clade starting in the Inner Sea's
  shallows;
- the stone, cloud and storm giant placements;
- the kobold homeland;
- B-02 (the Uplands, or the deep forest?).

These are what the lineages model does. **Direction:** strike them as canon and read them from the run.

**3.3 The two-continent "milk line" is an outcome to look for, not a premise.** It is the best idea in the map drafts,
and it is emergent: if the reptilian line holds a landmass alone through deep time and mammals cross late, that land
has no native dairy. **procgen_world can read it cheaply.** For each landmass, the clade of its native fauna can be
taken as the root stem that held it longest before the people-shaped lines (no fauna is simulated, PW-184; this is a
proxy, worth a line in the brief). **Direction:** keep it as a hoped-for outcome. Prefer candidate worlds that show it
(a nice-to-have in 3.1).

**3.4 Split dates are tier inputs, not history.** The canon's own rule is "dates are orders of magnitude, never on the
page". procgen_world draws its own times around anchors. **Direction:** keep the culinary depths as the input for the
tiers (item 7), and accept a world's drawn dates for the history.

**3.5 Anchor the timeline; don't fix it.** The herding divide (11–9 kya), the potato (8 kya), the first dragonborn
settlement (9.5 kya) and the peppers' wing-before-road gap (~0.5 vs 0.38 kya) should become anchors the sim draws
around, as the animal anchors already are (× lognormal). The very recent items stay authored present-day facts: the
sugar paste 30 years ago, circles for two generations, fresh cane for 10 years. The sim's present is a snapshot, not
a decade.

**3.6 Steppe-orc milk: the culinary repo is right and `dnd.toml` is wrong for this world.** On Earth, Mongolian
herders mostly lack lactase persistence and live on fermented dairy. The Arha are that case. Two things follow:
- procgen should **derive the dairy form** per people: a low lactase share with dairy herds gives soured and
  fermented dairy, a high share gives fresh milk (item 5);
- "the milk line runs through the orc side" needs Tier-1 gene flow at the margin: a cline carrying the human
  herders' share into the neighbouring orcs (item 7).

**3.7 Aarakocra taste sweet.** `dnd.toml` gives the avian stem `sweet = false`. Earth's birds are split: many
songbirds and hummingbirds taste sugar through a repurposed umami receptor, while raptors, as far as is known, do not. The canon needs
sweet-tasting aarakocra: the raptor-highland ecotype bred peppers for fruit flavour, tasting only the sweetness. So
in the owner's preset, aarakocra get `sweet = true`. The raptor ecotype tasting sweet goes against Earth's raptors,
and it is the joke, so I'd keep it (Q7).

**3.8 Culture-only splits are the culinary repo's, not the sim's.** Some splits are cultural, not niche-driven:
- the Inheritance and Ephemeral elves (a schism in one forest);
- the infernal diaspora's two waves;
- the halflings' "same larder, different clock".

The groups model needs a niche difference to separate a group. **Direction:** author these in the culinary repo. The
brief lists them as "same land as".

**3.9 Read these from the sim rather than authoring them:**
- each people's leading fuel, staple crops, herd animals, fish and wild foods;
- who borders whom, and for how long;
- the halocline list (the mixing zones);
- substrate vocabulary (from the previous occupant);
- the bad years;
- which giants are rare and where;
- the first draft of each fact sheet's **ecology / fuel / staples** lines.

The drink rule "what ferments follows what's stored" is mechanical enough to be a **suggested** drink line in the
brief (staple grain → beer, mare's milk → kumis-like, honey → mead, palm → toddy, agave → agave wine). The culinary
side overrules it freely.

**3.10 The reverse: keep these authored.** procgen should not try to derive:
- etiquette, implements, names, the narrator, the guild;
- the circles and their routes;
- the half-elf exemption and the kenku curse's source;
- the deep-folk intoxicant politics;
- sumptuary law, the fasting calendar, the antler calendar's liturgy;
- the convergence premise.

**3.11 The teleportation rupture needs real chokepoints and hubs.** The circles are authored (magic is PW-696). But
"chokepoint cities die, circle cities boom" reads true only if the strait, passes and river mouths are real places in
the world: these are highlights plus a strait finder (item 11), and cities and states come with PW-661. **Direction:** place the infernal strait empire on the
chosen world's best strait, and the circle hubs at its best harbours and river crossings.

**3.12 "Outsiders lump" is partly derivable.** Several canon errors share one shape: "giant-kin" for goliaths, "sea
elves" for deep folk, "one undifferentiated goblinoid menace", "half-elves and half-orcs in one breath", and now
"devils and demons". In each, a people is named for what it looks like to neighbours with thin or hostile contact.
Item 10 generates them. **Direction:** treat "what outsiders get wrong" as partly read from the brief's reputation
rows, then sharpened by hand.

**3.13 Kenku: "the curse always takes."** A template's share is fixed today. The canon implies a slow, monotone
growth on the docksides wherever kenku and aarakocra marry. This is a small spec change in the preset draft.

**3.14 Food-word synonyms (the 10-24 note).** That culture is the culinary repo's to author. Which neighbour's
language a culture's food words come from is a contact-history fact: the substrate and the longest trade partner. The
brief carries it, and a poetic-cuisine people is likelier where many substrates meet (a long-mixed corridor).

**3.15 Era.** The canon's present has guilds, circles, stamped amphorae and an empire's bureaucracy: early modern
with magic. procgen's default `era = "renaissance"` fits. It is a placeholder until PW-675.

---

## 4. The antelope and cervid "fiends": a worked proposal

### 4.1 The change

`dnd.toml` keeps its tiefling template. In the owner's world:
- the **infernal** tieflings (horned) are an **antelope-like (bovid) people**;
- the **abyssal** tieflings (antlered) are a **cervid (deer, moose, reindeer) people**.

"Devils and demons" is what their human neighbours made of them: *the devils who came down from the western steppe
and took over swathes of land.* History can be unkind. The iconography already fits. Horizontal-pupilled eyes,
hooves and goat horns are the classical devil, and the real animal they describe is a bovid.

### 4.2 Lineage and origin

**Lean:** one **ruminant branch** off the mammalian line, deep (~50 Myr, the same order as the cats' 60 Myr: T3 with
humans). On Earth, bovids and cervids diverged ~25–30 Myr ago within the horned ruminants. So the two are relatives,
with no offspring between them (T2/T3), and they look alike to a human. It follows that **there are no half-fiends.**
The canon's "half-demon founder", "a trait that spread from a caste" and "every infernal tiefling descends from that
signing" all become human stories about them, which is the point. "Many humans trace their lineage to the old empire"
stays true as a *claim*, the way Rome claimed Troy.

Rejected:
- **(B) Close sisters of humans (T1), with horns by convergence.** It would keep half-tieflings as people. But it
  makes the bodies human-plus-horns and throws away the ruminant gut, which is where the cuisine lives.
- **(C) Two unrelated branches.** It loses the lumping: outsiders call both "fiends" because they *are* related, just
  not to the outsiders.

The sim chooses the homelands: each line's origin is the best niche in its parent's range, with isolation preferred
(§2 of `lineages.md`). The niches below should land the antelope folk on open dry country and the cervid folk on
forest and its edges, wherever the world has them.

### 4.3 Bodies and senses

| | Antelope folk ("infernal") | Cervid folk ("abyssal") | Culinary consequence |
|---|---|---|---|
| gut | foregut fermenter (rumen), **grazer**: grass and grit | foregut fermenter, **browser**: leaves, buds, mast, fungi, lichen (north), water plants (moose-like) | `cellulose = true`. The steppe's grass is their food directly: they need herds less than humans do. They chew cud for an hour after a meal, so a meal is long and the cud-chewing is the social part |
| diet | `herbivore`-leaning; milk, eggs, a little meat | the same; **gnaws bone and shed antler** for minerals (deer do) | the canon's open question "is antler eaten?": yes, gnawed in velvet season |
| starch | **grain in quantity sickens them** (the rumen sours: acidosis) | the same | the antelope conquerors rule a bread state they cannot eat much of |
| tannin | grazers lack the tannin-binding saliva | **browsers have it** (deer and moose saliva binds tannin) | cervids eat acorns barely leached. The canon's acorn-leaching then belongs to their *human* neighbours, and the goblin manioc resonance (§5c) changes meaning |
| salt | strong sodium craving, worst in spring | the same, plus calcium and phosphorus in antler season | **salt is strategic**: conquests follow salt, and the salt-lake grievance has a third party |
| teeth | no upper incisors (a dental pad); high-crowned grinders for grit | dental pad; low-crowned browsing teeth | food is pulled and torn, not bitten off; the knife cuts strips in the kitchen. Implements change, as the dragonborn's talons do |
| sweet, bitter, capsaicin | sweet yes, bitter normal, feels capsaicin | sweet yes, bitter **low** (tannins), feels capsaicin | |
| smell, sight | keen smell (flehmen); **dichromat**, wide field | the same | colour on the plate means little; aroma and texture do |
| display | **horns**: permanent, growth rings by year | **antlers**: shed and regrown yearly; in both sexes (reindeer-like) or males only (deer-like) | horn rings are an age record you cannot take off (law that "runs on signatures" becomes law that runs on rings). The antler calendar is biology (the canon's Decide 1: one clock, or two) |
| milk | tolerated (the rumen ferments it) | the same | |
| activity | crepuscular; endurance runners | crepuscular | |

### 4.4 Ways of life and homelands (preset niches)

- **`antelope_folk`:**
  - temp −5..26 °C, rain 150–900 mm; prefers steppe, savanna, open, desert edge;
  - traits nomadic, hardy; density ~0.8; explore 0.7; insularity 0.5;
  - `[[use]]` grazing at pull 0.75;
  - groups: **steppe runners** (cold steppe, saiga-like), **mountain** (ibex-like: hills and peaks), **savanna**;
  - steppe herders and raiders.
- **`cervid_folk`:**
  - temp −12..18 °C, rain 400–2000 mm; prefers forest, temperate, continental; forest edge and oak mast;
  - density ~2; insularity 0.6;
  - `[[use]]` foraging and timber;
  - groups: **forest** (red-deer-like, oak and chestnut country), **boreal wetland** (moose-like), **tundra herders**
    (reindeer-like, lichen, both sexes antlered; neighbours of goliaths and frost giants);
  - forest peoples.
- **Wishes:**
  - `cervid_folk` near `human` (the old polity was mixed);
  - `antelope_folk` near `human` at a steppe-to-farmland edge (weight 0.5);
  - `antelope_folk` apart from `arha` at 0.3 (grazing rivals; the canon gives the steppe to the orcs).

### 4.5 History reinterpreted (`[[event]]` anchors until PW-661)

| Canon (tieflings) | Owner's world | In procgen |
|---|---|---|
| The old abyssal empire (~3–1.9 kya); the trait "began in a small cadre, spread, a good share but well under half" | a **cervid-led polity over a human majority** in forest and upland. The "trait" is the cervid share of its people; "under half" is a census, not a curse | `[[event]] kind = "polity", by = "cervid_folk", over = ["human"], at = "3 kyr", until = "1.9 kyr"`: an elite overlay. The sim places it where cervids and humans cohabit most |
| The infernal rebellion (~2.1 kya): "altered entire, 100%, in one event", by contract with devils; took the strait | **a conquest from the steppe**: the antelope folk came down in a generation and took the strait and its farmland. The "contract with devils" is the humans' memory of the **vassal treaties** they signed. "Every infernal descends from the signing" is a founding myth about *the treaty-bound humans*, told by the humans | `[[event]] kind = "conquest", by = "antelope_folk", over = ["human", "cervid_folk"], at = "2.1 kyr", from = "steppe"`: an overlay of rulers (~5%) spreading over the hosts within ~1000 km in ~100 yr from the steppe edge nearest the best strait. **These are the reputation-making events** |
| The fall (~2–1.5 kya): the abyssal folk pushed into the Uplands | the cervid folk withdraw to forest uplands; the sim's refuge and displacement logic | from the competition, nudged by the event |
| The infernal contraction (~200 ya), the circles | unchanged, authored | |
| Abyssal tieflings "integrated with humans, many humans trace their lineage to them" | cervid and human communities mixed for millennia; claimed descent | composition per cell; the claim goes in the brief's reputation rows |
| The antler calendar | cervid biology; the human towns that keep it are the old polity's core | the old polity's cells in the brief |

The canon's emotional centre survives intact. The empire that is being routed around is still the strait empire;
its rulers are antelope folk and most of its people are human. Some suggestions for the culinary side, not rulings:
- the fasting calendar (half the year without meat or dairy) is the overlords' own diet imposed as law, which is why
  humans call it devilish;
- the reclining one-handed meal and the cud-chewing hour fit together.

### 4.6 What this does to the game

A tiefling player character in the owner's world is an antelope- or cervid-folk character: same rules, new flavour,
and an exonym they live with. `dnd.toml`'s tiefling template is untouched.

### 4.7 How procgen generates the misunderstanding

This is the reputation mechanism (item 10, `draft-reputation-and-exonyms`). Its inputs, per observer people O and
subject people S:
- the **contact record** (item 7): first contact, border length over time, mixing;
- **events** that set O against S:
  - authored `[[event]]` conquests and polities;
  - derived incursions: S's presence rising sharply in O's cells within a few centuries (displacement, the
    nomads' riding fronts);
  - each with its direction from O ("from the steppe to the west", from centroids and highlights);
- S's **visible body**: the display keys (horns, antlers, scales, feathers, size, aquatic) matched against a small
  table of folk categories (devil: horns and hooves; demon: antlers; giant-kin: size; sea-elf: an aquatic people-shape;
  fae: arrival), with each culture free to add categories later;
- the **tier** between O and S (alien bodies get mythic names readily).

Rules:
- **Category.** O names S by the folk category S's body fits best, unless O's contact with S is rich and peaceful, in
  which case O knows S by an ordinary name.
- **Valence from history.** S conquered O: feared. S ruled O: resented. O ruled S: despised. Trade: exotic. Barely
  met: monsters at the edge.
- **Persistence.** A conquest's reputation fades slowly (e-folding ~1.5 kyr, slower with writing, by era), and
  peaceful centuries erode it only a little. History can be unkind.
- **Lumping.** O gives one name to several peoples of one category when its contact with each is thin ("fiends":
  infernal and abyssal), and splits them where contact is rich.
- **Borrowing.** A people with no contact of its own takes the reputation of its best-connected neighbour, so the
  whole west calls them devils though only the strait was conquered.

Outputs:
- `meta.present.reputation[O][S] = {category, valence, basis, since, strength, lumped_with}` and the reverse;
- a story line: "To the farming humans of the plain at 44N 21E, the antelope folk are 'devils who came down from the
  steppe to the west' (a conquest ~2.1 kyr ago); the humans who live among them call them by their own name";
- a brief row with "what they are" (lineage, body) next to "what they are called" (by whom, and why).

Version 0 runs on the lineage history and the event anchors (no states). Version 1 reads PW-661's conquests and
trade.

---

## 5. Questions for back-and-forth with the owner

Each shapes both repos.

1. **Who owns the map?**
   - (A) The sim's world is the map; the canon's geography becomes a requirements list scored over candidate worlds.
   - (B) The written map is kept, and worlds are searched until one fits it closely.
   - (C) Author the map and force the sim (rejected: forcing).

   **Lean A** (with B's list as the score).
2. **How authored are the timeline's dates?**
   - (A) Anchors the sim draws around, per world.
   - (B) Exact.
   - (C) Sim-derived, and the book adapts.

   **Lean A**, with the last 30 years authored.
3. **The fiends' depth.**
   - (A) A deep ruminant branch (~50 Myr): no half-fiends, and the "half-demon founder" is a myth.
   - (B) T1 sisters of humans, so half-tieflings exist.
   - (C) Two unrelated branches.

   **Lean A.**
4. **The infernal origin.**
   - (A) A conquest from the steppe replaces the rebellion (the owner's "came down from the western steppe").
   - (B) Keep the rebellion: the antelope folk were a subject people inside the cervid polity.

   **Lean A.** It makes the reputation event a conquest.
5. **Antlers in both sexes or males only?** It is the canon's open Decide.
   - (A) Reindeer-like: one clock.
   - (B) Deer-like: two clocks, so the calendar is a male rhythm and the women keep another.
   - (C) By group: tundra herders have both sexes antlered, forest folk only males.

   **Lean C:** the one-people-not-one-cuisine thesis in a skull.
6. **Pull a thin slice of history forward from v3?** The canon's premises need empires, conquest and trade. PW-661 is
   v3.
   - (A) A v2 "contact and events" slice: `[[event]]` anchors, incursions, reputation, cost-distance trade reach.
   - (B) Wait for PW-661.

   **Lean A.** It is cheap, and it is the shape PW-661 can grow from.
7. **Aarakocra sweet taste, including raptors?**
   - (A) All ecotypes taste sweet (the pepper joke needs it).
   - (B) The raptors don't, so the joke moves to the granivores.

   **Lean A.**
8. **Source of truth for people facts.**
   - (A) The culinary repo owns bodies, ancestry and rulings; procgen's preset mirrors them, with a check.
   - (B) The preset is canon.

   **Lean A.**
9. **Marine peoples: how far?**
   - (A) Habitat on sea cells for deep folk, merfolk and storm giants.
   - (B) Coastal land-lines only, with the deeps authored.

   **Lean A** for merfolk and storm giants. Deep folk are a "couldn't visit" chapter, so (B) is acceptable for them if
   the cost bites.
10. **Is the owner's world fantasy-only?** Real mode already keeps humans only. **Lean:** the preset is fantasy, and
    real mode is the existing switch.

---

## 6. Suggested order of work for the fun lane

Each step pays off on its own. Ticket ids where they exist; the new ones are inbox drafts filed with this proposal.

1. **The owner's world preset** (`draft-owner-world-lineages-preset`), with the small spec items: half-elf
   `linger = false`, the kenku growing template, `[[event]]` stubs (stored, read later). Build on the leans of
   Q3–Q5. *m.*
2. **Body keys** (`draft-body-keys-for-the-culinary-world`). *s.*
3. **Brief v0** (`draft-culinary-brief-export`), on what exists today (§2.3), so the culinary side can start at once.
   *m.*
4. **Fuels**, PW-722, with fat and oil. *s.*
5. **World fit** (`draft-world-fit-for-a-written-setting`): pick the owner's planet. This is worth running before the
   heavy L7 peoples runs, and needs Q1. *m.*
6. **Crops**, PW-721, with §2.2's rows, carry by wing, and the exchange events. *m.*
7. **Animals as stocks and goods, and the dairy form**, PW-719, with new rows and PW-724 giant stock (the layer to
   uint16). *m.*
8. **Salt and sea food** (`draft-salt-and-sea-food-goods`). *s–m.*
9. **Contact history, tiers, substrate and clines** (`draft-contact-history-and-interfertility-tiers`). *s–m.*
10. **Reputation v0** (`draft-reputation-and-exonyms`). It needs 9 and the event anchors. *m.*
11. **Ways of life**, PW-723 (pastoral giants and Arha, fisher-foragers, sea nomads), which sharpens fuels and food.
    *m.*
12. **Marine peoples** (`draft-marine-peoples`). *m–l.*
13. Then PW-661's thin slice (Q6) and PW-675's era read, which turn the anchors into emergent history.

Dependencies outside the lane:
- The peoples need a time zoom (PW-651).
- The ice-age pass is parked (PW-470); v1's kludge (PW-471) is what the owner's world will run on.
- The showcase recipe is L7 (`docs/coordination.md`).

---

## 7. The interface between the repos

### procgen_world → culinary-dnd: the culinary brief

**CLI:** `planet brief RUN [--people ID…] [--region LAT LON --radius-km R] [--at KYR,…] [--format json|md]`.
- RUN is a peoples run of a world.
- The default era slices are the present plus 0.5, 1, 2, 3, 6, 9 and 12 kyr ago (from the recent pass's frames).
- `--all` writes one file per people and one per mixing zone into `briefs/<run>/`.

The JSON is the contract, carrying a `brief_version`. The Markdown is the same content for reading. The culinary repo
keeps copies (for example `data/worlds/<run>/`), so its "one home per fact" rule still holds: the world facts' home is
the brief.

**Per region (a cell neighbourhood or a mixing zone) and era:**

```json
{
  "brief_version": 1, "run": "d489d0", "world": "1df1c3", "tree": "seven_meals@<hash>", "era_kyr": 2.0,
  "place": {"lat": 44.2, "lon": 21.0, "radius_km": 400, "near": "the 1,800 km range at 40N 25E (highlight)"},
  "land": {"koppen": {"Cfb": 0.6, "Dfb": 0.3}, "biome": "temperate broadleaf forest", "soil": "brown forest soil",
           "fertile_share": 0.4, "rivers": [{"class": "barges", "to_sea": true}], "coast": "estuary harbour",
           "growing_months": 7, "frost_months": 3, "dry_season": null},
  "bad_years": [{"kind": "drought", "kyr": 2.3, "years": 300, "rain_x": 0.6}],
  "fuels": {"wood": 0.55, "charcoal": 0.15, "straw": 0.2, "dung": 0.1},
  "wild_food": {"mast": 0.8, "game": ["cervid-like browsers", "boar-like"], "honey": true, "fungi": "rich"},
  "fish": {"river_runs": true, "shelf": 0.3, "shellfish": ["salt marsh"], "sea_mammals": false},
  "salt": {"nearest": "salt pan of a closed basin", "km": 420, "sea_salt_coast_km": 180},
  "crops": [{"id": "wheat_barley", "since_kyr": 7.1, "route": "road"},
            {"id": "chili", "since_kyr": 0.5, "route": "wing", "from": "jungle at 5N 30E"}],
  "animals": [{"id": "cattle", "since_kyr": 6.0, "dairy": "fresh"}, {"id": "pig", "since_kyr": 7.5}],
  "peoples": [{"id": "human", "group": "farmer", "share": 0.62}, {"id": "cervid_folk", "group": "forest", "share": 0.25}],
  "substrate": [{"id": "cervid_folk", "held_until_kyr": 3.0}],
  "neighbours": [{"id": "antelope_folk", "border_km": 900, "since_kyr": 9, "tier": "T3"}],
  "trade_reach": {"days_by_road": {"steppe": 12, "strait": 20}, "by_sea": ["harbours within 1500 km"]},
  "events": [{"kind": "conquest", "by": "antelope_folk", "kyr": 2.1, "from": "steppe to the west"}],
  "suggested": {"drink": ["beer (grain)", "mead (honey)"], "notes": "rule-based; the culinary side overrules"}
}
```

**Per people:**
- what they are: lineage chain with split times, tier to each neighbour, body and senses, groups;
- where: homelands per era, migration path, refuges, landmasses and numbers;
- what their land gave them over time: a timeline of crops, animals and fuels arriving;
- neighbours over time (the contact record) and the haloclines they share;
- **what they are called**: the reputation rows by observer, with the basis (§4.7), and their own names for others;
- the bad years in their land;
- the stories the run already writes.

### culinary-dnd → procgen_world

- **The preset** (`seven_meals.toml`) mirrors `genetics.md` and the bodies (Q8). A small check script can diff the
  preset's tree and bodies against a YAML export of the culinary repo's tree, if the owner wants one.
- **Event anchors** (`[[event]]`) for the dated history the canon insists on, which the sim places and honours softly.
- **Setting requirements** (§3.1) for the world-fit score.
- **Later, a names overlay** (`names.toml`): the culinary naming skill's names keyed to highlight features, landmasses,
  mixing zones and lines. The viewer and brief would show those names in place of coordinates. procgen_world has no
  place names, and should not coin them: names are the culinary repo's domain.

### Rules the brief keeps

- **Deterministic.** Run id, tree hash and seed are in every file, and the same inputs give the same brief.
- **Mechanism words are allowed in the brief.** The culinary repo's style rule keeps real-world mechanisms off the
  page, not out of the notes.
- **Every derived line says it is derived** (`suggested`), so the culinary side knows what it may overrule.
