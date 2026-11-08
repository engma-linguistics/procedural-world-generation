# Language lane work queue (from the six coverage reviews, 2026-11-07 night)

Daniel 11-07: no hurry to merge; queue all of it here on lang-design. Reviews: grammar-gaps.md, phonology-gaps.md,
soundchange-gaps.md, lexicon-gaps.md, contact-gaps.md, names-spelling-gaps.md (each has a ranked list; numbers below
refer to them). Lanes are split by the files they own, so two can run at once without conflicts.

| Lane | Owns | Items | Status |
|---|---|---|---|
| finish (round 5) | output.py size, sentences.py, sound tables | size/speed, overused segments, sentences use WOLD words, final run, demo + complexity section | merged 08b80ab9 |
| grammar A | grammar.py, concepts (WE split) | grammar-gaps Phase A | merged |
| names & spelling | romanize.py, names.py, romanization.tsv | names recs 1-8 (codes vs taxonomy doc, one spelling per phoneme per lect, phonemes not allophones, no IPA leak, clicks ǀǃǁǂ, b/p aspiration, capitals); then personal names (Germanic dithematic first) and settlement names | merged |
| sound | inventory.py, rules.py, lect.py (phonology parts), sound tables | phonology 1-5 (parse_segment pool bug, tone count, stress in IPA + speech, small inventories from common sounds, dragon sub-bass); soundchange 1-3 (21 unparsed rows, per-line preferences and once-per-line named shifts, staged chain shifts, missing common changes); then **a synchronic rule layer** (Daniel 11-07: "do we have phonology and phonological rules?"): each lect keeps an ordered list of live rules, derived from its allophones and recent conditioned sound changes and phonologized as they age, applied productively to affixes, compounds, loans and new words and across word joins in sentences (harmony, assimilation, tone sandhi), and listed on the pages; series-based inventory draw, phonotactics re-check, stress on forms, lexical diffusion, tone evolution | running (lang-sound) |
| lexicon & contact | lexicon.py, inputs.py, history.py (contact), concepts | lexicon 1,3,5,8,12 + contact 1-3 (WOLD borrowability, pronoun/numeral keep, contact-intensity borrowing, substrate calibration, numeral systems, colour stages, areal check + diffusion); then food/taste vocabulary from the cuisine sheet, kinship systems, taboo/avoidance from culture taboos, faiths (liturgical language, god names), polities | pass 1 done (b3297063, not merged: horizon 17.6 kyr, nʷ overuse); pass 2 running |
| demo bugs (read of the 11-08 demo) | sentences.py, demo_page.py | person nouns glossed INAN/things class (sea elf, tabaxi merchant); noun-class numbering (tabaxi: no class 1, class 3 twice); dual prose says a marker the example lacks (white dragon); correlative note quotes 'sings' for a 'dance' sentence; classifier examples without the classifier; prose PST forms differ from examples (cloud giant iŋ vs in=, human); 'have' note says dog for a boat sentence; ᴖ (U+1D16) leaking into IPA; felt word families whose members don't share the root; self-ancestor in ancestry lines and sea elf 'elvish' from a gnome proto; relatives line drops percentages; gram labels PAST/PST mixed; 'Likely cause.' lowercase; tool/agent jargon on the page (sketch.py, 'the lane picked', G055, cx) | grammar B: fixed (lang-gram-b) |
| grammar B, C, D | grammar.py, sentences.py | grammar-gaps queue | B done (lang-gram-b); C done on lang-gram-c: concord, constructions as grams, phase C items 13-19, and the fixes from the read of phase B's demo; D next |
| texts | sentences.py, demo_page.py | romanized line on texts, Schleicher-style fable proto + daughters, faith origin myth | with grammar D |
| cold review | read-only | a fresh linguist agent reads the regenerated pages | last |

## Decisions for Daniel (collected; none blocks the queue)
1. Synthesis level (how affix-heavy), after the WALS 22A measure (grammar A task 7).
2. Species leanings in grammar: the lane's default table, for Daniel to adjust.
3. Non-human letters in book spellings (purr vs trill rr) — names rec 5.
4. Merger-veto strength / homophony; rate spread between lects (soundchange 4, 9).
5. Minority-speech lifetime after shift; L2 share levels; how much dialect continuity (contact 8-10).
6. A shifting people: keep the old language's sounds, or reshape by its own voice (phonology 16).
