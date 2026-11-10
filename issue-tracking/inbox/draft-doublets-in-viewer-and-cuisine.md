---
title: "Show the conquest and trade doublets (cow ~ beef) in the languages viewer and on the cuisine pages"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: viewer
effort: s
impact: med
found_by: lang-lane13
blocked_by: []
relates: [PW-1636, PW-692]
refs: ["tools/language/sketch.py::doublet_rows", "tools/language/sketch.py::doublet_line", "tools/language/demo_page.py::lang_section", "planet/language/contact.py::finish_registers", "planet/language/texts.py::recipe", viewer/langview.js, viewer/langmore.js, "run a24559"]
---

## Description
In plain words: lane 13 (PW-1636) gave the languages food doublets: a conquered people keeps its own word for the
animal and takes the rulers' word for its meat (cow ~ beef), or keeps its word for the grain and takes the traders'
word for the flour or the bread. On a24559, 168 of 573 living languages have at least one (199 meat words, 145
product words), plus about 2,600 formal-register synonyms. The sketches and the demo page list them, with the conquest
or trade that brought each ("the meat word *X* from antelope folk 4, after 14 sites of the cervid folk taken by the
antelope folk about 7.0 kyr ago").

What misleads if it is never done: Daniel works in the viewer, and the viewer's language panel shows none of this, so
the conquest layer is invisible where he looks; and the cuisine side (Seven Meals, PW-692) cannot say where a
people's meat and bread words came from, which is why the feature was asked for. The data is in languages.json
already: the doublet word's etymology note ("contact, elite; doublet; the donor's word for 'cattle', kept for 'cattle
meat'"), `systems.registers.high`, and `systems.contact_layers` ({donor lect: {elite | trade: [from kyr, to kyr,
why]}}). `sketch.doublet_rows` reads it all and can be ported to JS.

What I'd do: a "Doublets" block in the viewer's language panel (food pairs first, then up to ~8 formal words), and a
line per meat or bread word on the cuisine page when its word is a doublet. Optionally the proposal's per-language
"layers" table (rows = donor languages; channel, period, words, top fields).
- [ ] the viewer's language panel lists a language's food doublets with donor and conquest
- [ ] a cuisine page names the source of a borrowed meat or bread word
