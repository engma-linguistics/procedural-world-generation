# Proper cultures: a proposal, round 2 (languages, names, polities, attitudes, gods)

For Daniel, 2026-11-01 (evening). Revises `proposal.md` (round 1) with your notes in `owner-notes-r1.md`. Where a note
and round 1 disagree, the note wins. Docs only; nothing is built. Round 1's sections that still stand are kept here in
trimmed form; the rest is in round 1. Sources are at the end with what was actually read (all by round 1 unless marked).

## In plain words

Nothing about the shape of the plan changes. A culture is still the unit; each gets a lect (a way of speaking), a name
stack, and, later, a ruler, attitudes and gods. What changed is what we promise and in what order.

- **Language is fuzzy and partly political.** "A language" is a stretch of mutually understandable lects, not a box. Where
  the lines fall depends on politics too: a ruling lect has prestige (your Norman example), so a conquered people's
  speech bends toward it. You will be able to click a people and see a strong-colour blob that fades with distance: "the
  language of these people", with hard cutoffs where something wholly different is spoken.
- **Time and depth.** The in-world horizon is 10 kyr and we stop tracking anything deeper. Language can begin more than
  once, at about the same time across species, but not tied to when a species became genetically modern.
- **Names.** Rivers and mountains keep their names through conquests; settlements and states change theirs.
  Outsiders lump distinct small cultures into one; the viewer will show both views.
- **War is mostly a change of owner.** A battle ends when the loser has lost perhaps 10-20% (your figure, not a sourced
  one), and the farmers just have new landlords, unless the winners are intolerant of their species or culture. The
  same tolerance decides whether a state keeps other peoples' records (your cuneiform point).
- **Writing** is shaped by what it is written on. Secret dragon writing is parked as an optional scenario.
- **Gods** are only placeholder domains in v0. The religion design comes after a talk with you; nothing real before it.
- **Dragons and kin.** Dragon kinds are several cultures each, but "Draconic" stays one language with colour dialects.
  Kobolds live under dragons and speak close to them. Dragon dominion becomes dragon realms (polities with subjects).
  Goblins mostly stay low-tech and get folded into other goblinoids' realms.
- **Order.** Languages v0 and polities v0 are output-side (a readout after the run). Polities go into the history in v1,
  together with authored nudges ("this people rises here") by re-running from a time zoom.
- **Your four questions** are answered in section 2, each with a call: de-hardcode groups (yes, in two steps), the history
  zoom (start now, needed before polities v1), the village experiment (designed, not run), Catalan and Spanish (I
  could confirm only what the distance table says, not the history).

## What changed from round 1

| # | your note | what changed | where |
|---|---|---|---|
| 1 | Skills drift and relate to cultural identity | Nothing to change; kept as a feature | 3.1 |
| 2 | Languages as dialects with an army; "language of these people" fading blob | Language line stays fuzzy MI spectrum, politics shifts it; new viewer layer | 3.1, 5 |
| 3 | War costs 10-20%, then a change of owner, unless winners intolerant | War outcome is ownership change; displacement scales with the winner's intolerance | 3.3 |
| 4 | Polities trim, not topple | Kept; no polity knobs aimed at the leader share | 3.3 |
| 5 | Religion discussion first | Gods v0 is placeholder domains only; real design waits for the discussion | 3.4 |
| 6 | Some names last forever (rivers, mountains) | Place-name persistence by feature type | 3.2 |
| 7 | Writing shaped by media | Script lineage has a medium; secret dragon writing is an optional scenario | 3.5 |
| 8 | Word forms and sounds later | Confirmed: glosses only until PW-986 | 3.2 |
| 9 | Culture is not language, nor dialect; China and Hindi-Urdu type cases | Kept; both mismatches shown on the card | 3.1 |
| 10 | Groups: relax or de-hardcode? | Answered | 2.1 |
| 11 | Small areas have distinct cultures that outsiders lump | Exonym view against endonym view, observer-side lumping | 3.2, 5 |
| 12 | Writing as a secret held by early-modern dragons | Optional scenario, later | 3.5, 8 |
| 13 | Villages: test with/without; generate on demand | Experiment designed, not run | 2.3 |
| 14 | Horizon 10 kyr; no beyond_horizon | Horizon 10 kyr; flag and per-family horizon removed | 3.1 |
| 15 | Catalan and Spanish | Answered | 2.4 |
| 16 | Chiefdom at L6/L7/L8 cells | Answered by your own follow-up; a chiefdom is a one-cell tier label | 3.3 |
| 17 | Placeholder war formulae need pulling out | Listed as a prerequisite for polities | 7 |
| 18 | Ruling lect prestige (Norman conquest) | Kept as the main polity-to-language lever | 3.1, 3.3 |
| 19 | Tolerant, record-keeping states preserve records | Record survival = writing x tolerance | 3.3, 3.5 |
| 20 | Gods v0 fine | Same | 3.4 |
| 21 | Cohesion makes one culture per dragon colour: out of date | Corrected: dragon kinds are 1-5 cultures each (D36 B) | 1, 3.6 |
| 22 | L1 culture vs language, L2 language line, L3 rate | Recorded as settled | 6 |
| 23 | Lect tree as deep as demes; language can begin more than once | Kept (try first, B if disliked); multiple independent onsets | 3.1 |
| 24 | Kobolds align to dragons | Kobold lects start from Draconic and stay close by exposure | 3.6 |
| 25 | Language onset near-simultaneous, not tied to modernity | Onset drawn per stem around a shared window | 3.1 |
| 26 | Draconic: one language across colours | Settled: one language, colour dialects | 3.6 |
| 27 | L7 morphology scalar: B | Settled: wait for real L2 share | 6 |
| 28 | N1 glosses; N2 everyone | Settled | 6 |
| 29 | P1 output-side v0, in-history v1 | Settled | 6, 7 |
| 30 | P2 nearly B: writing is the impetus for small states | Chiefdom needs writing; small states need it nearly; writing is also an impetus | 3.3 |
| 31 | P3 war scope B eventually, not v0; P4 no feelings | Settled; P4 means D31 A stands | 6 |
| 32 | P5 emergent first; authored nudges via time zoom for v1 | Settled; nudges are a v1 wish | 3.3, 8 |
| 33 | Attitudes extend reputation.py, refactor when big | Settled | 3.4 |
| 34 | Polities may come out too regular | Kept as an uncertainty; handle if it shows | 9 |
| 35 | History zoom timing | Answered | 2.2 |
| 36 | PW-1254 | Cohesion by lifespan; 2 kyr side-by-side; no merging across ways of life | 3.1, 3.6 |
| 37 | Density ladder PW-1275 | An input to polity population and a prerequisite accessor | 3.3, 7 |
| 38 | Goblins low-tech; kobolds to dragons; dragon dominion in polities | Folded into polities | 3.3, 3.6 |

---

## 1. Where we are (state, short)

Round 1's section 1 inventory still stands (peoples, demes, cultures, contacts, reputation, tech tree, settlements,
brief). Updates:

- Overlapping demes (lane 109, PW-1259) are merged. Each frame stores every people's presence; demes overlap (87% of
  peopled cells hold two or more peoples on the L6 test run); dragon kinds are one to five living cultures each
  (`docs/review/overlapping-demes/report.md`, read). Old runs need a new peoples run to get overlap.
- Your 11-01 rulings: D36 B (dragon kinds may be several cultures, PW-1268); PW-1254 (era table kept, cohesion scaled by
  lifespan, side-by-side merge after 2 kyr, no merging across ways of life); density from one shared ladder (PW-1275, todo,
  v2, effort l); goblins and kobolds as in 3.6 (`docs/wiki/decisions.md`, read).
- Ticket groups from round 1 section 1.2 are unchanged and not repeated. The ones that matter here: PW-670/1254/1268 cultures;
  PW-767/972/982-986/947 language and names; PW-756/785/1172/1258/1108 polities and war; PW-768/904/907 attitudes and
  gods; PW-908/909 history zoom; PW-1275 density.
- Standing rulings (round 1 1.3) are unchanged: emergent first, anchors later; language a joint project; light v0 passes first.

---

## 2. Your open questions, answered

### 2.1 Should groups be de-hardcoded?

**Recommendation: yes, in two steps; keep authored groups as seeds, not constraints.**

What a group is today: an authored way of life inside a people (human seafarers, steppe orcs), not cut into demes; its land
counts as its people's (round 1). Cultures already carry a way of life and two drifting skills (sea craft, open-country
herding), so most of what a group expresses already emerges per culture.

The density ladder (PW-1275) says way of life changes with tech for *part of a people*. That is the pull the other way:
if ways of life are fully per culture, a people that half-farms and half-herds has to be two cultures, which then
conflicts with PW-1254 (no merging across ways of life) and inflates the culture count.

Weighing it:
- **Per-culture way of life only** (full de-hardcode): simple, but a way-of-life transition (herders taking up farming)
  becomes a culture split and an artificial boundary. Rejected.
- **A share of a culture on each way of life** (the ladder's reading): transitions are gradual and cost no splits. A new
  culture appears only when a share persists, is separated in space, and the PW-1254 rule (no merging across ways of
  life) keeps it apart. This is the sounder mechanism.
- **Hardcoded groups**: they work, but they stop steppe orcs from *emerging* where the land says so, and a world with
  no authored group gets no equivalent.

So: step 1, land the ladder with way-of-life *shares per culture* (PW-1275 plus the shift-with-tech rule). Step 2, make
groups seed an initial share and a starting skill, then check on the dnd runs that the emergent ways of life reproduce
what the groups gave; retire the group code path once they do (no backward compatibility, per the repo rules). I have not
read the ladder's design beyond the ticket and your ruling; the shape of the shares is a judgement for the lane.

### 2.2 When does the history zoom (PW-908) need to happen?

**Call: not before v0; start it in parallel with v0 and land it before polities v1.**

- Languages v0 and polities v0 are output-side and read frames and a 100-year ledger. The 100-year step only sees
  long-lived states (round 1 section 7). That is fine for a first look, and it does not need a finer history.
- Polities v1 (war in the history) and your authored nudges ("this people rises here", "these are wiped out") both
  need a time zoom you can select a region in and re-run from a moment. PW-908 (25-year steps from each region's farming
  onset) is that. Without it, v1 polities are blind to short-lived states, and nudges have nothing to re-run.
- It is a large ticket (effort l, v2 milestone, status todo). Put it on a parallel lane now so it does not become the
  critical path for v1. This matches your hunch that it cannot wait much longer.

I have not read PW-908 beyond its header and title; the scope is the ticket's, not mine.

### 2.3 Villages: tracked or generated? An experiment design (not run)

Your ask: test with and without village tracking, always keep villages for the last ~200 years, and generate villages on
demand from town data, possibly rolling up to the city level.

**Question the experiment answers:** do tracked villages change anything that matters downstream (towns, cities, polity
seeds, cultures' sizes, minorities) beyond storage and complexity?

**Arms** (same world, same seed, L6 first, then one L7 world):
- **A: baseline.** Villages tracked every 100-year step.
- **B: no villages until the end.** No villages tracked before the last 200 years (two steps); the last 200 always include them.
- **C: on demand.** B plus a function that generates a cell's villages when asked, from the cell's town data and the
  people left over after towns: count and sizes from the same central-place rule, deterministic given the cell and step.

**Measures:**
1. Town and city counts, sizes and founding steps, compared A against B (do towns appear in the same cells and steps?).
2. Culture sizes, minorities and colonies in the settlement ledger (do they shift?).
3. Polity-relevant seeds: the largest town per culture per step, and chiefdom-hazard inputs.
4. For C: the generated villages in the last 200 years against the tracked ones (count and size distributions per cell).
5. Cost: ledger size on disk and wall time for the settlements pass, per arm.

**Pass criteria** (suggested, yours to change): B's towns and cities within the A run-to-run variation of a rerun with a
different seed; C's last-200-year villages within the same variation of the tracked ones.

**Cost:** two world runs per arm at L6 (peoples history already exists; the settlements pass is output-side), plus one
small code change: a `track_villages` switch and the on-demand generator for arm C. I have not measured the settlements
pass: the cultures pass is about 2 s a run (round 1), and I expect settlements to be seconds to minutes, but that is a
guess, so the experiment's first step is timing arm A. Size: one Sonnet lane, small; roughly the same again for the L7 repeat.
It does not touch the history. Do it before polities v0 builds on the ledger, since polities read what the ledger holds.

### 2.4 Catalan and Spanish: contact or normalisation?

You expect they did have contact but not direct communication and normalisation for a long time. What I can actually say
from what was read:

- Wichmann (2019) puts Catalan-Spanish at LDN 0.66, the highest of his example pairs (table above), well past his
  language/dialect cut-off at LDN 0.51 (round 1 full read). So they count as clearly separate languages by that
  measure, and *more* different than Cairo and Moroccan Arabic (0.58).
- In the round 1 model, a split with no contact reaches the cut-off at about 1.27 kyr. Converting 0.66 the same way
  (LDND about 0.745, s about 0.255) gives about 2.0 kyr of no-contact divergence, which I computed from Holman's
  fit and Wichmann's conversion. That is a model equivalent, not a date: contact would lower the similarity pull and
  make the real time longer.
- I did not read anything on the actual Iberian history, so I cannot confirm or refute "different enough and far
  enough away for a long time". What the model offers is the *distinction* you are drawing: contact (borrowing,
  levelling) raises surface similarity, while *normalisation under a standard or a ruling lect* raises
  **exposure**, which raises intelligibility without touching the surface similarity (section 3.1). The
  literature says exposure dominates real intelligibility (r 0.87-0.93, Gooskens & van Heuven 2020). So the sim
  can tell "close because they talked" from "close because one was the standard".
- A suggestion if you want it confirmed: a cheap targeted read of the Catalan-Spanish history, as a Haiku pass, before
  we tune the contact term on it. I would not use this pair as a calibration target until then.

---

## 3. The proposal, revised

### 3.1 Languages (Stage 0, no words, no sounds)

**Stands from round 1:** one lect per culture, born, split and ended with it; the true lect tree is deep as the demes
(300 kyr), tried first; "languages" are *derived* clusters of lects, never stored.

**Changed:**
- **Fuzzy, partly political.** A language is a stretch of lects with high mutual intelligibility (MI). The line is
  drawn at the Wichmann cut-off (s about 0.40) as the default, but the viewer's language blob and the brief both read MI,
  and politics shifts MI through exposure: a ruling lect, a written standard or a trade speech raises
  how well subjects understand it. So "the language count" may depend on politics (your L2 ruling: mostly A, with
  politics). Both mismatches are visible per culture: one language called two things because of culture, and
  distinct cultures with indistinguishable lects (your China and Hindi-Urdu cases; the China example is yours, I did not
  source it).
- **The 10 kyr horizon.** In-world scholars can see relations up to about 10 kyr back. Beyond that nothing is tracked or
  flagged: there is no `beyond_horizon` field and no per-family horizon. Families are clades whose root is younger than 10
  kyr, a constant. The true tree keeps whatever the demes give; we do not ask what the truth was beyond what scholars
  could know. Splits, merges and overlaps just happen.
- **Language can begin more than once.** Each people's stem draws its own onset of *spoken language* from a window around
  a shared date, near-simultaneous across species, and set apart from its genetic modernity (the humans' 200 kyr of language against a
  longer genetic modernity is your example, a rough figure from your note). Inside one stem, separate demes that have not
  met can have started separately too: a lect root can appear in more than one place, and contact spreads the faculty
  after (PW-947). The window's width and the lag after modernity are my judgement; I'd start with a window of a few tens of
  kyr and flag it for tuning. No pair across stems is related (`s_inherited = 0`).
- **Cultures split before languages.** `T_APART_KYR` 0.15-0.6 kyr, a no-contact split at 0.6 kyr has s about 0.62, still
  dialects (round 1). Expect many cultures per language, as on Earth. PW-1254's rules (cohesion by lifespan; no merging
  across ways of life) apply: two cultures of the same people with different ways of life stay two cultures, usually
  one language.

**The model, trimmed (stands):**
- Similarity s between two lects (ASJP-style, 1 minus LDND; Holman 2011). Divergence with no contact:
  `s(t) = s0 * r^(2t)`, `s0 = 0.92`, `r = 0.72` per kyr; each lineage has a lognormal multiplier `rate_x` (sigma about 0.3,
  the fit's 29% scatter).
- Contact pulls the surface back: `s' = s + [ -(la+lb) s + kappa c_ab (s0 - s) ] dt`. Neighbours along a chain stay close; ends
  diverge: that is the dialect continuum. Two numbers per pair: `s_inherited` (the comparative method; never pulled back)
  and `s_surface` (what a listener hears).
- MI: `mi_inherent = f(s_surface)`, a logistic curve of ours, fitted to European close relatives (no published closed
  form; Gooskens & van Heuven 2020 give only correlations). Then `mi_ab = mi_inherent + (1 - mi_inherent) E_ab`, with
  exposure E_ab (judgement) growing with b's speakers dominating shared cells, b's culture ruling a's (polities), or
  b being a written standard or trade speech. A small seeded asymmetry stands in for the Portuguese-Spanish structural residue.
- Bands in the brief: dialects (mi >= about 0.7), partly understood (0.4-0.7; 0.4 is Gooskens et al.'s workable
  threshold), separate (< 0.4).
- Pairs: touching demes now plus each lect's nearest sister; any other pair on demand.
- Light events: split, koine (sister cultures merged), shift (one culture swallowed), death, contact episodes, standard.
- **Loan strata** (forms empty): core, cultural, food (every crop or animal spread writes a loan with its route),
  substrate (from shifts). Sizes from the World Loanword Database: mean borrowed share about 25%; by field social
  and political 0.64, religion 0.49, agriculture 0.45, food and drink 0.37, kinship 0.23, body 0.17; traded goods
  (olive 0.93, wine 0.74) borrow heavily, basic states (raw 0.05, cooked 0.06) stay native.
- **Checks, not targets:** two lects about 1.3 kyr apart with no contact sit at the line; a walker people's open range
  shows a chain whose ends are below the line while neighbours stay above; similarity against travel distance looks like
  Seguy's curve with scatter; lect density follows growing season (Nettle 1998; trend, not constant).

**What politics adds (changed):** the ruling lect's prestige drives shift among a state's subjects (Abrams & Strogatz, in
3.3), and raises `E_ab` toward the ruling lect. Your Norman-conquest example is the intended picture: a court language
that does not replace the commoners' speech, but pulls a large share of its vocabulary and prestige register.

### 3.2 Names

**Stands:** the name stack per culture with forms empty, glosses only (your E/X/P taxonomy): endonym pattern and gloss,
glossonym, an exonym per neighbour that matters from the relationship, scholarly names for dead cultures, name history.
Gloss strings fix PW-1249's repeated placeholders. English glosses and forms empty: settled.

**Changed:**
- **Some names are very resilient.** Names of rivers and mountains persist through conquests and language shifts (your
  note); settlement names change more often; polity names change most. Implementation: each place name carries a
  persistence class (water and mountain features high, settlements medium, polity low) and a small chance of an
  arbitrary "sticks forever" name regardless of class. The classes and rates are my judgement; I have not read the
  toponymy literature this round. The substrate stratum from shifts is where these names are recorded.
- **Outsiders lump.** A region's several small, distinct cultures can be one exonym to a distant observer, and may look
  alike on the map, while each regards the others as distinct (your Native American example). The culture split
  already makes them distinct (local, by time apart). Lumping is *observer-side*: reputation.py already lumps by
  observer and subject (round 1); extend it so the lump size grows with distance and thin contact. Store both views
  and let the viewer switch (section 5).

### 3.3 Polities

**Stands (round 1 2.1, trimmed):**
- Tiers: band or tribe (no polity), chiefdom, state, empire (emergent: rules more than one culture or people).
- Output-side v0, using the settlement ledger, techs, cultures and circumscription (`counter._circumscribed`); in the
  history in v1.
- Chiefdoms start where a culture with chiefdoms and towns has a hazard of founding one at its largest town, scaled by
  local density, resource concentration, a contagion term and circumscription (Carneiro 2012).
- Reach: a chiefdom about half a day's travel (25-30 km on foot, Spencer 2010), a state 50-250 km soon after state
  institutions appear; writing, law, roads, horses and ships extend that, by judgement.
- Frontiers breed empires (Turchin 2009, Turchin et al. 2013); polities end with a base hazard (Arbesman 2011, exponential,
  mean about 220 years) and tiers move one step at a time (Currie et al. 2010, abstract only).
- Size checks, not caps: Taagepera 1997.

**Changed:**
- **Chiefdom and grid.** By your follow-up, a chiefdom is a one-cell thing at L7 (a third to a fifth of a cell, from the
  round 1 figure); at coarser cells it is smaller still. It is a tier label on a town and its cell, not a map shape.
- **Gate (P2, nearly B).** A chiefdom needs writing; a small state can barely do without it. I read your "impetus" point as
  a *feedback*: need for records pressures the adoption of writing, so writing's invention hazard gets a bump
  where a chiefdom or small state forms. Output-side v0 cannot feed back (the tech tree is output only, PW-946), so v0 just
  uses the gate with a slight lenience (a chiefdom without writing is allowed if its neighbours have it, because it can
  borrow it). The real feedback arrives with the history in v1.
- **War is mostly a change of owner (P3 B, not v0).** The losing side's army breaks at perhaps 10-20% losses (your
  figure; I did not source it), and the cells change hands. A cell's population does not change much: the farmers keep
  farming under a new ruler. Population loss and displacement depend on the winner's **tolerance** of the subject's
  species or culture (attitudes, 3.4): tolerant winners cost little, intolerant ones expel, enslave or exterminate a
  share. This agrees with round 1's finding that war deaths at sourced violent-death rates were 0-0.2% of any people
  (lane 101) and with your "trim, not topple" expectation, except in long sustained aggression. P3 B (war deaths and
  displacement) is eventual, not v0; v0 draws ownership only.
- **Pulling out placeholder formulae.** The in-fighting term (FEUD_CUT, SOCIAL_Q) and the state-pacification proxy G and
  hostile-frontier share F in `counter.py` are placeholders for what polities replace. A prerequisite lane lists and isolates them
  (section 7) so polities can swap them cleanly (PW-1258).
- **Languages (the Norman point).** The ruling lect's prestige drives shift among its subjects: round 1 used Abrams &
  Strogatz (2003): `dx/dt = y c x^a s - x c y^a (1-s)`, a = 1.31 +/- 0.25, status s from tier, writing and cities.
  The shift is computed per cell per 100-year step, and an elite lect can add vocabulary without displacing the commoners'
  (partial shift, a large loan stratum). Political complexity predicts a language's area (Currie & Mace 2009).
- **Tolerance and records.** A tolerant, record-keeping empire preserves other cultures' records (your cuneiform point,
  which I accept as plausible but did not source). So the survival of a conquered people's texts and scholarly names =
  writing x the state's tolerance toward them, not just writing.
- **Population from the density ladder.** A polity's population within reach reads one accessor for density. Until
  PW-1275 lands that accessor reads today's density; when the ladder lands (way of life x tech stage x land
  productivity, kind factor 0.8-1.2) it swaps in with no change to polities.
- **Dragon realms.** Dragon dominion over land belongs in polities, not in habitat learning (your ruling): a dragon
  realm is a polity whose ruling culture is a dragon culture, with subjects of other peoples (kobolds, dragonborn, others). Its
  reach is the flight range, not the tech tiers. Kobolds gravitate to dragons and occasionally form dragon,
  dragonborn and kobold realms. Open decision O4 asks how such a realm's gate works.
- **Goblins.** Goblins mostly stay low on the tech tree (short brutish lives), so they rarely form polities of their own
  and more often become subjects of other goblinoids (hobgoblins, bugbears) via the same ruling-lect shift. Their lects stay
  separate unless shifted.
- **Emergent first; authored nudges later.** Polities emerge by default. In v1 you can select in a time zoom "this
  specific people rises about now" or "these are wiped out or nearly out by a neighbour" and the sim re-runs from just
  before to contrive it. That needs the history zoom (2.2) and the polities in the history. The round 1 `[[event]]
  kind = "polity"` back-fill stays as the fallback for Seven Meals empires (PW-785).
- **Leader share (P4).** No polity knobs aimed at it; D31 A stands, report the share after polities and stop.

### 3.4 Attitudes and gods

**Attitudes (changed):** extend `reputation.py` per culture pair (settled), with a refactor when it gets big. The
vector stands: xenophobia, expansionism, assimilation vs **tolerance**, grudge (fading with intermarriage, shared faith
and shared language, slowed by a stubbornness axis). Tolerance is now explicitly an input to war outcome and record
survival (3.3). Output-side v0.

**Refactor trigger.** The lane that adds attitudes first checks how large `reputation.py` is; if the new code would make it
a grab bag, it splits reputation and attitudes into a small package in the same change. You said "refactor when
needed", so this is pre-approved; the lane reports what moved.

**Gods (changed):** v0 is placeholder domains only: a pantheon per culture of 3-7 slots with domains and no names,
following way of life and land, as in round 1. Syncretism on merges and state cults are *not* in v0. Real
design starts only after the religion discussion with you. Your starting framing, so we hold it: look at what is around a
people, what taboos there reasonably could be, the natural forces they deal with (hurricanes, tornadoes, lightning,
a sea god if they have a sea, river spirits, desert things, ancestor worship, "the gamut of what humans have done").
Nothing is built on this until we talk.

### 3.5 Writing

**Stands:** writing is a tech (tokens, proto-writing, writing floor 5.3 kyr, alphabet); effects output-side: standards,
scholarly names, literacy share, memory of conquests.

**Changed:**
- **Media shape scripts.** A script lineage carries a `medium` (clay, reed or papyrus, bark or leaf, stone or wood
  as runes, hide), read from the land and techs, not from a date. Real scripts were arguably shaped by their media
  (your note: runes, cuneiform in clay, papyrus; leaves feel "a bit more spurious but decent enough"). v0 stores only the
  medium id and the lineage; the shape effects are a later, deeper design ("way WAY in the reeds").
- **Record survival.** Writing x tolerance (3.3). A medium also changes survival of records (clay lasts, leaves rot),
  which the same field enables later.
- **Secret dragon writing (optional scenario, later).** If dragons reach behavioural modernity far earlier than others, writing could be a
  secret they keep for a very long time and that eventually leaks, against dragons simply discovering their own writing
  or being gifted it. It should be a scenario switch on the tech tree's contact gate, not a default. Not in v0 or v1.

### 3.6 Dragons, kobolds and kin

- Dragon kinds are one to five cultures each (D36 B). The round 1 line "cohesion already makes one culture per colour" is out of date.
- **"Draconic" is one language across colours** (settled), with colour dialects (MI about 0.8, round 1's lean) held together by
  dragon cohesion (0.9, a round 1 figure for dragons). One lect per dragon culture.
- **Kobolds** start from Draconic at their split (round 1 L5 A, which you approved with the note that kobolds closely
  align themselves to life under dragons). Their lect stays close to the dragons' by exposure (high `E_ab` toward the
  dragon lect when under a dragon realm) and drifts only slowly.
- **Dragon dominion** is a polity (3.3); **goblins** are subjects or low-tech (3.3).
- Dragons are sapient: nowhere do the models treat their speech as a lesser thing.

---

## 4. Data model deltas (against round 1 section 3)

Round 1's `languages.json`, `names.json`, `polities.json` sketches stand. Changes:
- `languages.json`: remove `beyond_horizon`, `horizon_kyr` becomes the constant 10; add `onset` per stem and per lect root;
  add `mi_ab` exposure source (`standard`, `ruling`, `trade`) so we can tell normalisation from contact.
- `names.json`: add `persistence_class` and `sticks` to place names; add `view: lumped|distinct` per exonym.
- `polities.json`: add `kind: dragon_realm`, `tolerance` and `record_survival` per subject culture, `war` events carry
  `losses_share` and `displaced_share`.
- `cultures.json`: gods are a placeholder list only; add `way_of_life_shares`.
- Where each lives: unchanged (output-side for everything except polities v1 which goes in the history).

---

## 5. Viewer: what you would see (changes)

Round 1 section 4 stands (Languages view with a dendrogram, culture card, globe layers, intelligibility-from-here,
polities on the slider). Additions and changes:
- **"The language of these people" layer:** select a people or culture and the map shows a strong colour at the core
  fading out with intelligibility, with hard cutoffs where something wholly different is spoken; it reads `mi_ab` so the
  blob follows politics. Particularly for the pre-empire period.
- **Dendrogram:** the 10 kyr line replaces the per-family horizon; nothing is drawn beyond it as "related".
- **Exonym view toggle:** "as they see themselves" (distinct cultures) against "as outsiders see them" (lumped).
- Card: dual mismatch notes ("same language, two names", "indistinguishable lects, one name").

---

## 6. Settled decisions (recorded)

| id | question | ruling |
|---|---|---|
| L1 | culture is a language? | no; a fuzzy spectrum of intelligibility |
| L2 | where is the language line? | mostly A, with politics shifting it |
| L3 | the rate | my choice: Holman r = 0.72, lognormal rate multiplier, no burst |
| L4 | time depth | lect tree as deep as demes, tried first; B if disliked; language may begin more than once |
| L5 | across species | kobolds start from Draconic; no inherited relatedness across peoples; shift only under polities |
| L6 | dragons | one lect per dragon culture; Draconic one language across colours |
| L7 | morphology scalar | B: wait for a real L2 share |
| N1 | gloss language | English glosses, forms empty |
| N2 | who gets names | every living culture and peoples-level rows merged in, for now |
| P1 | output-side or history | output-side v0, in-history v1 |
| P2 | tier gates | nearly B: chiefdom needs writing; writing is also an impetus |
| P3 | war scope | B eventually, not v0 |
| P4 | leader share | no strong feelings: D31 A stands |
| P5 | your empires | emergent first; authored nudges via time zoom in v1 |
| A1 | attitudes | extend reputation.py; refactor when big |
| A2 | gods | A (domains only) for v0; B and beyond from the discussion |
| D36 | dragon kinds | B: may be several cultures |
| PW-1254 | era table | kept; cohesion by lifespan; 2 kyr side by side; no merge across ways of life |

---

## 7. Lane plan for v0

All output-side; judged in the viewer on the dnd runs and one Seven Meals run; none re-runs a history. Tiers per the
model-tier memory: Opus for model physics, Sonnet moderate, Haiku mechanical.

| lane | content | needs first | tier |
|---|---|---|---|
| **Prep: placeholder formulae** | list and isolate the war, in-fighting, G and F proxies in `counter.py` (PW-1258) so polities can swap them | nothing | Sonnet |
| **Prep: PW-1254 implemented** | cohesion by lifespan, 2 kyr side-by-side merge, no merge across ways of life | your ruling (done) | Sonnet |
| **Prep: village experiment** | section 2.3, one run per arm | nothing (L6 world) | Sonnet |
| **Prep: new peoples runs** | rebuild dnd runs on overlapping demes so cultures see overlap | lane 109 (merged) | compute only |
| **1. Languages v0** | `languages.py`: lects, `s_inherited`, `s_surface`, MI both ways, families under 10 kyr, events, loans (forms empty), multiple onsets, `/api/languages`, brief block, Languages view, card, "language of these people" layer, intelligibility-from-here | PW-1254 implemented; new peoples runs; stable culture ids across recuts (to check) | Opus model, Sonnet viewer |
| **2. Names v0** (PW-972) | name stack per culture, gloss only; place-name persistence; observer-side lumping and the exonym toggle; PW-1249 fixed | lane 1 (MI and contact) | Sonnet |
| **3. Polities v0** | `polities.py`: tiers from ledger, techs, circumscription; reach by travel time; competition as ownership change; dragon realms; tolerance stub; `polities.json` and layer | placeholder-formula prep; village experiment ruled; density accessor (today's density now, PW-1275 later); PW-1254 implemented | Opus |
| **4. Owner look** | you look at 1-3; rulings on the open decisions | 1-3 | - |
| **5. Religion discussion** | no code; with you; sets gods v1 | scheduled by you | - |

Lanes 1 and 3 can run in parallel once their prep is done; lane 2 straight after lane 1. PW-908 (history zoom) starts in
parallel (2.2) but does not gate v0. Order of the output passes: demes, cultures, polities (v0), lects, names, attitudes
(v0), gods (placeholder), brief.

---

## 8. Open decisions left (only those not settled)

- **O1. De-hardcode groups** (2.1): my call is yes, in two steps (ladder with shares first, groups become seeds second).
  Needs your yes before the ladder lane's brief says so.
- **O2. History zoom timing** (2.2): my call is start now in parallel, land before polities v1. Confirm.
- **O3. Village experiment** (2.3): go or no-go, and whether the pass criteria are right.
- **O4. Dragon realms' gate:** what lets a dragon culture rule (a count of subjects, sapience and flight range only, or
  a tech-like hoard stage)? Round 1 has nothing on it; my lean is flight range plus subjects present, no tech gate.
- **O5. Religion discussion:** when. Blocks anything real on gods; v0 placeholders are unaffected.

No other round 1 decision is open.

---

## 9. Deferred (v1 and later) and uncertainties

**v1:** polities in the history with war (PW-1172, PW-1258, PW-1108); authored nudges by re-running from a time zoom;
the history zoom (PW-908/909) in place; tolerance-based displacement (P3 B); writing feedback (writing as impetus for
small states); attitudes full (PW-904, PW-768); real gods after the discussion (state cults, syncretism, ranks); writing
effects (standards, scholarly names, script lineage); groups retired once shares reproduce them.

**Later:** PW-986 language demo (real words, sounds, grammar); sound change per hop; PW-985 morphology; the secret dragon
writing scenario; writing shaped by media in detail; mixed-way-of-life culture splits at fine scale; weird worlds.

**Uncertainties, said plainly:**
- `kappa` (contact pull) has no literature value; tuned by eye on the intelligibility map. A judgement.
- The MI curve is ours, fitted to European close relatives; no evidence it transfers to dwarves.
- Exposure dominates real MI, so `mi_ab` is mostly the judgement term `E_ab`; `mi_inherent` is the sourced half.
- The onset window width, persistence classes and tolerance-to-displacement rates are judgements.
- Frames are coarse (0.5 kyr near the present; 100 years for polities); the history zoom fixes it later.
- Polities may come out too regular (Voronoi-ish); if it shows, we decide then (PW-1104).
- Unread: PW-908's and PW-1275's design beyond the tickets; the toponymy literature; the Iberian language history.

---

## 10. Literature note

Round 1's subagents read these on 2026-11-01; nothing is cited from memory. Status: full text, abstract only, or data.
Anything not listed was not read. No new sources were read in round 2.

- Holman et al. 2011, *Current Anthropology* 52(6): the dating formula, s0 0.92, r 0.72; **full**.
- Wichmann 2019, *Computational Linguistics* 45(4): language/dialect cut-off LDN 0.51, 1,075-1,635 yr; pair table
  (Indonesian-Malay 0.12, Hindi-Urdu 0.43, Russian-Belarusian 0.46, Danish-Swedish 0.49, Cairo-Moroccan Arabic 0.58,
  Catalan-Spanish 0.66); **full**.
- Gooskens 2007; Gooskens et al. 2017/18; Gooskens & van Heuven 2020: phonetic and lexical distance, 40% threshold,
  exposure r 0.87-0.93, Portuguese-Spanish asymmetry; **full**.
- Nerbonne 2010 (Seguy's curve, through a summariser); Abrams & Strogatz 2003 (a = 1.31 +/- 0.25); Nettle 1998;
  Currie & Mace 2009: **full**.
- Pagel et al. 2007 (**abstract**); Lees 1953 (**full**); Gavin et al. 2017 (**full**); Amano et al. 2014 (**abstract**).
- Haspelmath & Tadmor 2009, World Loanword Database: **data** (Tadmor's chapter unread).
- Carneiro 2012; Spencer 2010; Turchin 2009; Turchin et al. 2013 (main text); Taagepera 1997; Arbesman 2011; Grinin 2003:
  **full**. Currie et al. 2010: **abstract and summaries only**. Carneiro 1970: not read (used through 2012).
- In repo: peoples-counterpressures design (violent-death rates, K(W)); emergent-cultures design; your ethnonym taxonomy doc.

**Not verified; do not build on these without a read:** Swadesh's percentages; Pagel's per-word half-lives; the
three-generation shift pattern; Gavin's fitted constants; Turchin 2013's parameters; Currie 2010's rates; Feinman and
Flannery sizes; the Norman conquest's effect on English, the cuneiform tablet record and China's lects (your examples,
accepted as given, not sourced here); the Catalan-Spanish history; anything about river and mountain name persistence.

## Follow-ups noticed (for tickets; not filed)
- A ticket for the placeholder-formula extraction in `counter.py` if PW-1258 does not already cover it.
- A ticket for the village experiment (2.3).
- A ticket for the Catalan-Spanish history read, if you want it.
- A ticket for a `track_villages` switch and on-demand village generator, contingent on the experiment.
