---
id: PW-1654
title: The Common rendered in English, Tolkien-style (on by default), with what the locals actually call each place alongside
type: story
status: done
parent: PW-767
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-972, PW-1549]
refs: [planet/language/names.py, planet/lineages/nameslot.py, "planet/language/placenames.py::english", "planet/language/placenames.py::unique_english", tests/test_nameslot_calendars.py, docs/review/language/for-daniel.md]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: owner ruling 2026-11-10: by default the Common is shown "translated" into English, the way Tolkien gives Westron as English (Hobbiton, Bywater) and Rohirric as Old English, so a DM can say every Common name aloud. Every name already carries its meaning ("the red field", "Krak's town"); with the toggle on, the Common's names are built as English compounds from that meaning using English's own generics (TOWN/enclosure > -ton/-worth/-hay, HOUSE > -ham/-stead, FIELD/clearing > -field/-ley, WALL/fort > -bury/-borough, MARKET > Chipping-/-cheap, trading place > -wick, a founder > "Grim's" + generic: Grimsby-style). Other languages keep their own forms.

Owner also wants the deep history visible: each place shows the English Common name, the local name (each lect that holds it), and the chain of older names with who gave them.

Toggle: viewer control (owner uses the viewer, not the CLI), default English. Acceptance: no English Common name is an English swear or slur (spelling guard), names are unique per region, every one traces back to the meaning it translates.

## Updates
- 2026-11-10: Created from inbox draft draft-english-common-translation.md (found by coordinator).
- 2026-11-10: Data side done in language lane 15 (`placenames.english`, `names._english_feature`): every settlement, ruin, river, lake, sea, peak and land carries `english` (a calque of its meaning with English generics: -ton/-worth/-hay, -ham/-stead, -field/-ley, -bury/-borough, -wick/Chipping, -ford, -mouth, -kirk/-minster, -dale/-combe, -fell/-horn, -ness; a founder Grimsby-style, 'X's people' -ing-, descendants -ings) and `english_how`. Unique per region (the deme's place) by a qualifier (Great, Upper, Kirk...), one name per river along its course; every name passes romanize.offensive (0 flagged on a24559). The local name and the `history` chain (founders' name, each later holder's hearing) sit beside it; nameslot.slot places carry `local` and `english` (nameslot.place_english). The viewer toggle and map labels are PW-1655.
- 2026-11-10: Lane 15b: one founding per site (`Personal.founding`): a site several demes list (264 on a24559) is coined once by the founders' lect on its cell, and each deme hears that name; the English translates that one founding meaning (later holders only re-hear the sounds), so it is the same in every deme and matches the meaning beside it (was 137 sites with two meanings, 156 mismatched records; now 0). Uniqueness now holds in every region a site sits in; ruins keep `english_how`.
