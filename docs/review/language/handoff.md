# Language lane handoff (overnight, 2026-11-03)

You are the language lane. You work in the worktree `.claude/worktrees/lang-design` (branch `lang-design`), alone, overnight. Daniel
(he/him, a linguist) reviews in the morning. This is a big design-led project, and you own the thinking: the design doc is a
starting point that Daniel has approved, not a spec to transcribe. Where it is thin, think it through and write down why.

## Goal for tonight, in order

1. **PW-1423, species voice profiles.**
   - The percept space: sounds stored as *heard*.
   - The profile schema in the lineage spec: make cost per percept, hear resolution per axis, articulators present, modality.
   - Inheritance along the tree, like the `body` keys (`planet/lineages/spec.py::parse_body`).
   - The human profile, PHOIBLE-weighted.
   - A **sourced draft** of the non-human profiles (avian/aarakocra, tortle, lizardfolk and troglodyte, feline, draconic, and
     the rest of `dnd.toml`). Write it in `docs/review/language/voice-profiles.md`, with your reasoning and the sources you
     actually opened. Daniel: "you're the one actually thinking through it". He reacts afterwards; this is not a gate.
2. **PW-986, the end-to-end demo**, on the fantasy peoples run **a24559**:
   - dnd preset, world 848662, time zoom 56dee1;
   - it already holds `demes.json`, `cultures.json`, `gods.json` and `settlements.json`;
   - the slice is listed in the design doc, section "Build order and checks". Language shift is IN the demo.
3. If the demo stands and its checks pass, push on into the PW-982 full version: a bigger rule catalogue, the lexicon processes
   and the grammar ladder. Stop where quality would drop. A solid demo beats a sprawling half-version.

## Read first

- **Design doc** "Languages from scratch: design": https://claude.ai/artifact/58m5qxKajjfn6TkTqq3EL2.
  - Read it with the Claude Docs connector: `read` project `2179edaf-c157-4d31-8c14-15f6d3934a73`, then its tab's body node.
  - Its comment threads hold Daniel's answers; the "Questions for Daniel" table summarises them.
  - Don't edit the doc. Write your results in the repo.
- **Ethnonym taxonomy** (endonym patterns E1-E12, exonym patterns X1-X9, name-change processes P1-P8, the per-culture name stack):
  - Claude Docs id `7b3b1078-417a-4f09-a04d-862b94bd6877` (https://claude.ai/artifact/GDbAyM2ZHRYuXKkeMes8vS).
  - Use the patterns. Its etymologies are not source-checked: never quote them as fact.
- **Tickets**: `uv run python issue-tracking/board.py show PW-767` (the epic), then PW-1423, PW-982, PW-986, PW-972 (name
  stacks), PW-984 (food loanwords), PW-985 (complexity as a pressure), PW-981 (demes) and PW-983 (the first-principles
  experiment: out of scope tonight).
- **Repo**: `CLAUDE.md`, `docs/wiki/index.md`, `issue-tracking/README.md`.
- **Code you build on**:

  | File | What it gives you |
  | --- | --- |
  | `planet/lineages/demes.py` | demes, the deme tree, contacts |
  | `planet/lineages/reputation.py` | substrate takeovers and conquests: your shift triggers; exonym v0 |
  | `planet/lineages/cultures.py` | cultures |
  | `planet/lineages/gods.py` | god domains, for the concept list |
  | `planet/lineages/life_history.py::generation_yr` | the per-generation step |
  | `crop_defs.py`, `animal_defs.py`, `crops.py`, `spread.py` | food concepts and spread routes |
  | `planet/lineages/brief.py` | the culinary brief |
  | `viewer/lineages.html` | the peoples workbench |

## Rulings (Daniel, 2026-10-28 and 2026-11-03)

- **Sounds**
  - Store sounds as heard, in one percept space for every species.
  - How a sound is made is a per-species cost, and still matters for sound change.
  - Aarakocra labials are substitutes with a cost: heard as labial, made another way, as parrots do.
  - Non-human sounds get symbols: IPA, then extIPA, then a Unicode phonetic block, kept in a data table.
- **Sound change**
  - Every rule carries its physical cause and what it needs. A species keeps the rules whose cause it has, weighted by its make
    costs.
  - Contrast maintenance by functional load is built in from the start. Without it everything erodes to mush.
  - **Rates per generation**, exponent **1** to start: long-lived peoples change slower.
  - **Tree plus wave**: changes spread sideways over the contact record as well as down the tree.
- **The deme tree is not the language tree.** Demes speak lects with shares, and language shift happens.
  - Triggers: elite rule (takeovers and conquests), swamping by migrants, city mixing, trade languages.
  - A shift leaves a substrate: an accent, local words and place names, calqued grammar.
  - In-world scholars see only about 6-10 kyr deep; store the true history and the scholars' view apart.
- **Grammar** in full depth.
  - Typology features drift at feature-specific rates, drawn with their correlations.
  - Real grams with forms move down a ladder: free word, clitic, affix, fused, lost (Heine and Kuteva paths). Sound change
    erodes them like anything else.
  - Sound change runs on inflected forms, so alternations arise by themselves; analogy levels some of them.
  - **Complexity is never a stored number.** Population, adult L2 share and isolation push on fusion and loss rates, and
    complexity is measured from the grammar.
  - First languages start low in morphology.
  - Proto-languages start around 20 kyr ago, for every species.
- **Words**
  - A concept list: core vocabulary, food, landscape, kin, numbers and god domains.
  - Replacement is frequency-dependent; new words come from derivation, compounding, colexification shifts, borrowing, taboo
    and substrate.
  - Every word carries its etymology.
  - River and place names are the conservative layer.
- **Output**
  - IPA internally. One house "common" romanization; the draft table in the doc is a placeholder, so improve it. Uvulars get
    their own spelling, from any convention linguists or real peoples have used.
  - The romanized endonym is the book headword. A run's dominant trade or city lect becomes its Common, emerging rather than
    authored, with its exonyms beside the endonym.
  - Writing is Daniel's other repo: don't look for it. A placeholder export (IPA, morpheme breaks, glosses per word) is
    welcome.

## Engineering

- **Where the code goes.** Put new code in a package of its own (lean: `planet/language/`). Keep it deterministic per seed.
  Keep it a pass over the stored peoples run, like `demes.py`. It must not change the history simulation.
- **Outputs** go to `runs/<id>/languages.json`, plus whatever the brief and workbench need.
  - `runs/` is a **symlink to the main checkout's runs** (Daniel's).
  - Adding a new file to a24559 is fine. Don't rewrite its existing files, and don't rebuild the run in place.
  - If you need a fresh peoples run, make a new one.
- **Reference data.** PHOIBLE, Index Diachronica-style change lists, CLICS, Grambank/WALS and the WLG paths are fine to
  download.
  - Raw downloads go under `data/language/`. It is git-ignored and shared with main.
  - Commit only small derived tables, with source and licence noted. Check each licence (most are CC-BY or CC-BY-SA).
  - **Never `rm -rf` through `data`, `runs`, `worlds`, `zooms` or `grids`.** They are symlinks to the main checkout. A lane
    wiped `data/earth` this way on 10-30. Delete only exact files you created.
- **The viewer.** Daniel uses the viewer, not the CLI, so the demo must show up there:
  - in the workbench: names with etymologies, a cognate table across sister lects, one paradigm per lect, and the food word's
    route;
  - and in the brief.

  Look at it with `planet serve` (port 8765). If the main server is running, use another port, and stop your server before you
  finish.
- **Tests.** Run `uv run pytest -q` on the not-slow tests and your new ones before each commit under `planet/`. The full suite
  runs at merge. Update the golden files only for intended output changes, and say so.
- **Commits.** Commit locally on `lang-design` only. Never push, and never merge to main: the coordinator merges. Don't commit
  the five symlinks (they show as untracked).
- **Commit identity.** Git identity is missing in this worktree path, so commit with
  `git -c user.name="Daniel Bishop" -c user.email="$(git -C /home/daniel/personal/repos/procedural-world-generation config user.email)" commit ...`.
- **Machine.** Stay at or under about 32 cores and about 90 GB RAM; the machine is shared. `/tmp` is RAM, so keep scratch small.
- **Waiting on long jobs.** Wait in the foreground, with `timeout 570 bash -c 'tail --pid=$P -f /dev/null'` repeated. Don't end
  your turn to wait.

## Morning report

Write it as `docs/review/language/demo.md`, in plain words for a linguist reader. Lead with what works and what doesn't.

- Sample proto-inventories next to PHOIBLE norms.
- A cognate table across sister and distant lects.
- Three or four full etymologies (a people's endonym, a river, a god, a food word).
- One food word's route, hop by hop, with the changes at each hop.
- One shift case: the deme, its old language, its new one, and what survived as substrate.
- A paradigm or two, with how they got there.
- The checks from the doc, each with a measured result.
- Screenshots of the workbench.
- The judgement calls you made and why. Put the ones Daniel should rule on at the top.

Also:
- Remaining issues go in **at most 3** inbox drafts, `issue-tracking/inbox/draft-<slug>.md` (template in the README). Never
  assign PW ids.
- Add an update to PW-1423 and PW-986 in the morning report, not on the board. The coordinator does the board after merging.

## Working habits

- **Three strikes.** If one approach fails three times in a row, write it up and move on.
- **Context.** If your context passes about 250k, write a continuation section at the end of this file: state, next steps,
  open threads. Then stop cleanly.
- **Wording.** Dragons are sapient: never call them beasts. The antelope and cervid peoples carry no "fiend" framing.
- **Genuine judgement calls.** Pick a defensible lean, build it, and list it for Daniel. Don't stall.

## Continuation (lane, 2026-11-04 03:20)

**State.** Everything is committed on `lang-design` (last commit: morning report). Read `docs/review/language/demo.md`
first: the rulings Daniel should make are at its top, then what works and what doesn't, then the samples and the measured
checks. `runs/a24559/languages.json` is the shipped run (117 MB, commit e0520b9f's code, RATE_SCALE 5). Three inbox drafts
are in `issue-tracking/inbox/` (rates and horizon: needs-decision; file size and cost; non-human variant share). Tests:
the not-slow suite passed (1483) before the tidy-up round; the language tests (507) after it.

**Next steps, in order, for whoever picks this up.**
1. Daniel's rulings (demo.md, top): the horizon measure and target, the sisters bar, exponent 1 for short-generation
   peoples, the voice-profile choices, river namers, book-mode romanization.
2. The lexicon: the replacement curve (faster rare end, slower core end) is the lever for the horizon; coinage share
   (~a third of new words) vs the 5% affix cap; apply the affix cap to the final lexicon, not only at coinage; derivation
   meanings still absurd at times (RAIN + 'do' = burn).
3. The ʒ monoculture (second commonest segment) and i at ~30% of vowel tokens: the palatalization and dispersion rules;
   rare rules firing late in long lines once the common ones hit the cooldown.
4. Romanization: ɹ and ɾ share a letter (279 lects spell two sounds alike in the full mode).
5. Food routes: the hop table and the receiver's etymology disagree in 27% of hops (the receiver replaced the word later);
   show both or mark the hop as superseded.
6. Size and speed (draft): sidecars for snapshots and etymologies; `Segment.__hash__`, `hear_word`, `functional_load`.
7. `brief.build` crashes on a24559 under current code before reaching the language section (PW-1275: the stored tree no
   longer parses); a main-branch issue the coordinator should ticket.

**Open threads.** Koine has fired on real data (109 entries) but nobody has judged it; the knowledge tables' examples
(`reference-data.md`) deserve a spot-check; `lang-time` screenshots show a complexity dip that may be a pass artefact.

## Continuation (lane, 2026-11-04 evening)

**State.** Everything is committed on `lang-design`; nothing is merged. Read `docs/review/language/demo.md` first (rewritten
tonight; every number is from the shipped run). `runs/a24559/languages.json` is the shipped run (150 MB, deterministic:
two runs identical apart from timing). Checks 7 of 9 pass: sisters strict 0.499 (bar 0.5) and the human horizon 10.7 kyr
(target 6-10) fail by a hair. Language pages: `docs/review/language/sketches/` (`tools/language/sketch.py`). Rounds and
trials: `calibration.md`. Tests: the not-slow suite passed (1,543) before the last catalogue edit (S208/S209); language
tests after it.

**Next steps, in order.**
1. Daniel's rulings in `issue-tracking/inbox/draft-language-rulings-rates-roots.md`: sisters vs horizon, the generation
   exponent, felt vs etymological word families (lean: store `etym_roots` too).
2. `draft-language-realism-leftovers.md`: p rare, ʁ ɹ ɦ too common, growl share, function-word coinage via
   grammaticalization paths.
3. `draft-languages-json-size-and-cost.md`: sidecars and the three hot spots.

**Open threads.** Small-inventory word length is about 2.5 syllables at under 300 syllables (Daniel asked for long words
there); kenku tonal share varies 67-89% run to run; the scholars' "languages" can span true families through loans.

## Continuation (round 5 core lane, 2026-11-07 night)

**State.** Branch `lang-core` (worktree `.claude/worktrees/lang-core`, from `lang-design` at 8affd567), nothing merged or
pushed. Tasks 1-4 of the round are committed; task 5 (file size and pass speed) is not started. Numbers per task are in
calibration.md "Round 5, core lane"; the not-slow suite passed after task 4 (1549 passed). The last full run (task 4,
scratch output, not in `runs/`) is 236 MB and 1284 s; determinism was not re-checked this round.

**Schema change for the surface lane.** Lexicon entries carry `etym_roots` (list of root ids, same shape as `roots`; the
historian's roots, set when the word is made); the doc-level `roots` table covers ids from both. Lexicons now hold ~712
concepts (WOLD meanings, `lists=WOLD1460` in concepts.tsv). New check row "overused segments (all living lects)".
New allophone test name "coda". Nothing else in the file changed shape.

**Next steps.**
1. Task 5, as planned in `issue-tracking/inbox/draft-languages-json-size-and-cost.md`: profile one worker first, then
   the shared tables, sidecars and one expander per side (Python and viewer/langcore.js), `etym_roots` only where it
   differs, format procgen-languages/2 in architecture.md §11; two runs identical apart from `timing`.
2. `draft-language-realism-leftovers.md`: ɒ in 18% of human lects (untraced), ɫ / y in reptilian and avian lects (profile
   intent), the u‼ vowel in the overuse check, p rare (0.60 of all lects), growl share, function-word coinage, and
   Daniel's call on ~22% polysemy.

**Measuring.** The lane's scratch scripts (`meas.py`, `runsnap.sh`) were in the session scratchpad and are gone with it;
`meas.py` read a languages.json and reported same-form pairs, tone re-firings, renewal and affix shares, replacement
shares, segment shares over all and human-voiced lects, checks, timing and bytes per key. Rewrite as needed.

## Continuation (finish lane, 2026-11-08)

**State.** Branch `lang-finish` (worktree `.claude/worktrees/lang-finish`, from `lang-design` at a6f293a3). All tasks are committed. Nothing is merged or pushed.

The final run is in place:
- `runs/a24559/languages.json`, `languages-etym.json` and `languages-snapshots.json`;
- `run.json` `meta.languages` is updated by the pass, as in earlier rounds.

Numbers are in calibration.md "Final run (2026-11-08, finish lane)". The defaults taken while Daniel was away are in `for-daniel.md`.

**Schema change: format procgen-languages/2 (architecture.md §11).** Every reader must go through the loaders:
- `planet.language.output.load(path, sidecars=...)` / `save(doc, path)` in Python;
- `LangCore.expand(main, {etym, snapshots})` in the viewer. `langview.js` fetches the sidecars when `doc.format` is /2.
- `langserve.py` serves `languages-<part>.json` beside `--languages`.

The in-memory doc is unchanged (/1 shape).

**Determinism.** The output must not depend on the str hash seed. Never iterate a set or frozenset of strings (or of Segments, whose hash includes `kind`) where the order can reach an rng draw or a float sum; sort it first. The slow test `test_deterministic_across_hash_seeds` runs the tiny world under two seeds.

**Next steps.**
1. Speed. The wall clock did not fall: steps are about 920 s at 12 workers. The next lever is the worker side (`rules._apply_one`, the Pattern memo dict, `dataclasses.replace`). Each interval forks a fresh Pool; a persistent pool would only save the fork, not the stepping.
2. The scholars' horizon still fails (10.7 kyr against 6-10).
3. The complexity tab of the demo reads today's L2, population and isolation. A per-snapshot `l2`/`pop` would let causes be dated.

## Continuation: grammar phase B (lang-gram-b, 2026-11-08)

Done on `lang-gram-b`: the demo-page bugs, then mood (IMP, HORT, OBLG, APPR), object agreement, genitive sources,
the inclusive subject marker and possessor marking. See for-daniel.md "Grammar phase B" and architecture.md section 7.
Left for the next grammar lane, in this order:
1. **Concord** (grammar-gaps item 8). Proposed shape:
   - a process `Grammar.processes["concord"]`, a sorted list drawn from "dem", "adj", "verb", grown at a small
     hazard while a class marker is bound at affix level, and dropped when none is;
   - `sentences.noun_phrase` copies the noun's class marker (same form and side) onto the adjective and the
     demonstrative;
   - `verb()` takes the subject's class marker in place of 3SG when "verb" is in the list (Bantu subject concord).
2. **Constructions as grams** (item 10): Q (from IF/'or'/'not'), COP (G056, map 'COPULA'), REL (G055), COMP (G023
   SAY), FOC (G057 COP > FOC).
   - They would need `_wanted` entries from `polar_question`, `copula` and `relative`, realised values, and
     `sentences.py` using the gram where one lives (the lexical stand-in stays as the fallback).
   - Watch the complexity score: free grams lower `mean_level`.
- Measuring: the isolated harness is
  `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/78e89d74-f837-4b74-a7da-25a178d37d96/scratchpad/gramb/sim.py`.
  - Run it with `PYTHONPATH=. NP=10 .venv/bin/python <sim.py> 300 out.json` from the worktree. It takes about
    2 minutes.
  - `shares.py` in the same folder reads it and also counts the phase B series. Copy both rather than editing them.

## Continuation (lexicon & contact lane, 2026-11-08)

**State.** Branch `lang-lexcon` (worktree `.claude/worktrees/lang-lexcon`, from `lang-design` at 8871eb3f). Nothing merged or pushed. What changed and the defaults taken are in `for-daniel.md` "Lexicon & contact lane"; numbers in `calibration.md` "Lexicon & contact lane". New module `planet/language/lexsys.py` (numeral systems, colour stages, kinship systems, sound symbolism); new table `data/borrowability.tsv` (WOLD borrowed scores, `build_reference_tables.py --only borrowability`); new checks `borrowability` (WOLD rho, pronoun loans) and `areal` in `checks.py`. Lexicon entries can carry the process `colex:<focus>` (a system's shared word); lects carry `systems` {numeral, colour, kin, intensity, areal} in the document. `lect.py` passes `contact_weights`, `numeral_base` and `population` to `lexicon.step` (a three-line change in the sound lane's file).

**The one full pass this lane ran** measured task 1 only (borrowing, numerals, colours, symbolism, substrate, areal); the food/technology words and the kinship systems were added after it and are tested on the tiny world and the lexicon tests only.

**Next steps, in order.**
1. A full pass of the current code (10 workers, scratch output), then re-tune: LOAN_CONTACT against the WOLD rho and the per-lect loan spread; AREAL_K against the areal check; COLOUR_SPLIT against the stage spread; KIN_CHANGE.
2. Kinship: steer the draw by the culture's descent (`taboos.json` clan_exogamy, cousin_one_side) and show a kin table in the sketch (`tools/language/sketch.py`).
3. Taboo and avoidance vocabulary from `runs/<id>/taboos.json` (dead_soundalike, ruler_name, inlaw_words, motherinlaw): a raised replacement hazard and an avoidance word list (lexicon-gaps rec. 6, contact-gaps rec. 7).
4. Faiths (`gods.json`): a liturgical lect frozen at the founding, learned loans for GOD, SPIRIT, PRIEST, TEMPLE and god names (contact-gaps rec. 5). Polities need a polities doc in the run first (a24559 has none).
5. Segment borrowing at high intensity (contact-gaps 3d) for an inventory areal signal.

## Continuation (lexicon & contact lane, pass 2, 2026-11-08)

**State.** Branch `lang-lexcon`, with lang-design (grammar A and B, names, finish) merged in. Nothing is pushed. The
not-slow suite passed (1734) on the merged tree. Numbers are in calibration.md "Lexicon & contact lane, pass 2" (the
horizon diagnosis and the p2/p3 runs); decisions 7-12 and the sound-lane edits are in for-daniel.md "Pass 2". The last
scratch pass (p3) is at `scratchpad/lexcon/p3/a24559/` (session scratchpad; delete it when done). Measurement scripts
are in `scratchpad/lexcon/`:
- `hnoise.py`: horizon read noise, bootstrap and logistic fit;
- `retain.py`: in-pass core retention by age;
- `tail2.py`: deep-pair shared roots;
- `gainers.py`: which rules produce a segment;
- `harness.py`: isolated-lineage retention and source mix;
- `meas.py`: pass 1's measures.

**New in the document:** horizon groups carry `logistic_kyr` and the check row carries `human_logistic`. Lects'
`systems` may hold `avoidance` {concept: [ipa, how, note]}.

**Next steps.**
1. Daniel's decision 7 (how to read the horizon). If he picks the logistic fit, switch `checks.horizon` to `human_logistic`. It reads ~13 kyr against the 6-10 target. The remaining lever is the per-lineage tail: 21% of the core survives 16 kyr, where a constant rate keeps 9%. Look at FREQ_SPREAD and the keep share of class-3 words.
2. Per-lineage retention after 1 kyr is 0.825 in p3, below the 0.86 target. The name taboos are part of it; consider KEEP_COMPENSATION ~0.95.
3. Faiths: a liturgical lect frozen at the founding, learned loans for GOD/SPIRIT/PRIEST/TEMPLE, and god names (gods.json; contact-gaps rec. 5).
4. Segment borrowing at high intensity (contact-gaps 3d): the inventory areal signal is still ~0 (-0.003).
5. The sentence lane's numeral note could use the lect's own ELEVEN/THIRTY words.

## Continuation: grammar phase C (lang-gram-c, 2026-11-08)

Done on `lang-gram-c` (from lang-design 3d239669): concord, constructions as grams (Q, COP, REL, COMP, TOP, FOC),
phase C items 13-19, and the fixes from the coordinator's read of phase B's demo. See for-daniel.md "Grammar phase C"
(defaults, measures, odd output) and architecture.md ("Grammar phase C" block, for the code). Not merged or pushed.

Left for the next grammar lane (phase D is next in grammar-gaps.md):
1. Intonation-only polar questions are 51% of the full pass (WALS about 14%): the Q pull is weak under high L2.
2. Antipassive near 0% (one gram source only).
3. Concord copies the class marker's own form; no separate agreement series. Daniel's call whether `gender` needs
   concord to show.
4. Synthesis is unchanged (55% in the 0-1 bin); FUSE is Daniel's decision.
- Measuring: copy `scratchpad/gramc/sim.py`, `shares.py` and `shares_c.py` (the last counts the phase C grams and
  processes). Run `PYTHONPATH=. NP=10 .venv/bin/python sim.py 300 out.json` from the worktree (about 1-2 minutes).
- Commits: use `git -c user.name="Daniel Bishop" -c user.email=lolologist@gmail.com commit`.

## Continuation (faiths & contact pass 3, lang-lexcon, 2026-11-08)

**State.** Branch `lang-lexcon` (lang-design 63cf15ee merged in), committed locally, not merged anywhere. Not-slow
suite 1739 passed; `-k language` 677 passed + the piper speech test, which failed once under load and passes alone (34/34,
also on lang-design). Numbers: calibration.md "Faiths & contact pass 3"; defaults and odd output: for-daniel.md
"Faiths & contact pass 3"; design: architecture.md §13c (faiths) and §13d (segment borrowing). Last passes:
`scratchpad/lexcon/p4/a24559/a24559/` and `scratchpad/lexcon/p5/a24559/` (session scratchpad; delete when done).
`scratchpad/lexcon/meas_faith.py <languages.json>` prints the faith, learned-loan and seg-loan measures, the checks
and sample faiths.

**Where things are.** `planet/language/faiths.py` holds everything faith-side: `Plan` (reads `Run.gods_doc()`, which
re-derives gods.json in memory when the stored one has no faiths, ~130 s), `coin_name`, `step` (called at the top of
`History.interval`), `learned_step`, `learned_register`, `formulas`, `faiths_json` (the doc's `faiths`). God names are
lexicon words `name:god:<root being id>` with pos NAME (lexicon.step and stats skip NAME). Liturgies are frozen lect
copies `lit<fid>` in `h.liturgy`, not in `h.lects`. Segment borrowing: `lexicon._kept_segments` / `borrow(rng,
intensity)`, logged in `systems.seg_loans`, applied by `History.take_segments`.

**Next steps.**
1. Daniel's calls 1-8 in for-daniel.md (half-life, freeze point, segment borrowing rate).
2. River names through each lect's sound-change history (`name:river:<id>` words, as for gods), then X9 and P1/P3/P5-P7.
3. The horizon now reads low on the window (4.3) and 11.0 on the logistic fit; decision 7 of pass 2 still open.
4. Domain words for desert and sun gods (they borrow fire and sky).
