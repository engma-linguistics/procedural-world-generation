---
id: PW-1658
title: "Place names: each language family gets its own naming habits (first six: English, Welsh/Gaelic, Slavic, Arabic, Japanese, Bantu)"
type: story
status: done
parent: PW-767
milestone: v4
subsystem: culture
effort: l
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-972]
refs: [planet/language/names.py, planet/language/personal.py, planet/language/placenames.py, tests/test_language_names.py, docs/review/language/for-daniel.md]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: today every language names a town the same way: a generic word (town, village, fence, field, house) plus a founder's name, an adjective or the people's root. Real families differ, and that is much of why places "sound different". Each proto-language should draw its own naming habits, daughters inherit them and change them slowly, so a family is recognisable from its map.

A habit set says: which generic words a family uses for settlements and features, where they go (suffix, prefix, "X of Y" with the language's own genitive/head order), how a founder enters (genitive "X's town", collective "X's people / descendants", patronymic), and how generics wear down into endings over time (Old English tūn > -ton, burh > -bury/-borough).

First six templates, taken as patterns, never as Earth words:
- English: -ton, -ham, -ford, -bury, -ley, -wick, -ingas 'people of' (Hastings), Danelaw layer -by/-thorpe (a contact layer, as lane 13's elite/trade profiles).
- Welsh/Gaelic: prefixes Llan- (church enclosure + saint), Aber-/Inver- (river mouth: the Aber/Inver line in Scotland is a language boundary), Pen- (head, hill), Caer- (fort).
- Slavic: -grad/-gorod 'enclosure, town', -ów/-ov possessive (Kraków), -ice/-itz 'descendants of' (Katowice), -sk.
- Arabic: construct "X of Y" prefixes: Jabal 'mountain' (Gibraltar = Tariq's mountain), Ras 'cape', Wadi 'river valley', Dar 'house', Bab 'gate', Madinat 'city'; the article frozen in (Al-).
- Japanese: feature suffixes -yama, -kawa, -shima, -saki, -hara, with a voicing rule in compounds (rendaku: -kawa > -gawa).
- Bantu: class prefixes on places (Buganda land / Baganda people / Luganda language, already used for peoples) and the locative classes (Swahili pa-/ku-/mu-).

Acceptance: on a24559, place names of two families are told apart by eye in a side-by-side list; daughters of one proto share most of their generics; a sisters page row for place names.

## Updates
- 2026-11-10: Created from inbox draft draft-naming-habits-first-six.md (found by coordinator).
- 2026-11-10: Done in language lane 15 (`planet/language/placenames.py`). Each proto draws one of six templates as patterns (suffix/English, prefix/Welsh-Gaelic, possessive/Slavic, construct/Arabic with a frozen article, feature/Japanese with rendaku, locative/Bantu class prefix; spec-first templates for head-final protos, generic-first for head-first, locative favoured with live noun classes) with its own weights; daughters inherit it and drift (12% a lect: a generic dropped, taken up, or made commoner). Generics wear to one syllable by age x the template's wear (construct and locative keep theirs). Settlements carry `habit`, `frame`, `meaning` and `history`; `names.habits` lists each living lect's habit. Habit generics overlap 0.94 within a family against 0.23 across on a24559 (de1cc6 0.96 / 0.26). Side-by-side page and a place-names row on the sisters page in the lane report. Rivers and peaks on habits, and the contact layer (Danelaw -by), are lane 15 drafts.
