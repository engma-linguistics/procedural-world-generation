# Round 2: what each review point became

Round 1 draft: commit fd57cebe. Reviews (scratchpad `dragon-review/`): peer, farlow, nagy, mcnaughton-coe, carbone,
jetz-hamilton-sandom-ripple (jhsr), coverage; plus the owner's notes (OWNER-NOTES.md). Every reviewer quote I relied on was re-read in
the PDF (text layers searched for the exact phrase; Farlow pp. 172-176, 187-190, Hamilton 2007 Fig. 1, Hamilton 2009 Fig. 2, Marshall
Tables 1-2, Coe Fig. 3 and Nagy 1999 Table 2 read as page images). No reviewer quote failed that check.

Status: **fixed** (where), **declined** (why), **deferred** (to which inbox draft).

## Numbers and provenance

| point | what I did |
|---|---|
| peer M1 (sweep at c32e89f8, old refs 2.81/382) | **fixed**: a new sweep on main b36c9581 (GRAZE_REF 279), snapshot 8c7ce305, stored persistently in `data/review-inputs/dragon-r2/` with its scripts; `dragon_numbers.py` reads it; every JSON records the commit (`rev`). Header names it. |
| peer S3a (unpaired columns) | **fixed**: the pressure-off arm now covers the same 24 worlds and rolls; every comparison on the page is pooled over the same 24 runs on both sides; per-run ratios in `numbers.json` `paired`. |
| peer S3b (ratios quoted too narrowly; arms' maps diverge) | **fixed**: section 4.1 quotes the run-by-run spread and the class-area divergence between arms; Limitations say what it means. |
| peer M5 (three channels) | **fixed**: named in section 1 step 7 and section 4.2; a third arm (persecution off, overkill on; 6 runs at roll 7000) splits the two pressure channels (`channels_7000`). |

## Analysis bugs

| point | what I did |
|---|---|
| peer S2 ("others" drawn as nobody's) | **fixed** in `charts.py` and `dragon_numbers.py` (class 1 = others); map legend, boxes and every table carry "others' country". Box land is now the box's land fraction × its area on the sphere. |
| peer S1 (rich empty land: habitat, not pressure) | **fixed**: section 4.3 measures occupancy and suitability over all 24 runs; the old pressure explanation is gone; draft `draft-dragon-habitat-coverage-rich-land.md` replaces `draft-rich-empty-land-holds-few-dragons.md`. |
| peer M3 (30 kyr jump, 300 kyr drop) | **fixed**: both steps measured over all 48 runs (section 4.6, `steps`); eras at 31 and 29 kyr added to the probe; Figure 4 marks both and states its axis. Cause of the 30 kyr step stated as far as measured; drafts updated. |
| peer M4 ("food alone" two meanings) | **fixed**: defined once in section 3: "pressure off" is the arm; "food-fed density" is the per-cell figure. The phrase "food alone" is gone. |
| peer M6, M7 | **fixed**: in section 7 (What the model should change), with drafts. |
| peer: chart contrast in light mode | **fixed**: every chart is drawn twice in the page's own ink tokens and swapped by theme; palette validated in both modes. |
| peer: Figure 1 log bars from an arbitrary base | **fixed**: dot plot with each run as a tick. |
| peer: Figure 5 (old viewer screenshot) | **fixed** (dropped): it supported no claim; the viewer draft stays. |
| peer: Figure 6 no graticule | **fixed**: latitude and longitude ticks and grid; "equirectangular" in the caption. |

## Sensitivity (peer S4)

**Fixed**: section 2, `sensitivity.py` (analytic), table and tornado chart: intake law (Nagy reptiles, lizards, Varanidae, mammals, birds;
McNab varanids and dinosaurs), Nagy 2005's ±70%, guild exponent 0.6 / 0.66 / 0.75 / 0.79 / 0.85 / 0.889, assimilation 66% / Nagy's route
/ 85%, carcass use 65-91%, offtake against Farlow's turnover and Coe's production/biomass, and the above-ground NPP share, plus joint cases.

## Paper checks

(filled at the end of round 2; see below)

## Owner's notes

(filled at the end of round 2)

## Declined

(filled at the end of round 2)
