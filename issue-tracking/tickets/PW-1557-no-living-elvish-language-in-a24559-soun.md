---
id: PW-1557
title: "No living elvish language in a24559 sounds Tolkien-Elvish: should the elf people lean towards Sindarin/Quenya sound texture?"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: culture
effort: m
impact: med
found_by: lang-find
blocked_by: []
relates: []
refs: [tools/language/find.py, tools/language/data/reference_profiles.tsv, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## In plain words

The new language finder (`tools/language/find.py --like sindarin|quenya`) ranks every living language of a24559 against
Tolkien's two Elvish languages. None of the 27 languages spoken by elves, drow or sea elves comes close: the nearest
elvish match for Sindarin scores 4.7 and for Quenya 4.0, where a close match is under ~2 (Japanese finds three at
1.3-1.4). Elvish lects in this run tend to have tones, ejectives, retroflexes or nasal vowels, and short CV(C) words
(e.g. d548 Himgimchalu: sun /la˧/, water /u˦/, bird /mu˧bu˦b/; d675 Isemwas: sun /ipʼle/, two /nirpikʼ/). The best
Sindarin and Quenya matches overall are a storm-giant and two human lects.

## Description

Why it matters:

If Daniel (or a player) expects "the elves" to sound elvish in the D&D/Tolkien sense, the generated elvish languages
will read as arbitrary. That may be fine (the model nudges, it does not copy Tolkien), so this is a judgement call.

## Options

A. Leave it: elvish languages are free to sound like anything; the finder already surfaces the most Elvish-sounding
   language of any people.
B. Nudge the elf people's proto-language preset towards liquids and nasals (l r n m), θ/ð, vowel-final or sonorant-final
   words, no tones or ejectives, and slow loss of that texture (long generations already keep it conservative).
   Judge on several runs with `find.py --like sindarin --people elves` (distance under ~3 for the best elvish lect).

My lean: B as a light nudge on the proto preset only, if Daniel wants elves to read as elvish; otherwise A.

## Updates
- 2026-11-08: Created from inbox draft draft-elvish-lects-not-tolkien-elvish.md (found by lang-find).
- 2026-11-08: RULING (owner, Language Desk): leave the elves as their own (no nudge), but check that a Tolkien-like language could arise from the generator at all. Measurement running (elf proto draws scored with the finder's Sindarin/Quenya profiles).
- 2026-11-08: MEASURED (read-only, 9,000 proto draws with the generator's own draw_inventory/proto_lexicon/proto_grammar, scored by tools/language/find.py; scratch scratchpad/elvish/). Elves draw the same protos as humans (voice_profiles same_as_human). Calibration: Welsh scores 2.09 vs Sindarin, Finnish 3.08 vs Quenya, Spanish 2.66 vs Quenya, so "under 2" is stricter than Tolkien's own models.
  - Quenya: best 2.27; under 2.5 ~1 in 1,100 draws, under 3 ~1 in 63 (a run with 7 elf protos: ~1 in 9 chance of a Finnish-level Quenya-like elf proto).
  - Sindarin: best 3.01, none under 3. Blockers, by ablation: (1) consonant texture: r 1.1% vs 5.2%, l 2.2% vs 4.7%, n 2.8% vs 6.8%; word-final n/r/l/θ almost absent (codas use the same weights as onsets: inventory.py LEXICAL_MANNER approximant 0.45, lateral 0.9, rhotic 0.8 vs stop 1.4; _weights sqrt PHOIBLE share; _coda_cluster); (2) open-word share never below 33% at the proto (inventory.py _draw_shapes / SYLLABLE_TYPES; Sindarin 8%), only sound change can lower it (36 living lects reach <=25%); (3) θ/ð, y, ɬ, long vowels drawn independently, all four together 0 in 3,000.
  - In a24559 the 27 elvish lects drifted toward open syllables (+24 pts vowel-final), away from Sindarin (+0.69) and level on Quenya.
  - Realism angle (not a Tolkien fix): cross-linguistically codas favour sonorants (nasals, liquids) over obstruents (sonority/coda condition; Clements 1990), and n, r, l are among the most frequent consonants in running text. A sonorant-favouring coda weight would be a realism gain that also opens the Sindarin corner. Owner call on the Language Desk (card e.coda).
