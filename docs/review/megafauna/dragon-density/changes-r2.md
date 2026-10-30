# Round 2: what each review point became

Round 1 draft: commit fd57cebe. Reviews (coordinator's scratchpad `dragon-review/`): peer, farlow, nagy, mcnaughton-coe, carbone,
jetz-hamilton-sandom-ripple (jhsr), coverage; plus the owner's notes (OWNER-NOTES.md). Every reviewer quote relied on was re-read
in the PDF (text layers searched for the exact phrase; Farlow pp. 172, 176, 187-190, Hamilton 2007 Fig. 1, Hamilton 2009 Fig. 2,
Marshall Tables 1-2, Coe Fig. 3 and Nagy 1999 Table 2 read as page images). No reviewer quote failed that check.

Status: **fixed** (where), **declined** (why), **deferred** (to which inbox draft). Section numbers are round 2's.

## Numbers and provenance

| point | what was done |
|---|---|
| peer M1 (sweep at c32e89f8 with old refs) | **fixed, and partly right**: the round-1 default sweep in fact reproduces exactly on main (2a7385/7002 identical cells and counts; orc mean density 1.391 both), so it ran after the refit; only the old pressure-off arm ran at c32e89f8 (2a7385/7000: 604,169 then, 601,925 now). Regardless, a new sweep on main b36c9581 (snapshot 8c7ce305) is stored persistently in `data/review-inputs/dragon-r2/` with its scripts; every output records `rev`; the page header names both commits. |
| peer S3a (unpaired columns) | **fixed**: the pressure-off arm covers the same 24 worlds and rolls; every comparison is paired; per-run ratios in `paired`. |
| peer S3b (ratios quoted too narrowly; arms' maps diverge) | **fixed**: Table 2 gives run ranges and the median (range) of the paired ratio; Section 3 states the class-area divergence between arms; Limitations repeat it. |
| peer M5 (three channels) | **fixed**: named in Section 1 step 7; a third arm (persecution off, overkill on; 6 runs, roll 7000) splits them (Table 3, `channels_7000`). |

## Analysis bugs

| point | what was done |
|---|---|
| peer S2 ("others" drawn as nobody's) | **fixed** in `charts.py` and `dragon_numbers.py` (class 1 = others' country); map legend, boxes and every table carry it. Box land = land fraction × box area on the sphere. |
| peer S1 (rich empty land: habitat, not pressure) | **fixed**: Section 4.3 measures pressure, occupancy and suitability over all runs; round 1's pressure explanation is withdrawn in the text; `draft-dragon-habitat-coverage-rich-land.md` replaces `draft-rich-empty-land-holds-few-dragons.md`; Section 7 item 6. |
| peer M2 (127:1 vs the band drawn at 1.65 t) | **fixed**: both ratios given everywhere (96:1 at eco mass, 127:1 all ages); Figure 4's caption says the model sits just outside the band at 1.65 t. Abstract no longer offers the band as support. |
| peer M3 (30 kyr jump, 300 kyr drop) | **fixed**: both steps measured in every run and both arms (Section 4.5, `steps`); eras 31 and 29 kyr added to the probe. The 30 kyr step is located on the empty land's food (×3 in both arms), which the pressure makes dominant; peer's "a pressure effect" is half right. Cause beyond that deferred (`draft-dragon-count-step-at-recent-pass.md`, updated). |
| peer M4 ("food alone" two meanings) | **fixed**: "pressure off" (the arm) and "food-fed density" (per cell) defined once in Section 3; the phrase "food alone" is gone. |
| peer M6 (order of eating; uneaten share; small predators unpressed) | **fixed** as Section 7 item 12; draft `draft-food-budget-uneaten-share-and-unpressed-small-predators.md`. |
| peer M7 (young dragons eat in the apex class) | **fixed**: Section 1 step 5 and Section 7 item 8 (factor computed from the stage food shares); draft `draft-guild-weighting-exponent-and-young-dragons.md`. |
| peer: chart contrast in light mode | **fixed**: every chart drawn twice in the page's ink tokens and swapped by theme (media query and `data-theme`); categorical palette validated in both modes (light: contrast WARN, relieved by direct labels and tables). Page muted ink darkened to 5.5:1. |
| peer: Figure 1 log bars from an arbitrary base | **fixed**: dot plot with per-run ticks (Figure 2). |
| peer: Figure 3 points vs text | **fixed**: points pooled over all runs; occupied cells shown separately, which is what sits on the line. |
| peer: Figure 4 axis and arm labels | **fixed** (Figure 5): axis states linear/log; arms "pressure off" / "the model (pressure on)"; both hand-overs marked. |
| peer: Figure 5 (old viewer screenshot) | **fixed** (dropped): it supported no claim; `draft-viewer-dragon-density-layer.md` stays. `shot.py`, `crop.py` removed. |
| peer: Figure 6 no graticule, others' legend | **fixed**: ticks and grid in degrees, "equirectangular" in the caption, five-class legend. |

## Sensitivity (peer S4)

**Fixed**: Section 2, `sensitivity.py` (analytic), Table 1 and Figure 1: intake law (Nagy reptiles, lizards, Varanidae, mammals,
birds; McNab varanids and dinosaurs), Nagy 2005's 30-170%, guild exponent 0.6 / 0.66 / 0.75 / 0.79 / 0.85 / 0.889, assimilation
66% / Nagy's conversion / 85%, carcass use 65-91%, offtake against Farlow's turnover and Coe's production/biomass, and the
above-ground share of NPP; three joint cases. The "literature-leaning" case keeps the 10% offtake (the higher offtakes are upper
bounds, Farlow p. 176), and lands at ×0.96.

## Peer minor points

| point | what was done |
|---|---|
| wild-game share blending | **fixed** (Section 1 step 3). |
| 625,000 vs 711,000 kcal per head | **fixed** (Section 1 step 3, "one animal, two values"). |
| "86% of the way" → on a log scale | **fixed** (Section 1 step 7, Section 7 item 1). |
| plain words: per-world range; "the model assumes"; rich grassland caveat | **fixed**: plain words rewritten; numbers computed; occupancy caveat in paragraph 2. |
| McNaughton production check is weak | **fixed** (C4 caveat). |
| grazing NPP is not McNaughton's NAP | **fixed** (C24, Section 7 item 2, draft). |
| Sword Coast ranges | **fixed** (Table 7 run range). |
| western Europe box land share | **declined**: no coastline or land mask is on file, and the reviewer's 40-45% sea is an eyeball estimate; the page says the comparison is of size and shape only. |
| herders' land share per era | **fixed** for now (Table 2 "Land now"); per-era shares are in `numbers.json` (`land_share`). Partly declined: the table would get too wide at phone width. |
| jargon, ticket ids and code identifiers in prose | **fixed**: the body has none; Appendix A ("For the developers") maps them. |
| abstract without ticket ids; caution moved up in plain words | **fixed**. |

## Paper checks

| reviewer, item | what was done |
|---|---|
| mcnaughton-coe 1 (C1 above-ground; B incl. insects) | **fixed**: Section 1 step 1 (C24, C25), Section 2 row f, Section 7 item 2, draft `draft-prey-fit-fed-whole-plant-npp.md`. |
| mcnaughton-coe 2 (C4 comparator) | **fixed**: C4 caveat; Coe P/B used as the bound (C26). |
| mcnaughton-coe 3 (C3 x variable, domain, r) | **fixed**: C3 sentence rewritten with NAAP from rainfall, domain, r = 0.966. |
| mcnaughton-coe 4 (C2 page and refs) | **fixed**: pp. 142-143, refs named. |
| mcnaughton-coe bibliography | **fixed**: "DOI not printed" for McNaughton and Coe. |
| farlow 1 (reversed reading) | **fixed**: Section 4.4 (C16, C17 with the p. 190 quote), Section 8 paragraph 2; round 1's sentence withdrawn explicitly. |
| farlow 2 (fauna ratios pp. 189-190) | **fixed**: C36. |
| farlow 3 (Farlow's milder correction) | **fixed**: Section 1 step 5 (C18). |
| farlow 4 (eq. 7/8 cross-check) | **fixed**: Table 1 caption (C33). |
| farlow 5 (wording, offtake share of turnover) | **fixed**: Section 1 step 2. |
| farlow 6 (C15 "Komodo dragon data added") | **fixed**. |
| farlow bibliography | **fixed**: "DOI not printed". |
| nagy 1 (2.7 t mass framing) | **fixed**: Section 1 step 6 (C27): all-ages mean, a single ~1.0 t reptile's rate; 4.1 t at 1.65 t; adults and ancients eat 84%. Owner note 3. |
| nagy 2 (85% unsourced; Nagy's own conversion) | **fixed**: Section 1 step 6, Table 1 row, Section 7 item 4, draft `draft-dragon-kill-conversion-assimilation-carcass.md`. |
| nagy 3 (uncertainty; Nagy 2005; growth) | **fixed**: C28, C29, Table 1 rows. |
| nagy 4 (fit choice: lizards, Varanidae) | **fixed**: Table 1 rows; Section 7 item 3. |
| nagy 5 (code comment p. 260 → p. 261) | **deferred**: model code is out of scope for this paper; in `draft-dragon-intake-law-and-label.md`. |
| nagy 6 (bibliography) | **fixed**: Nagy 1999 "DOI not printed" (the PDF prints none; not added from memory); Nagy 2005 added with its printed DOI. |
| carbone 1 (C12 against the fit at 1.65 t) | **fixed**: 62 kg vs 104 kg, 1.7×. |
| carbone 2 (C10 has a source; exponent sensitivity) | **fixed**: C10 cites Carbone & Gittleman p. 2274 and note 10; Table 1 exponent rows. |
| carbone 3 (C8 "predicted"; species per class) | **fixed**: Section 1 step 5. |
| carbone 4 (C9 page 2685; source line) | **fixed**. |
| carbone 5 (C11 mass; extrapolation; prey basis) | **fixed**: Section 4.4 first bullet. |
| carbone 6 (C23 at eco mass) | **fixed**: 46:1 and 35:1. |
| carbone 9 (p. 2687 ectotherms; p. 2683 juveniles) | **fixed**: Section 4.4; Section 7 item 8. |
| carbone bibliography (issue 5563) | **fixed**. |
| jhsr 1 (Hamilton units; 4.44 vs 4.14) | **fixed**: Section 8 (C22), both constants, r² and scatter. |
| jhsr 2 (Ripple "17 of 31"; leads) | **fixed**: wording; Cardillo 2004 and Woodroffe 2000 put on the wishlist as "to fetch", not cited (owner note 4). |
| jhsr 3 (Sandom co-evolution caveat) | **fixed**: Section 7 item 9, Section 8 (C19). |
| jhsr 4-5 (Jetz caveats; overlap) | **fixed**: Section 4.4. |
| jhsr bibliography (Jetz 5694, Ripple 6167) | **fixed**. |
| jhsr code comments | **deferred**: to the relevant drafts (pressure source, overkill via PW-1000). |
| coverage 0 ("On file, not used" wrong) | **fixed**: Marshall, Burness, Carbone 2007, McNab, Hamilton 2009, Nagy 2005, Seymour now cited; only the flight papers remain "on file, not cited". |
| coverage Marshall M1-M5 | **fixed**: ecological mass attributed (C31); density line and interval (C34); viability (C37); M5 (reptiles 30-fold denser) **declined** as redundant with the Farlow reptile line. |
| coverage McNab Mc1-Mc3 | **fixed**: Mc1 (Section 1 step 6, C30, Section 7 item 3). Mc2, Mc3 **declined**: the Mesozoic-community ratio and the 8 t maximal theropod add little beyond C30 and Burness. Code-note (docstring "~0.55 of a mammal's") **deferred** to `draft-dragon-intake-law-and-label.md`. |
| coverage Burness B1-B3 | **fixed**: B1 (Section 4.4, C35), B2 (Section 6, C38). B3 **declined**: the 10-fold endotherm intake is a general statement already covered by Table 1's intake rows. |
| coverage Carbone 2007 Ca1-Ca5 | **fixed**: Ca1-Ca3 (Table 1, Section 7 items 4 and 8). Ca4 (maximum mammalian carnivore 1,100 kg) and Ca5 (largest species vulnerable) **declined** for length; neither moves a number. |
| coverage Hamilton 2009 H1-H3 | **fixed**: H1 (C40), H3 (Section 8). H2 (population size follows productivity) **declined**: it bears on PW-1020, not on dragons. |
| coverage Seymour | **fixed**: C39 in Section 8. |

## Owner's notes

| note | what was done |
|---|---|
| 1 length, plain summary first | **fixed**: full paper structure, plain words first, then abstract. |
| 2 game-present table | **fixed**: Section 5, Tables 5-6; method and the judgement stated; marked an extrapolation. |
| 3 stance; examples | **fixed**: Section 7 (twelve changes) and Section 8; every example named in the note is on the page (whole-plant NPP, 2.7 t label, 85%, flat 60% overkill, reversed Farlow). |
| 4 Woodroffe, Cardillo "to fetch" | **fixed**: `docs/references/wishlist.md`; listed on the page as "to fetch, not cited". |

## Declined (collected)

- Western Europe box land share: no land mask on file; an eyeballed share would be a number without a source.
- Marshall M5, McNab Mc2-Mc3, Burness B3, Carbone 2007 Ca4-Ca5, Hamilton 2009 H2: true, but they move no number on the page.
- Changing model code or code comments (nagy 5, jhsr code comments, McNab docstring): this is the paper; each is in a draft.
- Per-era land shares in Table 2: kept to "now" for phone width; all eras are in `numbers.json`.

## Left for later (not done in round 2)

- The 30 kyr step's cause beyond "the empty land's food changes at the hand-over" (needs the ice-age pass's own fields).
- A source for the above-ground share of NPP (wishlist).
- A source for persecution (Cardillo 2004, Woodroffe 2000 to fetch).
- Whether the model's viability test is strict enough at regional counts (draft).
