---
id: PW-1423
title: "Species voice profiles: sounds stored as heard (a percept space shared by all species), per-species make cost, hear resolution and articulators, inherited along the lineage tree"
type: story
status: todo
parent: PW-767
milestone: v2
subsystem: culture
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-982, PW-986, PW-984, PW-983]
refs: ["https://claude.ai/artifact/58m5qxKajjfn6TkTqq3EL2", "planet/lineages/spec.py::parse_body", planet/lineages/samples/dnd.toml, "planet/lineages/life_history.py::generation_yr"]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: every sapient species gets a voice profile saying which speech sounds it can make, how hard each is, and how finely it hears them. The language engine then works the same way for humans, aarakocra, tortles or lizardfolk. Humans are built first, but nothing in the data assumes a human mouth.

Daniel 2026-11-03 (design doc 'Languages from scratch: design', https://claude.ai/artifact/58m5qxKajjfn6TkTqq3EL2, section 'Sounds, stored as heard'):
- Segments are stored as they are **heard**: a vector over one percept space shared by all species (place as heard from formant transitions and burst spectrum, manner as heard, timing and voicing, phonation incl. harsh/growl and purr, vowel formants, pitch, plus open-ended non-human axes such as a second simultaneous source for the bird syrinx). Precedent: Jakobson-Fant-Halle acoustic features. How a sound is made matters less than for storage, but still matters for sound change.
- Per species: make cost per percept (0 easy .. infinite impossible), hear resolution per axis, the articulators present (lips, tongue tip, tongue body, velum, larynx, syrinx, beak), and a modality field (spoken now; signed reserved). Inherited key by key along the lineage tree like the existing body keys.
- Human is the default, PHOIBLE-weighted. Aarakocra labials: substitutes with a cost (heard as labial, made another way, as parrots do; rarer in inventories, likelier targets of change).
- Borrowing across species = nearest percept in the listener's inventory weighted by their hear resolution; percepts outside the listener's range are dropped (same operation as human loanword nativization, PW-984).
- Symbols: IPA, then extIPA (percussives for a beak clap), then new symbols from a Unicode phonetic block, kept as a data table; the house romanization maps them.
Open (in the doc): whether a lane drafts sourced numbers for the non-human profiles for a gut call (lean), as with the sapiens dates.
- [ ] percept space and profile schema in the lineage spec, the human profile, inheritance tested
- [ ] the demo PW-986 runs on it (other species flagged as using the human default)
- [ ] non-human profiles drafted with sources and set by Daniel

## Updates
- 2026-11-03: Daniel 2026-11-03: the lane drafts the non-human profile numbers with sources and owns the reasoning; Daniel reacts afterwards (no gut-call gate before building).
- 2026-11-03: Created.
