---
title: "Languages: word families grow through chains of compounds (hand > wing > bird > bee); felt families should stop where a speaker no longer hears the root"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: low
found_by: language lane 9 (PW-1537 R10)
blocked_by: []
relates: [PW-1537]
refs: ["planet/language/lexicon.py::felt_roots", "planet/language/lexicon.py::compound", "planet/language/lexicon.py::refresh_roots", "tools/language/sketch.py::_root_family", "tools/language/sketch.py::felt_members", planet/language/data/compounds.tsv, planet/language/data/derivations.tsv, docs/review/language/sketches/d760-hobgoblin.md, "run a24559"]
---

## Description
In plain words: the cold review (PW-1537 R10) found the hobgoblin 'arm or hand' word family holding bird, bee, ant,
fly and chick, and 'see' holding 'downstream'. Each single step is a real pattern (wing = 'arm of bird', a bird =
'the winged one', a chick = 'little bird'), but the sketch lists everything whose first root is 'arm or hand', so a
chain of three or four steps lands 'bee' in the hand family. The review also noted dragon languages have 3% of words in
felt families against 8-23% elsewhere.

Lane 9 checked where the chains come from (16 human protos, 20 kyr isolated, scratch harness): proto families are
sound (HAND > HOLD 'do', SEE > EYE/FACE 'thing', EYE > WINDOW). Odd members come from compounds made later, whose main
root is their head's: EYE + DAY = sun (Malay mata hari), then SUN + NIGHT = moon, SUN + 'like' = hot, so moon and hot
join the eye family; ARM OR HAND + BIRD = wing; HAND + TWO = ten, twelve. The hobgoblin chain itself was not
reproduced in the harness (it needs the stored run's history).

**What misleads if never done:** the "word family" section of a sketch or the demo can show families no speaker
would feel (bee under 'hand'), which reads as random.

What I'd try: `felt_roots` keeps a compound's head root only one step deep (a compound built on a compound is felt
under its nearest head: moon under sun, not under eye), and the sketch's family lists only members within two steps of
the root word. Then read the dragon felt-family share on the same run (their long generations make fewer new words,
which may be all it is).
- [ ] no felt family member more than two compound or derivation steps from the root word in the a24559 sketches
- [ ] the felt-family share per people reported before and after
