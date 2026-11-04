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
