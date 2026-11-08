---
id: PW-1549
title: "Languages and polities: empires spread their language and loanwords, states and confederations get names, rank drives polite speech"
type: story
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: l
impact: high
found_by: lang-design (lexicon & contact, names, grammar D lanes, 2026-11-08)
blocked_by: []
relates: [PW-1434, PW-1436, PW-756, PW-972]
refs: [docs/review/language/contact-gaps.md, docs/review/language/names-spelling-gaps.md, docs/review/language/for-daniel.md, docs/review/language/architecture.md, "planet/server.py::polities_doc", planet/lineages/polities.py, planet/language/history.py, planet/language/inputs.py, planet/language/names.py, planet/language/grammar.py, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the language pass knows nothing about states. In real history empires are what make a language win
(Latin, Quechua, Mandarin): rulers' speech spreads as a second language, lends words to every subject people, and
levels its own dialects into a standard. States and confederations also get names (the taxonomy's E11 'confederation'
and X6 'dynasty or state' patterns). Without this, no language page can say "the language of the old empire", the
names slot for states (PW-1436) stays empty, and polite speech (T-V, honorifics) is driven by population size alone,
while the page claims "rank is marked in speech".

**Now.** `planet languages` reads demes, cultures, gods, settlements and taboos; no polities. On main, polities are a
derived doc (`server.polities_doc`, `lineages/polities.py::derive`, ~30 s at L7, cached outside the run folder, PW-1431),
not a file in the run. a24559 predates polities. Politeness: `grammar.POLITE_MAKE` 0.002 x community size.

**Wanted** (contact-gaps rec. 4 and 15, names-spelling-gaps rec. 15):
- [ ] the language pass reads the polities doc (derive it at pass time like gods.json, read-only), per frame
- [ ] elite-rule shift triggers: a ruling culture's state over subject demes, strength from the share ruled; the
  ruler prestige bonus architecture.md §8 specifies
- [ ] an administrative lect (the capital's) that raises L2 shares and loans across the realm, and levels same-language
  lects inside one polity toward it
- [ ] E11 confederation and X6 dynasty/state names into the names slot (PW-1436)
- [ ] politeness and honorific markers gated by kingship/rank where polities hold it, not by population alone
- [ ] horizon and sisters checks re-read (an empire's levelling moves both)

Needs a run with polities and languages both (a24559 is too old: re-run or pick a newer D&D run).

## Updates
- 2026-11-08: Created from inbox draft draft-language-polities.md (found by lang-design (lexicon & contact, names, grammar D lanes, 2026-11-08)).
