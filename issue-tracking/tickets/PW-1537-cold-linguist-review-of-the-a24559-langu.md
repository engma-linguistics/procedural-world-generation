---
id: PW-1537
title: "Cold linguist review of the a24559 languages demo and sketches: findings to fix (worn-down markers, impossible sounds, sound-less words, the fable, templated texts)"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: l
impact: high
found_by: lang-design cold review (fresh agent, no lane history, 2026-11-08)
blocked_by: []
relates: [PW-986]
refs: [docs/review/language/sketches/, docs/review/language/sketches/index.md, docs/review/language/sketches/d551-elf.md, docs/review/language/sketches/d292-aarakocra.md, docs/review/language/sketches/d48-blue-dragon.md, docs/review/language/sketches/d704.2-halfling.md, docs/review/language/sketches/d261-silver-dragon.md, docs/review/language/sketches/d760-hobgoblin.md, tools/language/demo_page.py, tools/language/sketch.py, planet/language/sentences.py, planet/language/grammar.py, planet/language/rules.py, planet/language/inventory.py, planet/language/lexicon.py, planet/language/romanize.py, planet/language/texts.py, planet/language/faiths.py, docs/review/language/queue.md, docs/review/language/grammar-gaps.md, "run a24559", "demo build: lang-design scratchpad final/languages-demo-stripped.html"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: a fresh agent read the regenerated demo page (10 languages, the fable, the complexity section) and the
six sketches cold, as a historical linguist would. The sound histories, tonogenesis, kinship types, word families, the
'take X come = bring' serial verbs, polite 'you', split ergativity, avoidance speech and the per-language grammar
notes all read as real linguistics. What gives the game away is a handful of engine habits that repeat on every page:
grammatical markers that never wear down (a three-syllable 'the' on every noun), words with no vowel at all (a pronoun
that is just /h/), sounds no mouth can make (voiced ejective clicks), a fable whose "ancestor" does not match its
daughters, and the same recipe and myth told in every language. Two spellings on the page also read as offensive
English words ("naziguluni", "shitayoo'ï"). If nothing is done, the first linguist who opens the page will spot the
markers, the vowel-less words and the fable within minutes and stop trusting the rest.

Scope read: the demo (`languages-demo-stripped.html`, all 10 languages, fable, "more and less complex"), and the
index plus the elf, aarakocra and hobgoblin sketches in depth (others skimmed). Ranks: R1 hurts plausibility most.

### Must fix before publishing (not linguistics)
- [x] **Offensive-looking spellings.** Elf 7 myth, 'We do not eat wild swine': book spelling **naziguluni** ('pigs',
  bold, twice). Fable, Bagbeshaï 'in': **shitayoo'ï** (bold, twice). Borderline: elf **nige / nigeni / nigi**
  ('bird', 'birds', 'not'; myth and word list); halfling **lifukuwu** ('daughter', word families). Fix: a blocklist
  check on book spellings (substring, case-folded) in `planet/language/romanize.py`, re-rolling the spelling choice
  or picking another word for showcase texts; run it in `demo_page.py` checks.
  *Done (lang-last, ebc40791):* blocklist `planet/language/data/offensive_substrings.txt` (28 entries at first, cut to 14 slurs by the owner 11-08 (11759dde): plain swearing such as "shit" inside a word stays; case-folded,
  diacritics stripped, both registers). After the history, words whose spelling hits it are renewed at the source
  (`lexicon.offense_repair` via `history.offense_pass`: loan, derivation, fresh root; god names an epithet); given names
  are redrawn. One spelling per phoneme leaves no alternative spelling for a word, so forms with no word behind them
  (affixed, joined, grams, settlement joins) get a middle dot at a C|V boundary inside the match (`romanize.unoffend`:
  naz·i, sh·it). a24559: 439 lexicon words flagged, 439 renewed, 0 left; romanized fields of languages.json with a hit
  721 -> 0; regenerated demo (no audio) 0 hits (the only token is English 'spice' in prose). Not added as a
  `demo_page.py` check (the guard sits in `romanize_word`, so every spelling passes through it).

### Phonology
- **R1. Words and syllables with no vowel.** Human 20 2SG and 2PL pronoun is just **h** (pronoun table, sentence 4
  /h u˦vu˦pʼɲi˦/); dragonborn 44 1SG is **dʑ**, 'not' is **ʔ** (word list). Human 20 syllabifies prenasalised stops as
  their own syllable: sa˦**.ᵐp** 'sleep', na˦**.ᵐp.ᵐp**u˦f 'milk', DEF u˦nʈʂu˦**.ᵐp**. Aarakocra 8 sentences strip
  monosyllabic roots to one consonant: /lu˦**nʲ**/ 'eats' (s18), /u˦ᴖw**k͡p**/ 'the milk' (s6), /lu˦**w**/ 'older
  brother' (s8), /u˦ᴖ**w**/ 'hear' (s4, now identical to 'one' and the class prefix). Fix: a minimal-word constraint
  in `rules.py` (no deletion that leaves a lexical word or root without a vowel; a pronoun or content word is at least
  V or CV), prenasalised stops always onsets in syllabification.
  *Done (lang-last, e9fc69b9):* a sound change that would leave a lexicon word or paradigm stem with no vowel passes it
  by (`lexicon.has_nucleus`); a24559 living lexicon words with no vowel 304 -> 0, demo interlinear and joined lines 0
  (old: 'h' twice, ʘ̬w). The "sa˦.ᵐp" dot was not syllabification: `from_ipa` could not read ᵐp after a vowel, so
  `word_ipa` wrote a '.' to keep the parse; it now reads it (0 such dots in the new demo). Liturgical single-vowel words
  (Names section) are untouched.
- **R1b. Apocope applied outside its stated scope.** The aarakocra sketch says the final-vowel deletions (rules 3 and
  8) apply only "where words are made" / "inside words", but the demo's joined line applies them across words and
  phrase-finally (all the aarakocra examples above). Fix: the sentence joiner in `sentences.py` should apply only the
  rules whose scope is "across words in a phrase", or the sketch's scope column is wrong.
  *Partly done (e9fc69b9):* the cut came from `render_word` running word-level live rules over the affixed word (the
  phrase joiner is length-preserving already). `phonology.apply_word` now refuses a rule that would delete the stem's
  last vowel (an affix may still lose its vowel). Whether word-level apocope should run over affixed words at all, and
  the sketch's scope wording, are left.
- **R2. Sounds no mouth makes.** Elf 7 has voiced ejective clicks ʘ̬ʼ ǁ̬ʼ ǂ̬ʼ (chart; 'water' a˦ʘ̬ʼi˦bi˨); dragonborn
  44 has a prenasalised ejective **ᵑɡʼ** (chart; '11' ruᵑɡʼuj). An ejective is voiceless by definition. The elf sketch
  shows the cause: intervocalic voicing (4.5 kyr) hit glottalic consonants. Fix: voicing and prenasalisation rules
  exclude [ejective]; `inventory.py` rejects voiced+ejective and nasal+ejective.
  *Done (lang-last, 2e88db39):* `rules.impossible` (ejective + voice or prenasal); a rule does not act where it would
  make one (`_apply_one`, `_single`); S077, S083, S142 and the demo intervocalic voicing act on pulmonic stops only
  (tsv regenerated from `tools/language/knowledge_tables.py`); new check "no impossible segments (all lects)". Inventory
  draws from the symbol table never make one (the table has none), so `inventory.py` needed no change. a24559: words
  with an impossible segment 2669 in 81 living lects -> 0, check passes.
- **R3. Marked sounds without their plain partner.** Elf 7 lost plain ǀ ǁ ǃ ǂ (declicking, 2 kyr) yet kept the
  ejective, aspirated, voiced and nasal clicks at those places. Silver dragon 13 has no /n/ and no plain /m/ (only ŋ
  and growled m‼); blue dragon 10 has /p b/ but no /m/; dragonborn 44 has kʼ but no plain velar stop; blue dragon has
  sub-bass o˯ ʊ˯ but no plain o ʊ; silver dragon has a˯ but no plain a (so ˯ there is not contrastive and should not be
  written). Fix: a markedness check (a marked series member implies its plain partner at the same place, or a logged
  exception); declicking as a per-place change across all series; never drop every plain /m n/.
  *Partly done (lang-lane6):* series drag (`lect._series_drag`): a change that takes a marked sound's last plain partner at its place takes the marked member along (kʼ follows k > tʃ as tʃʼ, a˯ follows a > ɑ; Maddieson 1984, sound changes act on classes). a24559 living lects with a marked sound (aspirate, ejective, growl, register) lacking its plain partner 38% -> 36%; ejective orphans 192 -> 141, growl 102 -> 75 (calibration.md 'Lane 6'). Left: orphans that never had a partner (drawn so, or made by a split/borrowing), declicking per place, never dropping every plain /m n/. Prenasalised stops without a plain partner are left alone (Fijian ᵐb ⁿd).
- **R6. Growled voice is human.** "22 of its 69 sounds are outside the human voice" (blue dragon) counts harsh voice
  ‼, which human languages use (e.g. !Xóõ, Bai). It is also marked per segment in clumps (w‼ɔ‼j‼ 'dog'), where voice
  quality is a syllable or word register. Fix: count ‼ as a human phonation contrast unless the people's organs say
  otherwise; mark it once per syllable.
  *Partly done (lang-lane5):* the sketch's count leaves harsh voice out (`sketch._nonhuman`). Marking once per syllable
  is left.
  Left (lang-lane6): marking ‼ once per syllable needs voice quality as a syllable feature in the IPA writer and reader (`percepts.word_ipa` / `from_ipa` round-trip), not a display tweak.
- **R9. Sound changes that fire again and again.** Elf 7 history: "w was inserted after u and before a vowel" (S125b)
  seven times, "w was lost before u or before o" (S027) four times, e > j (S205) four times; insertion and loss
  alternate. Real changes happen once. Fix: in `rules.py`, cool a rule down for several kyr after it applies and never
  let an insert/delete pair alternate.
  *Done (lang-lane6):* the repeats were hiatus repairs (`Lect.resolve_hiatus` fires outside the re-fire memory). A repair the line already made within its re-fire wait is now recorded with cause "persistent" (the line's living rule at work on new hiatus, Chafe 1968), and the sketch lists it once ('re-applied N times'). Most repeats of one row in a living lect: median 4 -> 2, p90 13 -> 6, max 23 -> 8. Left: no general guard against an insert/delete pair alternating across steps (only within one step).

### Morphology and syntax
- **R1. Markers that never wear down.** Grammaticalised markers stay identical to, and as long as, their sources:
  human 20 DEF **u˦nʈʂu˦.ᵐp** (three syllables, = 'that') on every noun; elf 7 REL lo˦ja˦lu˦jo˦ = 'that'; silver
  dragon F= **sa˯ʃũ** (= 'woman') and 3SG **ɡɑʃwoːh=** on every verb; dwarf 1 =**eidiw** on every noun. Worst cases
  put marker and source side by side: hobgoblin 19 s9 'that COP' = **ɡbiːnaf ɡbiːnaf**; blue dragon 10 s11/s13 'ACC
  take' = **ʁa‼ ʁa‼**. Fix: in `grammar.py`, each bonding step (free > clitic > affix) shortens the form (lose
  syllables, tone, length; clitics at most one syllable, affixes usually one segment or CV), and a marker that is
  still identical to its source cannot stand next to it.
  *Partly done (lane 4 PW-1570 and lang-lane5):* binding clips to one syllable (clitic) and the first syllable (affix)
  (lane 4); free and clitic grams now also wear like function words (`grammar.GRAM_WEAR` 0.001 x frequency, the
  owner's PW-1570 rate; never onto a word's or another gram's form). Free grams 3.35 -> 3.23 segments, grams identical
  to their source 34.8% -> 32.5% (calibration.md 'Lane 5'). Left: a marker identical to its source can stand beside it
  (Mandarin 把 'take' > object marker is
  the real-world case; no adjacency veto added).
  *Done (lang-lane6):* a free marker still identical to the word beside it is said once, glossed for both (`sentences.haplology`: the repeated-morph constraint, Stemberger 1981; English the boys'), 21 notes over the living lects' pages.
- **R4. Noun classes that are not systems.** Dwarf 1: "genders by animacy" with one class that every noun takes
  (one class is not a gender). Blue dragon: default class 4 'de' is never on dog, fish or house in the sentences.
  Halfling 39 calls its class prefixes "classifiers" though they show concord. The same semantic menu recurs ("languages,
  ways and tools" from 'tongue', which then holds dog, fish, milk, thunder; "lands, qualities and abstractions" from
  'name'). Aarakocra 8 concord is patchy: ANIM lu- on 'see' and 'sleep' but not on 'give' (s11), 'take'/'come' (s13)
  or 'big' in s19. Silver dragon M class marker kɑa˯ never appears. Fix: require two or more classes for a gender
  label; make `sentences.py` apply concord to every target the grammar names; give animals a living-being class.
  *Partly done (lang-lane6):* a gender label needs two or more distinct live class markers (`grammar._class_state`, Corbett 1991): gender 'none' 39% -> 66% of living lects (WALS 30A 56%); 75 lects keep one bound class marker on every noun with no gender label. Left: concord on every target, a living-being class for animals, the recurring class menus, 'classifiers' wording for concord systems.
- **R5. Contradictions inside one page.** Aarakocra: COMP "from the relativizer marker" but relatives have "no
  relativizer". Dragonborn (an ergative showcase): the transitive subject lacks ERG in s18 ('says') and s19 (topic
  sentence). Dwarf 1: accusative "marks only animate objects" but the recipe marks 'it' (the vine) ei-sãsu ACC-3SG.
  "Cumulative exponence" is claimed for plain sequences (dragonborn PST.2SG niu = ni + u; hobgoblin HAB.1PL kuːh =
  kuː + h). "As Welsh cath, y gath" is cited for glide formation (dragonborn s20) and final truncation (Bagbeshaï
  tʃutʃu > tʃutʃ), neither of which is an initial mutation. Fix: checks in `sentences.py`/`checks.py` for each.
  *Done (lang-lane6):* ERG on the sayer and on the subject of a topic sentence (an ergative clause stays transitive: Basque esan); DOM note says pronouns are marked too (top of the animacy scale, Hindi ko); a source gram since lost reads 'from a relativizer marker the language has since lost'; cumulative exponence blurs the join (`grammar._blur_join`) and a portmanteau still equal to its two parts is not called one; the stem-change parallel follows where the stem changed (Welsh for initial changes, German Tag/Tage for final, French petit for loss).
- **R7. One menu of sources for every language.** Negation from 'nothing' (elf, blue dragon, silver dragon, drow,
  hobgoblin, dwarf, dragonborn), Q and TOP from 'if', past from 'yesterday', 1PL from 'person', every 'exceed'
  comparison "with the verb for 'climb' (as Yoruba ju, Thai kwaa)". Each is attested; all of them in every language is
  not. Fix: weight sources per family and spread them (negation from 'not'-verbs, 'refuse', emphatic doubling; past
  from 'finish', 'leave'; Q from 'or', 'not').
  *Done (lang-lane6):* each family leans among the sources of a function (`grammar.path_lean`: lognormal sigma 1 from a hash of the proto id and the path, normalised per function so recruitment rates hold).

### Lexicon and semantics
- **R5. Homophony on the commonest items.** Human 20: u˦ = one, who, COP, LOC, AGT; u˦f = three, ACC, TOP, OBLG.
  Dragonborn: u = man, see, ERG, 2SG, IMP, DIST. Halfling: i = DEF, TOP, GEN, 2SG; 'who' ilifu = 'the woman'; 'what'
  hu = 1PL.EXCL. Hobgoblin: hiː = 3SG, HORT, 'eat'. Dwarf: 'fifteen' ujo̞ = 'woman'. Aarakocra: 'river' = 'big'.
  'Mother' = 'woman' in aarakocra, halfling and hobgoblin. Fix: the homophony veto in `lexicon.py` should weigh
  frequency (core list and live grams) and the mother/woman colexification should be rare.
  *Partly done (lang-lane5):* a word with the form of a live particle or clitic of another source is renewed as an
  accidental homophone (`lexicon._renewal_boost` via `Lexicon.gram_forms`), new words and wear keep off those forms
  (`_clashes`, `wear`); a shift leaving two frequent words (class <= 3) on one form is taken with chance
  (families / 12)^2 (`FREQ_SHIFT_CLASS`). Readings in calibration.md 'Lane 5'. Left: closed-class mergers by sound
  change (I ~ ONE ~ THREE in ~5% of lects) and gram-gram homophony of one-syllable clitics.
- **R8. Numeral notes that the forms do not support.** "11 = 10 + 1 ('ten' and 'one')" is printed for forms holding
  neither (hobgoblin iæ, dwarf mãwɛwnḭv, aarakocra u˦ᴖwʔa˦l, silver dragon kujie). The sketches' numeral line says
  "nine = 'ten + one'" and "eight = 'four + two'" (elf, aarakocra; wrong arithmetic for 9 and 8). Blue dragon:
  "'many' past twenty" yet 30 and 100 exist, and 'forty' = 'man'. Fix: print the composition only when the parts are
  recognisable in the form, otherwise "built as 10 + 1, now opaque"; label subtraction and multiplication correctly
  (`tools/language/sketch.py` numeral note, `sentences.py` numeral section).
  *Done (lang-lane6):* the composition prints only when both parts can be heard in the form (`sentences._part_heard`), else 'built as 10 + 1, now worn past recognition'; the sketch labels the arithmetic (9 = 10 − 1, 8 = 4 × 2) and 'now opaque'; restricted counting reads 'many for a hundred and more'.
- **R10. Odd derivation paths and avoidance words.** Hobgoblin 'arm or hand' family holds bird, bee, ant, fly, chick;
  'see' holds 'downstream'. Aarakocra avoidance words called "paraphrase" are single syllables, and one word o˨n
  replaces 'eat', 'see', 'sit' and 'sleep' (Dyirbal Jalnguy merges into general terms, not unrelated verbs); 'head' and
  'foot' share k͡pe˨t. Dragon languages have 3% speaker-felt families against 8-23% elsewhere.
  *Partly done (lang-lane6):* avoidance words are general terms within a field (eat/drink, see/hear, go/come, sit/sleep, hand/foot share one), never one form across fields (`lexsys.AVOID_GROUPS`). Left: CLICS derivation families ('arm or hand' > bird, bee), dragon felt-family share.

### Texts
- **R2. The fable's ancestor does not fit its daughters.** The intro says the triton ancestor (about 6 kyr ago) still
  shares many words with the four daughters, but the daughters agree with each other against it: 'say' *xiŋŋiʔo vs
  lɨnɨu, lɨ̞nʔɨ̞, liniʔi, jäwnäʔo; 'see' *vaxaŋaːɡ vs nuhɨʔu, nuːʔo̞, nufuʔu, nähuʔo; 'bird' *iːj vs ʒɨ, sɨ̞, nufuba,
  ɐːɨ; 'fish', 'come', 'give', 'good' likewise. A shared innovation absent from the shown ancestor means the ancestor
  line is not the 6 kyr state. This is the page's Schleicher showcase. Fix: build the ancestor line from the lexicon
  as it stood at the split, and check that each daughter word descends from it or is marked replaced or borrowed.
  *Not done (lang-last ran out of the one pass).* Diagnosis on the a24559 run before these fixes: the ancestor p320 is
  an arrival proto (born = died 6.0 kyr) with ONE child, d767, a copy at 6.0. All four daughters descend through d767
  (d767 itself and three later buds of it), so their real common ancestor is d767 at its earliest bud, after it had
  replaced 'say', 'see', 'bird' etc.: shared innovations of the d767 line, not a wrong p320. No dead lect in 2-9 kyr
  splits into 2+ living lines at its death (lects bud and live on), and the snapshots keep only the core-100 forms and
  grams, not a full lect, so the fable cannot be told in the split-time state from the output. Fix needs the engine to
  keep a full copy of a lect at a chosen bud (the fable's MRCA), or `texts.pick_family` to pick the MRCA lect and a
  bud time and the pass to store that state. Needs a pass.
  *Done (lang-lane6, PW-1592):* the ancestor is the daughters' common lect as it stood at its first bud 2-9 kyr ago (`History.splits`, `output.splits_json`, `texts.pick_family`), daughters on 2+ branches; `texts.fable_descent` checks it in `demo_page.py`. a24559: d767 at 4.5 kyr and four daughters, 0 problems.
- **R3. Every recipe and myth is the same text.** All ten recipes run "Take X. Grind it with a stone. Put it in the
  pot. Cook it at the fire. Eat it with salt. It is good." (grinding cane, alliums, nightshade fruit, bananas; goat
  meat swaps in "cut with a knife"). All five myths forbid wild swine (elf, drow, aarakocra, silver dragon,
  dragonborn, three different faiths); all use "X holds Y. X gives us water/rain.
  X, hear us!". Fix: recipe steps from the cuisine data (boil, roast, ferment, dry, pound, soak), a few sentence frames
  per step, and myth lines drawn from the faith's own data or left out when thin (`texts.py`).
  *Done (lang-lane5):* recipes follow the food (`texts.WAYS`: grain, pulse, tuber, fruit, green, sweet, meat, fish;
  2-3 ways each, picked by a hash of the lect id; spices and drink plants never the food). a24559 living lects: 6 ->
  52 distinct step sequences, commonest 30% -> 19%; staple alliums 189 lects -> 0 (maize, wheat, millet lead). Myths:
  the gods' verb and the invocation vary per faith (`MYTH_HOLD`, `INVOCATION`; one wording per faith in all its
  languages): 'hear us' 116 of 116 -> 37 / 25 / 24 / 22 over four invocations. The swine taboo itself is faith data
  (77 of 108 faiths): draft-faith-taboos-mostly-swine.
- **R6. Myths of the wrong people.** Elf 7 and drow 2 show "the sky faith of the earliest hill giants of the east of
  Ratal" with no word on how elves came by it; the faith is "founded 300 kyr ago" (silver dragons: 250 kyr), 15 times
  older than any proto-language here (20 kyr). Fix: say "a faith the elves took from the hill giants" and cap founding
  dates at the founding people's own language age, or explain the gap.
  *Partly done (lang-lane5):* the myth title says when the people took the faith over ('..., which the elf people
  took over', `sketch.myth_of`). Founding dates: draft-faith-taboos-mostly-swine.
- **R9. Translations add words.** "the carrion birds" / "the wild swine" for plain bird-PL / pig-PL (elf, drow,
  aarakocra, silver, dragonborn myths). Fix: gloss what is there ('birds', 'pigs'), or coin the compound.
  *Done (lang-lane5):* the English says 'pigs', 'birds'; the label goes in the note (`texts._plural_en`).

### Names
- Mostly convincing (sentence names like Yegǀuwizi 'the child came', matronymics, settlement etymologies). Two slips:
  liturgical hill giant 'sky-father' is a˦, the same as 'we' a˦ ("a a rramiiwi"), and most liturgy words are a single
  vowel (u 'soul', i 'sing', i 'give'); internal ids leak into word families as **god:31 (name)**, **god:255**,
  **god:289** (elf, aarakocra, halfling, silver dragon). Fix: print the god's name; apply the minimal-word rule to
  liturgical languages too.
  *Partly done (lang-lane5):* word families print "a god's name" for name:god:N (`sketch.cname`).

### Presentation
- **R4. Slash brackets on phonetic output.** The joined line under each sentence is written /…/ but carries
  allophones (elf [d] for /t/, [ʘ̬] for /ʘ/) and phrase sandhi. Use [ ] or label it "as said".
  *Done (lang-lane5):* [ ] with an 'as said' tooltip (`demo_page.py`).
- **R7. Book spellings that cannot be read.** Dragons spell ˯ as "mh" and ‼ as "rh" in every word:
  samhshunwanmhch'samhshun, thurhdeïkhomhwïnerhḷ; human 20 untsumpnampmpufuf. Elf mixes click letters with px for ʘ
  (pxagǂhabu). Fix: at most one non-human mark per word in the book spelling; clicks all letters or all digraphs.
  *Partly done (lang-lane6):* one non-human mark a word in the book (after its first marked run). Left: the bilabial click letter (draft-language-bilabial-click-spelling, a taste call).
- **R10. Small slips.** "ago ago" in sketch faith and liturgy lines (`sketch.py` adds "ago" after `kyr()`, which
  already ends in "ago"); "Berlin & Kay stage other"; the index says inclusive/exclusive 'we' cannot be shown, but every
  page shows it; dragonborn lists the ˯ mark though no live word has it; "most English-like" hobgoblin has onsets ʃb-,
  hb- that the score ignores; the complexity section prints a stray "Marks beyond the standard IPA" line after the
  tortle and kobold entries.
  *Done (lang-lane5):* 'ago ago', the B&K 'other' stage wording, the false inclusive/exclusive caveat, the stray marks
  line (complexity cards key only the marks they show). Left: ˯ listed with no live word; the English-likeness score
  ignoring onsets.

### Side effect of the last fixes (lang-last full pass, 2026-11-08): overused nʲ
The single full pass after the three fixes (scratchpad `last/a24559`) fails "overused segments (all living lects)":
nʲ in 62 of 618 living lects (10.03%, 5.2x PHOIBLE) against the 10% floor; the run before had it in 35 of 620 (5.7%).
Spread over kobold, kenku, human, aarakocra, dragonborn (not one family). Likely the minimal word: CV words with i that
apocope used to cut now keep the i, so S221 (n > nʲ before i) finds more contexts and its coda exit S234 fewer. Not
confirmed (one pass only). Candidate: S221 weight 0.4 -> 0.3, or exit S233 also before i in long words; needs a pass.
All other checks pass except the scholars' horizon (accepted).

### Acceptance
- [x] no lexical word, pronoun or root without a vowel in any demo or sketch line; no nucleus-less syllable (demo
  checked; sketches not regenerated)
- [x] no voiced or prenasalised ejective in any inventory of the run
- [ ] a marked series member without its plain partner is either gone or listed as a logged exception
- [x] markers that bind shorten; no marker sits next to its identical source
- [x] fable daughters descend from the shown ancestor (a check in `demo_page.py`)
- [x] recipe and myth texts differ in more than the nouns across the ten demo languages
- [x] numeral composition notes only where the parts are visible; arithmetic labels right
- [x] offensive-substring check passes on all book spellings in the demo
- [ ] a second cold read of the regenerated demo finds none of R1-R3 again

## Updates
- 2026-11-09: Lane 6 (lang-lane6) did R1 haplology, R2 (PW-1592), R5, R7 source lean, R8, R9 persistent repairs, and parts of R3, R4, R7 spelling, R10; 'Done (lang-lane6)' notes per item.
- 2026-11-09: Lane 5 (1612db8f) did R1 gram wear, R3 recipes by food and myth wording per faith, R5 homophones and frequent-pair damping, R6/R9 myth notes, small slips; R2 fable ancestor -> PW-1592; faith data -> PW-1591. Remaining items listed in the ticket's lane-5 notes.
- 2026-11-08: Created from inbox draft draft-language-cold-review.md (found by lang-design cold review (fresh agent, no lane history, 2026-11-08)).
