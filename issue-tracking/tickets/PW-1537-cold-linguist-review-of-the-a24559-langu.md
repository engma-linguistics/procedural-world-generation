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
updated: 2026-11-08
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
- **R6. Growled voice is human.** "22 of its 69 sounds are outside the human voice" (blue dragon) counts harsh voice
  ‼, which human languages use (e.g. !Xóõ, Bai). It is also marked per segment in clumps (w‼ɔ‼j‼ 'dog'), where voice
  quality is a syllable or word register. Fix: count ‼ as a human phonation contrast unless the people's organs say
  otherwise; mark it once per syllable.
- **R9. Sound changes that fire again and again.** Elf 7 history: "w was inserted after u and before a vowel" (S125b)
  seven times, "w was lost before u or before o" (S027) four times, e > j (S205) four times; insertion and loss
  alternate. Real changes happen once. Fix: in `rules.py`, cool a rule down for several kyr after it applies and never
  let an insert/delete pair alternate.

### Morphology and syntax
- **R1. Markers that never wear down.** Grammaticalised markers stay identical to, and as long as, their sources:
  human 20 DEF **u˦nʈʂu˦.ᵐp** (three syllables, = 'that') on every noun; elf 7 REL lo˦ja˦lu˦jo˦ = 'that'; silver
  dragon F= **sa˯ʃũ** (= 'woman') and 3SG **ɡɑʃwoːh=** on every verb; dwarf 1 =**eidiw** on every noun. Worst cases
  put marker and source side by side: hobgoblin 19 s9 'that COP' = **ɡbiːnaf ɡbiːnaf**; blue dragon 10 s11/s13 'ACC
  take' = **ʁa‼ ʁa‼**. Fix: in `grammar.py`, each bonding step (free > clitic > affix) shortens the form (lose
  syllables, tone, length; clitics at most one syllable, affixes usually one segment or CV), and a marker that is
  still identical to its source cannot stand next to it.
- **R4. Noun classes that are not systems.** Dwarf 1: "genders by animacy" with one class that every noun takes
  (one class is not a gender). Blue dragon: default class 4 'de' is never on dog, fish or house in the sentences.
  Halfling 39 calls its class prefixes "classifiers" though they show concord. The same semantic menu recurs ("languages,
  ways and tools" from 'tongue', which then holds dog, fish, milk, thunder; "lands, qualities and abstractions" from
  'name'). Aarakocra 8 concord is patchy: ANIM lu- on 'see' and 'sleep' but not on 'give' (s11), 'take'/'come' (s13)
  or 'big' in s19. Silver dragon M class marker kɑa˯ never appears. Fix: require two or more classes for a gender
  label; make `sentences.py` apply concord to every target the grammar names; give animals a living-being class.
- **R5. Contradictions inside one page.** Aarakocra: COMP "from the relativizer marker" but relatives have "no
  relativizer". Dragonborn (an ergative showcase): the transitive subject lacks ERG in s18 ('says') and s19 (topic
  sentence). Dwarf 1: accusative "marks only animate objects" but the recipe marks 'it' (the vine) ei-sãsu ACC-3SG.
  "Cumulative exponence" is claimed for plain sequences (dragonborn PST.2SG niu = ni + u; hobgoblin HAB.1PL kuːh =
  kuː + h). "As Welsh cath, y gath" is cited for glide formation (dragonborn s20) and final truncation (Bagbeshaï
  tʃutʃu > tʃutʃ), neither of which is an initial mutation. Fix: checks in `sentences.py`/`checks.py` for each.
- **R7. One menu of sources for every language.** Negation from 'nothing' (elf, blue dragon, silver dragon, drow,
  hobgoblin, dwarf, dragonborn), Q and TOP from 'if', past from 'yesterday', 1PL from 'person', every 'exceed'
  comparison "with the verb for 'climb' (as Yoruba ju, Thai kwaa)". Each is attested; all of them in every language is
  not. Fix: weight sources per family and spread them (negation from 'not'-verbs, 'refuse', emphatic doubling; past
  from 'finish', 'leave'; Q from 'or', 'not').

### Lexicon and semantics
- **R5. Homophony on the commonest items.** Human 20: u˦ = one, who, COP, LOC, AGT; u˦f = three, ACC, TOP, OBLG.
  Dragonborn: u = man, see, ERG, 2SG, IMP, DIST. Halfling: i = DEF, TOP, GEN, 2SG; 'who' ilifu = 'the woman'; 'what'
  hu = 1PL.EXCL. Hobgoblin: hiː = 3SG, HORT, 'eat'. Dwarf: 'fifteen' ujo̞ = 'woman'. Aarakocra: 'river' = 'big'.
  'Mother' = 'woman' in aarakocra, halfling and hobgoblin. Fix: the homophony veto in `lexicon.py` should weigh
  frequency (core list and live grams) and the mother/woman colexification should be rare.
- **R8. Numeral notes that the forms do not support.** "11 = 10 + 1 ('ten' and 'one')" is printed for forms holding
  neither (hobgoblin iæ, dwarf mãwɛwnḭv, aarakocra u˦ᴖwʔa˦l, silver dragon kujie). The sketches' numeral line says
  "nine = 'ten + one'" and "eight = 'four + two'" (elf, aarakocra; wrong arithmetic for 9 and 8). Blue dragon:
  "'many' past twenty" yet 30 and 100 exist, and 'forty' = 'man'. Fix: print the composition only when the parts are
  recognisable in the form, otherwise "built as 10 + 1, now opaque"; label subtraction and multiplication correctly
  (`tools/language/sketch.py` numeral note, `sentences.py` numeral section).
- **R10. Odd derivation paths and avoidance words.** Hobgoblin 'arm or hand' family holds bird, bee, ant, fly, chick;
  'see' holds 'downstream'. Aarakocra avoidance words called "paraphrase" are single syllables, and one word o˨n
  replaces 'eat', 'see', 'sit' and 'sleep' (Dyirbal Jalnguy merges into general terms, not unrelated verbs); 'head' and
  'foot' share k͡pe˨t. Dragon languages have 3% speaker-felt families against 8-23% elsewhere.

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
- **R3. Every recipe and myth is the same text.** All ten recipes run "Take X. Grind it with a stone. Put it in the
  pot. Cook it at the fire. Eat it with salt. It is good." (grinding cane, alliums, nightshade fruit, bananas; goat
  meat swaps in "cut with a knife"). All five myths forbid wild swine (elf, drow, aarakocra, silver dragon,
  dragonborn, three different faiths); all use "X holds Y. X gives us water/rain.
  X, hear us!". Fix: recipe steps from the cuisine data (boil, roast, ferment, dry, pound, soak), a few sentence frames
  per step, and myth lines drawn from the faith's own data or left out when thin (`texts.py`).
- **R6. Myths of the wrong people.** Elf 7 and drow 2 show "the sky faith of the earliest hill giants of the east of
  Ratal" with no word on how elves came by it; the faith is "founded 300 kyr ago" (silver dragons: 250 kyr), 15 times
  older than any proto-language here (20 kyr). Fix: say "a faith the elves took from the hill giants" and cap founding
  dates at the founding people's own language age, or explain the gap.
- **R9. Translations add words.** "the carrion birds" / "the wild swine" for plain bird-PL / pig-PL (elf, drow,
  aarakocra, silver, dragonborn myths). Fix: gloss what is there ('birds', 'pigs'), or coin the compound.

### Names
- Mostly convincing (sentence names like Yegǀuwizi 'the child came', matronymics, settlement etymologies). Two slips:
  liturgical hill giant 'sky-father' is a˦, the same as 'we' a˦ ("a a rramiiwi"), and most liturgy words are a single
  vowel (u 'soul', i 'sing', i 'give'); internal ids leak into word families as **god:31 (name)**, **god:255**,
  **god:289** (elf, aarakocra, halfling, silver dragon). Fix: print the god's name; apply the minimal-word rule to
  liturgical languages too.

### Presentation
- **R4. Slash brackets on phonetic output.** The joined line under each sentence is written /…/ but carries
  allophones (elf [d] for /t/, [ʘ̬] for /ʘ/) and phrase sandhi. Use [ ] or label it "as said".
- **R7. Book spellings that cannot be read.** Dragons spell ˯ as "mh" and ‼ as "rh" in every word:
  samhshunwanmhch'samhshun, thurhdeïkhomhwïnerhḷ; human 20 untsumpnampmpufuf. Elf mixes click letters with px for ʘ
  (pxagǂhabu). Fix: at most one non-human mark per word in the book spelling; clicks all letters or all digraphs.
- **R10. Small slips.** "ago ago" in sketch faith and liturgy lines (`sketch.py` adds "ago" after `kyr()`, which
  already ends in "ago"); "Berlin & Kay stage other"; the index says inclusive/exclusive 'we' cannot be shown, but every
  page shows it; dragonborn lists the ˯ mark though no live word has it; "most English-like" hobgoblin has onsets ʃb-,
  hb- that the score ignores; the complexity section prints a stray "Marks beyond the standard IPA" line after the
  tortle and kobold entries.

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
- [ ] markers that bind shorten; no marker sits next to its identical source
- [ ] fable daughters descend from the shown ancestor (a check in `demo_page.py`)
- [ ] recipe and myth texts differ in more than the nouns across the ten demo languages
- [ ] numeral composition notes only where the parts are visible; arithmetic labels right
- [x] offensive-substring check passes on all book spellings in the demo
- [ ] a second cold read of the regenerated demo finds none of R1-R3 again

## Updates
- 2026-11-08: Created from inbox draft draft-language-cold-review.md (found by lang-design cold review (fresh agent, no lane history, 2026-11-08)).
