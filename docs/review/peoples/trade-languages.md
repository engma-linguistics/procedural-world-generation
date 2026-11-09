# Trade languages and multilingual peoples (PW-1526, lane 230)

## In plain words

Daniel, 11-08: "Since you're working on trade goods, we need trade languages. And multilingual people."

Each culture now has, for every era of the trade window (the last 12.5 kyr, 0.5 kyr apart), a short list of the other tongues some of its
people speak, with roughly what share of its people speak each and why:

- **a neighbour's tongue**: people living mixed with or beside a neighbour learn its tongue, the bigger neighbour's more;
- **a ruler's tongue**: a subject people's townsfolk speak their rulers' tongue in the first era of rule, and more of the country each
  further era;
- **a host's tongue**: merchants a trading culture keeps in another culture's town (a merchant quarter) speak the town's tongue;
- **a trade language**: where trading towns of two or more cultures sit on one long-haul route network, one tongue serves them all. It is
  the ruling state's tongue when one state and its subject peoples carry most of the network's trade (as Aramaic and Greek did); else the
  busiest trading culture's tongue if it carries a clear majority; else a **pidgin** built mostly on the busiest culture's words (as the
  Mediterranean Lingua Franca was). The trading towns' people speak it, and a quarter of the people living along its routes. Once
  established it holds on after the state or trade that made it fades, until a much stronger tongue takes over; a pidgin gives way to the
  first real trade language that qualifies;
- **a liturgy**: when the run has languages.json, the clergy of every culture holding a faith speak that faith's frozen sacred register
  (the language pass fixes the canon; this ledger only says who learns it).

The language pass (planet/language/) owns the languages; this ledger owns who speaks which. A tongue is named by the culture whose tongue
it is, plus that culture's living lect id and language id at that era when the run has languages.json. It is a read-out (D63 A): nothing
in the history or the language pass changes.

Where to read it: `GET /api/tongues?run=<id>` (per era: counts and the trade languages), `&culture=<id>` (one culture's rows per era),
`&ago=<kyr>` (one era whole). Code: `planet/lineages/tongues.py`; tests: `tests/test_tongues.py`.

## Sources

All pages fetched on 2026-11-08. T§1, T§2 (Lingua franca, Pidgin) and T§3 (Language shift) quotes were fetched and checked by the lane
itself; the others were fetched and quoted by a research helper in the lane (the quotes are as its fetch tool relayed them). Wikipedia
only: no scholarly source was reached in this pass, so every number below that is not a quote is marked JUDGEMENT.

**T§1 Bilingualism is common, and borders make it.** Multilingualism, https://en.wikipedia.org/wiki/Multilingualism:
"This phenomenon can also occur in border regions with many cross-border contacts." "it was necessary to know two or more languages for
trade or any other dealings outside one's town or village." "It is believed that multilingual speakers outnumber monolingual speakers in
the world's population."

**T§2 Trade languages and pidgins.**
- Lingua franca, https://en.wikipedia.org/wiki/Lingua_franca: they arise "sometimes for commercial reasons (so-called "trade languages"
  facilitated trade)", and from administration and empire ("Akkadian remained the common language of a large part of Western Asia from
  several earlier empires", "until it was supplanted in this role by Aramaic"). "Sogdian was used to facilitate trade between those who
  spoke different languages along the Silk Road." The Mediterranean Lingua Franca was "used especially by traders in the Mediterranean
  Basin from the 11th to the 19th centuries."
- Pidgin, https://en.wikipedia.org/wiki/Pidgin: a pidgin "develops between two or more groups of people that do not have a language in
  common"; "It is most commonly employed in situations such as trade"; "A pidgin is not the native language of any singular speech
  community, but can be learned as a second language"; its vocabulary is "often drawn from several languages", "with one (the
  superstrate) being clearly dominant over the others".
- Mediterranean Lingua Franca, https://en.wikipedia.org/wiki/Mediterranean_Lingua_Franca: "the first to use it were the Genoese and
  Venetian trading colonies"; "Because it was a pidgin, Mediterranean Lingua Franca had a very small vocabulary."
- Imperial Aramaic, https://en.wikipedia.org/wiki/Imperial_Aramaic: the Achaemenids made it "the imperial standard", the "vehicle for
  written communication between the different regions of the vast empire"; before that it was "the lingua franca of the Neo-Assyrian
  Empire".
- Chinook Jargon, https://en.wikipedia.org/wiki/Chinook_Jargon: "a language originating as a pidgin trade language in the Pacific
  Northwest", "widely used by natives, trappers, traders, employees of the Hudson's Bay Company, missionaries, and pioneers"; it faded as
  English was learnt (the helper's paraphrase).
- Malay trade and creole languages, https://en.wikipedia.org/wiki/Malay_trade_and_creole_languages: Bazaar Malay, a trade pidgin of the
  archipelago's ports (paraphrase; no quote kept).

**T§3 Subjects learn the ruler's tongue, towns and government first, over generations.**
- Language shift, https://en.wikipedia.org/wiki/Language_shift: "Assimilation is the process whereby a speech-community becomes bilingual
  and gradually shifts allegiance to the second language." "Often, languages that are perceived to be of higher-status stabilize or spread
  at the expense of other languages"; "An example is the shift from Gaulish to Latin during the time of the Roman Empire." Breton: "60% of
  children received Breton from their parents in the 1920s and only 6% in the 1980s" (two to three generations).
- Language death, https://en.wikipedia.org/wiki/Language_death: shift "happens when language shift begins in a high-level environment such
  as the government"; moving to towns drives it (paraphrase).
- Vulgar Latin, https://en.wikipedia.org/wiki/Vulgar_Latin: "the spread of spoken or 'Vulgar Latin' became more and more intensive over
  time in major provinces."
- Koine Greek, https://en.wikipedia.org/wiki/Koine_Greek: "In its eastern provinces, the Roman Empire communicated almost exclusively in
  Greek."

**T§4 Lingua francas outlive what made them.** Koine Greek (same page) "served as the lingua franca of much of the Mediterranean region and
the Middle East during the following centuries" after Alexander; Latin "was the common language of communication, science, and academia
in Europe until well into the 18th century" (Lingua franca page), long after the Western Empire.

**T§5 Liturgical languages.** Liturgical language, https://en.wikipedia.org/wiki/Liturgical_language: Sumerian was "cultivated and
preserved in Assyria and Babylon long after its extinction as an everyday language"; "The training of clergy in the use of a sacred
language becomes an important cultural investment"; "Theravada Buddhism uses Pali as its main liturgical language."

## Diagnosis: what was there, what was missing

- **The language pass** (planet/language/) makes the lects and languages per deme, with its own proxy of bilingualism
  (`inputs.Run.l2_share`: other peoples on a deme's cells plus mixed cities) that wears grammar and draws loans, its own shift triggers
  (incursions, takeovers, mixed cities, swamping, long trade contact) and, since 11-08, liturgical registers (`faiths.py`: a faith's seat
  lect frozen when it first has temples; `languages.json` `faiths[fid].liturgy`). It records no second tongues per culture and no trade
  languages.
- **Trade** (trade_flow.py, trade_routes.py) gives per era the long-haul route network (layers bit 1), its trading towns (hubs with
  `trading`), their throughput (`strength`) and merchant quarters (`quarters`: the merchant culture and its share of the town's trade).
- **Polities** (polities.py) give per century who rules which cultures; `trade_flow._polity_state` already turns that into ruler culture
  -> subject cultures at an era.
- **Faiths** (gods doc, `faithmap.faith_of_culture`) give each culture's faith at an era.

So every input exists; what was missing is the ledger that joins them. No new physics is needed and none of the history is touched.

## Design

One era (`tongues.era_rows`), in order:

1. **Neighbours.** `frame_inputs` measures each culture's contact with each other culture: per cell it lives in, weighted by the cell's
   heads, the other culture's part of the culture-cells in the cell and its ring of neighbours. A culture's speakers of the neighbour's
   tongue = NEIGHBOUR_UPTAKE x contact x 2 x the neighbour's part of the two peoples' heads (T§1, T§3). At most TOP_PER_KIND neighbours
   are listed (the strongest).
2. **Rulers.** Per (ruler, subject) pair, the subject's townsfolk share in the first era of rule, plus RULE_SPREAD of its country folk per
   further era, capped at RULE_MAX (T§3). The whole people shifting is the language pass's job (its takeover and incursion shifts), not
   this ledger's, so the rate is slow on purpose.
3. **Hosts.** A merchant quarter of culture x in a town of culture h: QUARTER_FOLK of the town's people are x's merchants, and they speak
   h's tongue (T§2: trading colonies).
4. **Trade languages.** The long-haul route stretches are joined into networks; a network with trading towns of two or more cultures (merchant
   quarters count) gets one trade language (`tongues.pick`):
   - a ruling culture whose own trade plus its foreign subjects' trade on the network is at least RULE_TOWNS of the network's trade, whose own
     people carry at least RULE_OWN of it (lane 231: a state's tongue needs its own merchants, not just its subjects), and which rules at least one other people trading there: its tongue (Aramaic, Greek; T§2, T§3);
   - else the busiest trading culture, when it carries at least LF_LEAD (Sogdian; T§2);
   - else a pidgin whose main word-giver is the busiest trader (T§2: a pidgin between groups without a common language, its superstrate
     the dominant one);
   - an established lingua franca counts as carrying at least HELD of the trade, plus HELD_GROWTH for every era it has served (up to HELD_MAX), and is replaced only by a tongue carrying INERTIA times
     that (T§4); a pidgin gives way to any real trade language that qualifies (Chinook Jargon; T§2).
   A network inherits last era's trade language from the network it shares most trading towns with (ids and `since_kyr` carry over).
   Speakers: the trading towns' people, the merchant quarters, and ALONG of the people living on the route cells. The trade language's own
   people are native speakers and get no row; a pidgin is everyone's second tongue.
5. **Liturgy.** A culture holding a faith whose liturgy the language pass fixed, at or after the canon's date: LITURGY_SHARE (the clergy)
   speak the canon lect. The seat culture's own clergy count it once the canon is LITURGY_GAP_KYR old (T§5: Latin beside Romance).

A row is kept when at least MIN_SHARE of the culture's people speak it, or (for the tongues of trade: host, trade language, pidgin) at
least MIN_HEADS of them, a town's worth, since only traders and townsfolk speak those. A tongue of the same language id as the culture's
own (languages.json) is no second tongue.

| constant | value | basis |
|---|---|---|
| MIN_SHARE | 0.02 | JUDGEMENT: reporting floor |
| MIN_HEADS | 1000 | the settlement ledger's smallest town; JUDGEMENT to use it |
| NEIGHBOUR_UPTAKE | 0.5 | JUDGEMENT; the asymmetry (bigger neighbour learnt more) from T§3 |
| TOP_PER_KIND | 4 | JUDGEMENT: a readable list (per kind: neighbours, rulers, trade languages...) |
| RULE_SPREAD | 0.25 per era | JUDGEMENT; towns first and growing with time from T§3 |
| RULE_MAX | 0.9 | JUDGEMENT |
| LF_LEAD, RULE_TOWNS | 0.5 | JUDGEMENT: a majority; "clearly dominant" from T§2 |
| HELD, INERTIA | 0.25, 2.0 | JUDGEMENT; persistence itself from T§4 |
| HELD_GROWTH, HELD_MAX | 0.05 per era, 0.45 | JUDGEMENT (lane 231): persistence building with use from T§4, no rate in the source |
| RULE_OWN | 0.2 | JUDGEMENT (lane 231): "a large share" of the network's trade carried by the state's own people; T§2 gives no number |
| ALONG | 0.25 | JUDGEMENT; "used especially by traders" from T§2 |
| QUARTER_FOLK | 0.05 | JUDGEMENT: Curtin's institution (review1.md section 5) has no size |
| LITURGY_SHARE | 0.01 | JUDGEMENT: an order of size for a clergy |
| LITURGY_GAP_KYR | 1.0 | JUDGEMENT |

### Output

`tongues.derive` returns `{"format": "procgen-tongues/1", "columns": ["tongue", "kind", "share", "lect", "language", "via"], "frames": [{"frame",
"ago_kyr", "cultures": {culture: [row]}, "trade_languages": [{"id", "kind", "tongue", "lect", "language", "source", "since_kyr", "cultures",
"weight", "towns", "places", "speakers"}]}], ...}`. `via` is the trade language's id for trade rows, the town for host rows, `faith <id>`
for liturgy rows. The server keeps it in `.godscache` like the exchange doc (`server.tongues_doc`).

## Results on the stored runs

The six stored L7 peoples runs, read-only (4 dnd: 0141d1, 3e0eb4, a24559, a2b637; 2 Seven Meals: 07c755, 3c1caf, measured only, never
tuned), 26 eras each (12.5 kyr ago to now). Only a24559 has languages.json, so only it has liturgy rows and lect/language ids. There is no
earlier version of this ledger, so the baseline for "how much" is the source's own: multilingual speakers are believed to outnumber
monolinguals in today's world (T§1). Harness: the lane's scratch scripts `measure.py` (inputs, with the exchange doc made in memory and
nothing written under the data root) and `stats.py`.

| run (tree) | rows per era: neighbour / ruler / trade language / pidgin / host / liturgy | heads speaking another tongue (lower-upper) | trade languages per era (min-mean-max) | network-eras by source: rule / trade / held / pidgin | eras a trade language lasts (mean, max) |
|---|---|---|---|---|---|
| 0141d1 (dnd) | 917 / 106 / 56 / 0.7 / 3.6 / - | 68-85% | 0-13.5-40 | 331 / 11 / 8 / 2 | 1.4, 10 |
| 3e0eb4 (dnd) | 879 / 117 / 78 / 4.1 / 6.3 / - | 74-89% | 0-25.4-61 | 598 / 17 / 35 / 11 | 1.6, 10 |
| a24559 (dnd) | 1008 / 90 / 62 / 1.6 / 0.2 / 104 | 58-74% | 0-14.6-45 | 329 / 21 / 22 / 7 | 1.3, 5 |
| a2b637 (dnd) | 879 / 121 / 77 / 4.2 / 5.9 / - | 74-89% | 0-24.8-60 | 585 / 13 / 33 / 13 | 1.5, 8 |
| 07c755 (Seven Meals) | 803 / 134 / 95 / 1.0 / 6.2 / - | 68-86% | 0-24.5-54 | 541 / 35 / 56 / 4 | 1.5, 11 |
| 3c1caf (Seven Meals) | 1059 / 108 / 105 / 9.2 / 0.9 / - | 61-79% | 0-19.7-36 | 385 / 70 / 29 / 27 | 1.3, 6 |

(Heads: the lower bound counts each culture's most spoken other tongue, the upper bound the sum of its rows capped at all its people.)

What it shows:
- Nearly every culture (99.8-100%) has at least one other tongue, mostly a neighbour's; 58-89% of all heads speak a second tongue. That
  sits above the source's "more than half" for today's world, which fits a world of small peoples living mixed (T§1: in early times "it
  was necessary to know two or more languages for trade or any other dealings outside one's town or village").
- No share exceeds RULE_MAX (0.9); no culture lists more than 16 tongues in an era (4 per kind).
- Trade languages appear only once long-haul networks join towns of two cultures: none at 12.5 kyr ago, tens per era by the last few kyr.
- **Most trade languages are a ruling state's tongue** (85-90% of network-eras on the dnd runs, 75-85% on Seven Meals); a dominant
  trader's tongue, a held-over tongue and a pidgin share the rest. That is the run's polities speaking: most long-haul networks with two or
  more trading cultures lie inside a state that rules some of them.
- **Trade languages turn over fast**: a trade language lasts 1.3-1.6 eras (650-800 years) on average, up to 5-11 eras (2.5-5.5 kyr). The
  networks themselves re-form between eras (they are traced afresh each era from the routes), and a new state with a majority of a network's
  trade replaces the incumbent at once. (This table is the first version; lane 231 made lingua francas stickier and gave the
  state's own merchants a say, see the section below.)
- Cost: the ledger itself takes 0.1-0.4 s per run; reading its inputs (the goods ledger's cell pairs per era, polities, gods) about 20 s to
  2 min; the exchange doc it reads costs 1.5-5 min at L7 the first time (cached by the server).

### Lane 231: stickier lingua francas and trade over rule (PW-1563, rulings B and C together)

Same six runs, same inputs, read-only; the baseline is main on 2026-11-08 (the table above). Lifetime = eras one trade-language id lasts;
mix = network-eras by source (rule / trade / held / pidgin).

| run | lifetime before (mean, max) | after | mix before | mix after |
|---|---|---|---|---|
| 0141d1 | 1.38, 10 | 1.68, 8 | 331 / 11 / 8 / 2 | 152 / 144 / 40 / 16 |
| 3e0eb4 | 1.55, 10 | 1.96, 15 | 598 / 17 / 35 / 11 | 319 / 222 / 94 / 26 |
| a24559 | 1.28, 5 | 1.56, 11 | 329 / 21 / 22 / 7 | 214 / 97 / 50 / 18 |
| a2b637 | 1.50, 8 | 1.84, 13 | 585 / 13 / 33 / 13 | 301 / 229 / 90 / 24 |
| 07c755 (Seven Meals, measured only) | 1.48, 11 | 1.93, 17 | 541 / 35 / 56 / 4 | 274 / 220 / 115 / 27 |
| 3c1caf (Seven Meals, measured only) | 1.33, 6 | 1.76, 14 | 385 / 70 / 29 / 27 | 158 / 222 / 84 / 47 |

- B (HELD grows 0.05 per era served, to HELD_MAX 0.45) alone moves little: lifetime 1.28-1.56 mean, and more "held" network-eras.
- C (RULE_OWN 0.2: the state's own people must carry a fifth of the network's trade) does most of the work: a state that rules the roads
  but whose merchants are other peoples no longer takes the language, so rule falls from 75-94% to 31-56% of network-eras and a
  busiest-trader's tongue takes 28-53% (before 4-19%). Lifetimes rise by about 0.3-0.45 eras, still short of the centuries-long lingua francas of
  T§4: the ids also end when a network re-forms between eras with no shared trading town, which neither rule touches.
- Constants are JUDGEMENT (no source gives numbers); RULE_OWN 0.1 gives the same lifetimes with rule at 32-60%.

## Robustness

The lane 77 stress suite (`tools/peoples_robust.py`) runs the peoples history on many trees and keeps only its numbers; it saves no run, so
it has no settlements, polities or trade window for this ledger to read. This ledger is a read-out after the run (D63 A) and changes nothing
in the history, so the suite's numbers are the same on this branch as on main by construction, and running its ~145 runs (~3.5 h) would
measure nothing of this change. It was not run. What stands in for it:
- the six stored runs above on two trees (dnd at seeds 11 and 12, Seven Meals at seed 11), with and without languages.json, with
  polities and gods: no crash, every share in range;
- `tests/test_tongues.py`: each rule on hand-made eras; a run with no polities, gods or routes (the six-cell line); and 20 random eras
  (random people, borders, towns, quarters, rulers and routes, carried era to era) that must keep every row in range and of a known kind;
- the code takes every input as optional: no polities (nobody rules), no gods doc (no liturgy), no languages.json (tongues named by
  culture only), no long-haul routes (no trade language), dragons and other tribute-takers (their kobold merchants count as the realm's
  traders, as trade_routes does).
A suite that saves its runs' read-outs would be the way to judge read-outs on any tree; that is the suite's own scope, not drafted here.

## Limits and follow-ups

- The language pass does not read this ledger: its own l2_share and loan donors know nothing of trade languages or rulers' tongues (draft
  `draft-language-pass-reads-tongues-ledger.md`).
- Viewer (lane 231): a "Speaks also" table on the Lineages brief's culture card (`viewer/lineages.html`, `drawTongues`) and the era's trade
  languages in the Trade routes legend (`viewer/globe/trade.js`, `tongueLegend`); screenshots in `docs/review/viewer/culture_speaks_also.png`,
  `trade_languages_legend.png`, `trade_routes_with_languages.png`. The legend lists, it does not colour the networks on the map.
- A pidgin that lasts does not creolise or expand here (Tok Pisin, Swahili-like growth): the pidgin is a row, not a lect; the language pass
  would have to make it a lect for it to have words. Noted here, not drafted.
- A ruler's tongue is not kept after rule ends, except as a trade language (T§4 covers lingua francas, not every former subject).
- Sources are Wikipedia only; a scholarly pass on language contact and lingua francas would give the judgement constants better footing.
- Place labels of a trade language's towns are the settlement ledger's coarse region names ("the west of Simath" three times), so a
  network's towns can read alike.
