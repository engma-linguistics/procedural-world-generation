# Regional pantheons, round 1 (scout 220: PW-1521)

## In plain words

**What Daniel asked (11-09).** Could a larger, D&D-style pantheon evolve? Not one where the winners' religion takes over, but one where, in
*some regions*, a pantheon builds up over time. Each kind of people (dwarves, elves, orcs) keeps or gains gods of its own, and the big
domains (war, sea, harvest, death) get gods of their own that several peoples worship. D&D is only the inspiration. Nothing here quotes it.

**Short answer: yes. History did exactly this, and the model already has most of the ingredients.** Real pantheons grew mostly by
*matching*, not replacing. A Greek in Egypt or a Roman in Gaul looked at a foreign god and said "that is our Zeus" or "that is our
Mercury". Both names survived side by side, as at Bath, where the goddess was "Sulis Minerva". Big pantheons formed where three things met:
- **polytheists**, who can add gods without betraying the old ones;
- **mixed trade cities and multi-people empires**, where peoples worship side by side;
- **rulers who let local cults be.**

They broke down where an exclusive faith (one true god, the rest false) took hold.

**What today's worlds already show** (run 0141d1, rebuilt read-only on current main):
- 145 of 279 living cultures are tolerant (tolerance at least 0.5) and hold a faith that does not seek converts.
- 83 cultures hold a town or city where at least two peoples each make up a tenth or more.
- If each such town is treated as a meeting place for its own culture and its tolerant neighbours of other peoples, **47 candidate
  pantheons** appear. A typical one has 7 cultures, 5 peoples and 4 shared domain gods. Example: around the dragonborn towns of Luki, the
  dragonborn, human and leonin fire, sky and sea gods already match.
- Two things go wrong if the model just took that as it stands:
  1. **The candidates cover 58% of the land.** If touching meeting places were allowed to join, they would chain into one region of 114
     cultures and 25 peoples, covering 70% of the land. That is the worldwide pantheon Daniel does not want. A pantheon needs a limited
     reach.
  2. **Looking alike is cheap.** Almost every people has a hunt, sky or forest god, so "same top domain" matches nearly everything. Of 245
     people-in-region entries, only 77 have a god that matches no other people's. A people's *own* god therefore cannot be "the one that
     happened not to match". It has to be its patron, kept on purpose.
- On run 3e0eb4, Daniel's missionary dwarf faith is held by 192 of 267 cultures. Only 36 cultures are open, and **only 5 small pantheons**
  appear (15% of the land). That is the historical pattern: an exclusive, missionary faith shuts accretion down.

**The design in one paragraph.** Keep every culture's beings as they are. Add a regional record, a **pantheon**, centred on a *hub*: a
lasting mixed town or city, or the capital of a state that rules several peoples. When tolerant, non-missionary cultures of different
peoples near a hub have worshipped alike gods side by side long enough, the gods are *identified*: each keeps its own name and people but
gains a shared seat, for example "the sea god of the Luki pantheon (dragonborn, leonin, human)". Each people's **patron** (its leading
god) is never identified away: it stays that people's own, as Marduk stayed Babylon's. A people can also **adopt** a foreign god that
has no match among its own, as Rome took in Cybele and the Mediterranean ports took in Isis. Seats fall apart again when the hub empties,
when the region turns intolerant, or when an exclusive faith takes over. Everything is a chance in time, like the conversions, so it
happens in some regions and not in others.

## 1. How real pantheons accreted: a sourced short review

Sources were all fetched for this lane on 2026-11-08, listed at the end. Wikipedia is used where nothing better could be fetched;
Britannica returned 403.

**Matching foreign gods to one's own (interpretatio graeca / romana).**
- Herodotus equated Egyptian gods with Greek ones: Amon with Zeus, Osiris with Dionysus, Ptah with Hephaestus. He did the same for
  Scythian gods, for example Tabiti with Hestia [IG].
- Romans gave Celtic gods Latin names: Lugus became Mercury, Nodens became Mars, and Sulis became Minerva (the Bath temple's paired name
  "Sulis Minerva") [IG].
- Tacitus wrote that the Germans' chief god was Mercury. He described the twin gods of one grove as "Castor and Pollux" in Roman terms [IR].
- One Gallic god could have more than one Roman equivalent, depending on the source [IR]. Matching was loose and local.
- The Interpretatio romana page frames this as polytheism treating gods as translatable across peoples, citing Assmann's "intercultural
  translation". It notes that Greco-Roman religion was not dogmatic, so one god could carry several functions [IR].
- **Lesson for the model:** both the local and the shared identity survive, and matching runs on function (domain). That is the
  `identified` link, not a fuse.

**Absorbing foreign gods whole (Hellenistic and Roman).**
- Serapis was promoted by Ptolemy I in the 3rd century BC, built on Osiris and the Apis bull. The aim was a god both Greek and Egyptian
  subjects could revere. The page notes that the story of a decreed invention is partly legend [SER].
- Isis spread across the Mediterranean after 323 BC. Her Greek worshippers credited her with Greek goddesses' powers, including
  protecting ships at sea [ISIS].
- On the free port of Delos (from 166 BC) stood a temple of Isis, Serapis and Anubis. Merchants from Berytus honoured their own gods in
  paired Greek forms (Baal as Poseidon, Astarte as Aphrodite) [DEL].
- Mithras's Roman mysteries were carried by soldiers, merchants, customs officials and freedmen. The cult was strongest on the Rhine and
  Danube frontiers and in Italy [MITH].
- Cybele (Magna Mater) was brought to Rome in 204 BC, during the Second Punic War, on a Sibylline oracle confirmed by Delphi. Rome then
  fenced the cult in: citizens were barred from its rites, and its priests were denied citizenship [CYB].
- Rome also *invited* enemy gods across. Evocatio called a besieged city's guardian god to Rome with the promise of a better cult: Juno
  Regina of Veii in 396 BC (the Etruscan Uni), and reportedly the goddess of Carthage in 146 BC [EVO].
- **Lesson for the model:** a god can be **adopted** whole where there is no match. The carriers are ports, soldiers and empires.

**City gods rising with their cities (Mesopotamia).**
- The oldest god list (Fara, Early Dynastic) holds about 466 readable names. The longest, *An = Anum* (about 1300-1100 BCE), holds over
  2,000 names, arranged by family and court. Its last tablet is an appendix of Marduk's names [ANUM].
- Enlil was the god of Nippur. Rulers from across Sumer went there for legitimacy, and Babylonian kings still did after Marduk superseded
  him [ENL].
- Marduk rose with Babylon, from Hammurabi (1792-1750 BCE) on. By the creation epic many gods were "aspects" of him, and Kassite kings had
  to "take the hands of Marduk" to rule [MAR].
- From about 1300 BC Assyria's god Ashur was **syncretised** with Enlil, not set up as his replacement [ENL].
- **Lesson for the model:** the hub's own patron rises with the hub. The pantheon's head is the patron of whoever holds the strongest
  city. A god list is a roster that grows by adding, and the old names stay on as epithets.

**Hindu traditions absorbing local gods.**
- Sanskritization (Srinivas) is the adoption of high-caste customs by lower castes and tribal groups, including "Sanskritising" their
  pantheon. Local deities come to be identified with gods of the Sanskrit tradition. Critics note that the Sanskrit rites are often
  *added* to the local ones, not put in their place [SANS].
- Village goddesses (gramadevata) are often held to be forms of Lakshmi or Parvati, yet many keep separate worship. Few were fully
  absorbed [GRAM].
- The Tamil hill god Murugan "coalesced" with Skanda. He became the son of Shiva and Parvati, and his two consorts preserve both
  traditions [KART].
- The Buddha became an avatar of Vishnu by the Gupta period. In some regional lists, local gods (Vithoba, Jagannath) take that slot
  [AVA].
- Jagannath's tribal origin is a contested theory, so it is not used here [JAG].
- **Lesson for the model:** absorption is *regional* and *partial*. The local god keeps its own cult and gains a place in the larger
  roster.

**Japan: kami and buddhas combined (shinbutsu-shūgō).**
- Shrine-temple complexes (jingū-ji) were founded from the 8th century. At Usa, Hachiman was already combined with Maitreya in the 7th
  century [SHIN].
- Hachiman was declared a protector of the dharma, then a bodhisattva ("Hachiman Daibosatsu"), with a shrine at Tōdai-ji [HONJI].
- *Honji suijaku* held that buddhas appear locally as kami: Amaterasu as Dainichi, and each major shrine's kami with its buddha original
  by the late Heian period [EOS].
- From the late Kamakura period an inverted view made the kami the originals [EOS, HONJI].
- There was resistance at the start: the Mononobe objected to worshipping a "foreign kami" [SHIN].
- In 1868 the Meiji order forcibly separated shrines from temples, and many jingū-ji were destroyed. In daily practice the two stayed
  intertwined [SHIN].
- **Lesson for the model:** identification runs both ways, can last a thousand years, and can be **undone by a state's decree**.

**What favoured accretion over replacement.**
- **Polytheism versus exclusive monotheism.** Rome tolerated foreign worship that honoured the gods "according to ancestral custom". It
  persecuted Christians because their exclusive faith refused to sacrifice to the gods and the emperor [PERS].
- Rome did suppress cults it found threatening, such as the Bacchic cult [PERS]. Tolerance was policy, not indifference.
- Akhenaten's one-god Aten cult defaced Amun's temples. It was reversed within a generation of his death [ATEN]. Exclusivity imposed on
  a polytheist land did not hold.
- **Empire.** Cyrus's cylinder says he returned gods' images to their sanctuaries and restored their temples. Historians read this partly
  as conventional Mesopotamian royal propaganda (Kuhrt calls it "a literary device"). They also read it as a policy that ruled through
  existing local units because cooperation was cheaper than coercion. There is no archaeological evidence for temple rebuilding under
  Cyrus [CYR]. Ptolemy's Serapis is the deliberate version: a god made for a two-people state [SER].
- **Trade cities.** Delos's mix of Egyptian, Phoenician, Italian, Samaritan and Jewish cults sat in a free port [DEL]. Isis spread as a
  sea-protector [ISIS], and Mithras with soldiers and merchants [MITH].
- **Lesson for the model:** the hub conditions are a mixed city and/or a multi-people ruler, tolerant cultures, and faiths that do not
  seek converts. The breakers are an exclusive (missionary) faith, intolerance, or a ruler's decree.

## 2. What gods.py has today (and what it lacks)

- Every culture has its own beings, 3 to 15 of them, each with a weight over 20 domains, a devotion and an individuation.
- A daughter culture copies its parent's beings (`parent` links them). A merge **fuses** alike beings (FUSE_COS 0.6) or carries them in.
  A conversion copies the converter's leading god into the convert, beside its old beings.
- That already covers syncretism by merger and by conversion. Both are *replacement-flavoured*: one culture's record ends, or one faith
  wins.
- There is **no link between beings of different cultures that stay separate**, so the model cannot say "the tritons' sea god is the
  dragonborn's sea god". There is also **no regional unit** between "a culture" and "a faith". Faiths are spread over cultures by
  conversion, never pooled by place.
- Peoples have no god of their own above their cultures. A people's beings are scattered copies, related only through `parent`.

## 3. Prototype read-out (docs/review/culture/faiths/pantheon1/pantheons.py)

What the script does:
- It replays the gods read-only (`gods.inputs` + `polities.derive` + `gods.replay`, the same as `gods.derive`) and looks at the present.
- **Open culture:** tolerance at least 0.5 (attitudes.py) and a faith that is not missionary.
- **Meeting place:** a town or city whose `who` has two peoples each at 10% or more, placed in the culture holding its cell.
- **Region:** each open meeting-place culture plus its open neighbours of *other* peoples (one hop).
- **Gods counted:** a being with individuation at least 0.45 (temples, CONVERT_MIN). Spirits stay bound to their land.
- **Domain god candidate:** beings of 2 or more peoples with the same top domain and cos 0.6 or more to their mean.
- Every threshold is a read-out JUDGEMENT.

| run | living cultures | open | with a mixed town | regions | cultures in any | land in any | median region: cultures / peoples / domain gods |
|---|---|---|---|---|---|---|---|
| 0141d1 | 279 | 145 | 83 | 47 | 119 | 58% | 7 / 5 / 4 |
| 0141d1, touching hubs joined (`union`) | 279 | 145 | 83 | 3 | 124 | 70% | one region of 114 cultures, 25 peoples, 15 domain gods |
| 3e0eb4 | 267 | 36 (192 hold the missionary dwarf faith) | 83 | 5 | 21 | 15% | 5 / 4 / 3 |

Domain gods across the 0141d1 regions, by domain:

| domain | hunt | forest | sky | sea | fire | storm | river | rain | death | flood | mountain | desert | hearth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| regions | 47 | 33 | 31 | 29 | 23 | 18 | 16 | 10 | 5 | 4 | 3 | 2 | 1 |

War, harvest, smithing and ancestors never lead a temple-grade god in these worlds. Their beings stay under 0.45 individuation, because
only a culture's leading being reaches high tiers. So a D&D-like "god of war" or "god of the harvest" will not appear until the human
domains can lead. That is a salience question for gods.py, separate from pantheons (open question 5 below).

Examples (0141d1, read-out text abridged):
- *Around the human towns of the west of Thotal (orc 82%, human 17%):* 19 cultures, 11 peoples. Shared gods of fire (human, orc, tortle,
  triton), sea (the same four), sky (six peoples) and hunt (eight peoples). The orcs' own: a god of sun and sky.
- *Around the dragonborn towns of Luki (leonin and dragonborn, about half each):* 18 cultures. Shared fire, sky and sea gods of
  dragonborn, human and leonin. The leonin's own: a god of sun and sky. The lizardfolk's own: a god of rain and flood.
- *3e0eb4, around the bronze-dragon-held leonin city north-east of Trojanel:* 17 cultures, 9 peoples, 9 shared domain gods. It is one
  of only five pockets left open beside the missionary dwarf faith.

What the prototype shows:
1. The ingredients are common enough that pantheons will form. On a polytheist world they are too common: the gate has to be *lasting*
   mixing at a real hub, not any town with a 10% minority today. The rate has to be slow enough that only some regions get there.
2. **Reach must be bounded.** One hop already reaches 58% of the land through overlap. Joining touching hubs makes one 70% region. The
   design caps reach by distance from the hub and keeps regions separate.
3. **Matching by domain is nearly free.** The "people's own god" has to be chosen (the patron), not left over.
4. **A missionary faith suppresses pantheons** without any special rule: 15% of the land on 3e0eb4 against 58% on 0141d1.

Data note: 0141d1 rebuilt on current main has 0 missionary faiths and 53 conversions. Its stored `gods.json` has 17 missionary
conversions. The stored file predates a later change on main. That is outside this ticket and does not affect the read-out.

## 4. Design: regional pantheons in gods.py

The design adds mechanisms, not scripted outcomes. It is a read-out like the rest of gods.py: the history is untouched, and it uses its
own random stream, so the majority faiths and conversions stay identical, as in the minorities lane.

**Definitions.**
- **A people's own god (patron):** the being lineage (the root through `parent` over founded, born, split and converted copies) that
  leads (`high`) in the largest share of that people's cultures, by land. It is read per people and per region. A patron is never
  identified into a domain god; it keeps its seat as "the god of the orcs". A people can gain a new patron when another lineage comes
  to lead most of its land (a lineage that rises by conversion counts). That is how a people "gains" a god of its own, through the
  existing conversion and individuation rules.
- **A domain god:** a regional record, a *seat*, with a domain (the shared top domain) and a list of **member beings**, at most one per
  culture. Every member keeps its own id, label, culture and future name. The seat holds the cross-people identity, so it is "Sulis
  Minerva", not a fuse. Its individuation is the highest of its members'. Its head (the "Marduk" of the pantheon) is the hub-holder's
  member.
- **A pantheon:** a hub, its reach, its seats, and the patrons of the peoples inside it.

**Hubs.**
- A culture becomes a hub when it holds a town or city where two or more peoples have each held at least HUB_MIX for HUB_KYR (the trade
  city; the settlements series would need its `who` over time, today only "now").
- A culture also becomes a hub when it is the ruling culture of a state, empire or dragon realm whose subjects include another people
  (`rule_table`; the empire case: Serapis, the Achaemenids).
- A hub must itself be open.
- Its reach is the open cultures with land within PANTHEON_KM of the hub's centre, via the `where` unit vectors already in `inputs()`.
  This is a distance cap, not graph hops, so regions stay regional. Overlapping hubs keep separate pantheons. When one hub falls inside
  another's reach, the smaller joins the larger. This is the city-god hierarchy: Nippur's Enlil under Babylon's Marduk.

**Identification (the main event).**
- Inside a pantheon, for each domain, a culture's best being on that domain (individuation at least CONVERT_MIN, not its patron) and a
  seat's members (or another people's such being) are **identified** as a chance in time.
- The rate is 1/TAU_IDENT × openness(a) × openness(b) × the mixing at the hub. It is faster when both cultures are under one ruler.
- On identification the being joins the seat, or founds a new seat with the other being. Nothing else changes: weights, devotion and
  individuation are untouched.
- Openness is `religious_tolerance(c) × (0 if the culture's faith is missionary else 1)`.

**Adoption (gaining a foreign god).**
- An open culture in reach with **no** being on a seat's domain may adopt the seat as a new being: a copy of the head member's weights,
  how = "adopted", parent = the head.
- It does so at a slower rate, TAU_ADOPT. This is how a people takes in Isis or Cybele.
- The new being then drifts with its new land like any other. A sea god adopted inland becomes a river god in time, and leaves the seat
  when its cosine to the seat falls below FUSE_COS.

**Undoing (regional, reversible).**
- A member leaves its seat when its culture stops being open: intolerance, or a missionary faith taking over (the Meiji separation, the
  Christian refusal).
- A member also leaves when its culture leaves the reach, or when it drifts off the seat's domain.
- A seat with members of only one people left dissolves. A pantheon whose hub stops qualifying stays for TAU_HUB_MEM and then dissolves.
  An exclusive ruler's decree is the fast path: Akhenaten.
- The beings themselves are never deleted by this.

**Constants to choose (all JUDGEMENT; sourced scales where possible).**
- TAU_IDENT: centuries to a millennium. Hachiman went from a combined kami (7th century) to a bodhisattva (8th century) in a century or
  so [SHIN, HONJI].
- TAU_ADOPT: a few times slower than TAU_IDENT.
- HUB_KYR: about 0.3-0.5 kyr. That is enough that a passing conquest or a brief market does not seed a pantheon.
- PANTHEON_KM: about 800-1500 km, a kingdom's span.
- TOL_OPEN: around the median tolerance (0.5 today).

The target is a calibration bar, not a script. On a polytheist D&D world, perhaps 2-8 pantheons with 2-8 domain gods each, covering
under a third of the land. On a world dominated by a missionary faith, few or none. That would be checked over 3+ runs with re-rolled
draws.

**What it reads from lane 219 (PW-1520, religious tolerance, being built now).**
- It reads one number per culture per frame, `religious_tolerance(c)` in 0..1, and optionally a flag saying the faith is *exclusive*
  (refuses other gods), as distinct from *missionary*.
- Until that lands, the pantheon code falls back to `Attitudes.tolerance(c)` and the existing `Faith.missionary`.
- It never imports lane 219's internals. The interface is one accessor on `Pantheons` that lane 219 can override.
- If PW-1520 makes an exclusive faith something other than a missionary one, the openness formula should use exclusivity. The
  sources above tie Rome's clash to the refusal of other gods [PERS], not to the seeking of converts.

**Output (gods.json, procgen-gods/3).**
- A top-level `pantheons` list: id, hub culture, hub kind (city / empire), centre, reach (cultures), founded and ended years, head
  seat, `seats: [{domain, members: [being ids], founded_kyr, events}]`, `patrons: {people: lineage being id}`, and `events`
  (identified, adopted, left, dissolved).
- Each being doc gains `seat`: the seat id or null.
- Per people: `patron` (the lineage, with where it leads).

**What the viewer would show.**
- **Religion → Pantheons**, a new subtab beside Minorities. One card per pantheon: the hub town and the years it has stood. Then a
  **roster table**: rows are the domain gods (sea, sky, fire, ... with the head first), columns are the peoples present, and each cell
  is that people's member being, with its own label or name. Under it sits a row of the **patrons**: "the orcs' own: god of sun and
  sky". This is the D&D picture, a shared domain roster beside each people's own gods, but it is the *regional* one.
- **Map:** an outline of each pantheon's reach over the faith map. When names exist, a hover shows "sea god: X to the tritons, Y to the
  dragonborn" (PW-986 names, paired like "Sulis Minerva").
- **Being card / Cultures tab:** "identified with the sea god of the Luki pantheon (also worshipped by leonin, humans)", or "adopted
  from the Luki pantheon".
- **Timeline:** events when a pantheon forms, when a god is adopted, and when a seat breaks up ("the Luki pantheon split when the
  dragonborn took the missionary faith").

**Cost.** The mechanism runs inside `replay()`, so it adds seconds and needs no re-run of `inputs()`. One part is not cheap: hubs need
the mixed towns' peoples *over time*. Today settlements.json keeps `who` only "now". Either settlements stores a coarse `who` series, or
the hub test uses the culture-level contact edges over time (already in `inputs()` frames) as a stand-in: cultures of two peoples
sharing many edges for HUB_KYR, plus at least one town.

## 5. Open questions for Daniel

These are in the inbox draft `draft-regional-pantheons-design-choices.md`, as options with a lean:
1. matching or fusing;
2. how far a pantheon reaches;
3. how common pantheons should be;
4. what an exclusive faith does to them;
5. whether war and harvest gods should be able to lead.

## Reproduce

```bash
PYTHONPATH=. PLANET_DATA=<owner data root> NUMBA_NUM_THREADS=4 uv run python docs/review/culture/faiths/pantheon1/pantheons.py 0141d1 <scratch dir>
PYTHONPATH=. PLANET_DATA=<owner data root> NUMBA_NUM_THREADS=4 uv run python docs/review/culture/faiths/pantheon1/pantheons.py 0141d1 <scratch dir> union
PYTHONPATH=. PLANET_DATA=<owner data root> NUMBA_NUM_THREADS=4 uv run python docs/review/culture/faiths/pantheon1/pantheons.py 3e0eb4 <scratch dir>
```

Each run takes about 2 minutes. It reads the run and writes only `<run>_pantheons.json` into the scratch dir. Rebuilt on main c2e54f2b,
2026-11-08.

## Sources (all fetched 2026-11-08)

- [IG] Interpretatio graeca, https://en.wikipedia.org/wiki/Interpretatio_graeca
- [IR] Interpretatio romana, https://en.wikipedia.org/wiki/Interpretatio_romana
- [SER] Serapis, https://en.wikipedia.org/wiki/Serapis
- [ISIS] Isis (Hellenistic and Roman period), https://en.wikipedia.org/wiki/Isis
- [MITH] Mithraism, https://en.wikipedia.org/wiki/Mithraism
- [CYB] Cybele, https://en.wikipedia.org/wiki/Cybele
- [EVO] Evocatio, https://en.wikipedia.org/wiki/Evocatio
- [DEL] Delos, https://en.wikipedia.org/wiki/Delos
- [ANUM] An = Anum (page title "An = Anum"), https://en.wikipedia.org/wiki/An_=_Anum
- [ENL] Enlil, https://en.wikipedia.org/wiki/Enlil
- [MAR] Marduk, World History Encyclopedia, https://www.worldhistory.org/Marduk/ (cites Jeremy Black on Marduk's rise with Babylon)
- [SANS] Sanskritization, https://en.wikipedia.org/wiki/Sanskritization
- [GRAM] Gramadevata, https://en.wikipedia.org/wiki/Gramadevata
- [KART] Kartikeya, https://en.wikipedia.org/wiki/Kartikeya
- [AVA] Avatars of Vishnu, https://en.wikipedia.org/wiki/Avatars_of_Vishnu
- [JAG] Jagannath, https://en.wikipedia.org/wiki/Jagannath (its tribal-origin theory is contested; not used)
- [SHIN] Shinbutsu-shūgō, https://en.wikipedia.org/wiki/Shinbutsu-sh%C5%ABg%C5%8D
- [HONJI] Honji suijaku, https://en.wikipedia.org/wiki/Honji_suijaku
- [EOS] Encyclopedia of Shinto (Kokugakuin), "Honjisuijakusetsu", https://d-museum.kokugakuin.ac.jp/eos/detail/?id=8529
- [PERS] Persecution of Christians in the Roman Empire, https://en.wikipedia.org/wiki/Persecution_of_Christians_in_the_Roman_Empire
- [ATEN] Atenism, https://en.wikipedia.org/wiki/Atenism
- [CYR] Cyrus Cylinder, https://en.wikipedia.org/wiki/Cyrus_Cylinder

Not verified, and not relied on:
- Assmann's "Mosaic distinction" itself. Its Wikipedia page 404'd and the Heidelberg PDF was blocked. Only the Interpretatio romana
  page's summary of his "translation" idea is used.
- The "fifty names of Marduk" detail.
- Nanna as Ur's patron (Britannica 403).
- Rodney Stark on this question.
- The long Wikipedia pages were read only to about their first 100k characters.
