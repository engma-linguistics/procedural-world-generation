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
