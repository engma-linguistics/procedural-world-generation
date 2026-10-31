# v1.0 cut plan (lane 87, read-mostly triage, 2026-10-31)

## In plain words

**Can we cut the v1.0 tag now? Not quite, but nearly. About one working day from now, if the release checks come back clean.**

- None of the 23 open v1 tickets is a physics blocker today. The lane 75 and lane 80 merges already did the physics work the tag needs. The decisions log says "climate called done for v1" (2026-10-30, lane 80). The hard-failure tier was measured at 0 of 18 frozen over inside the judged window after PW-1142 (lane 75, one 18-draw roll at L6). That is the only evidence on file.
- PW-1156 (frozen spells after an 8-fold CO2 drop) was filed before PW-1142 merged. It describes the old state, in which 4 of 18 worlds froze over. Under today's main, 0 of 18 are frozen in the window, so I rate it not a blocker and obsolete until the tag checks say otherwise. The one thing missing is a re-check on more draws. That re-check is the real gate, and it is the first item in the plan.
- PW-1158 (carbon source runs low late) was looked at by lane 80. It cancels against a second, opposite bias (the erosion reference learnt on bare ground). Both are to be fixed together in v2. Not a blocker.
- What is still genuinely needed for the tag is a short list of release chores. These are the pre-tag checks (PW-825), the two docs tickets (PW-814, PW-816), a showcase rebuild on the final code (not a ticket today; PW-202 was done on older code, and old runs now refuse to re-slice), a full test run, and a hard-bar tally on more draws than 18.
- The 11 peoples and time-zoom tickets (1151, 1152, 1173, 1174, 1180 to 1184, and the viewer pair 1153 and 1176) are not tag blockers. Peoples tuning is the v2 fun lane. The owner already approved the fixes on 10-31 (desk D20), so lane 83 is implementing them. The viewer pair is polish.
- Nothing outside the v1 milestone blocks the tag. The high-impact open physics tickets are all v2, later or unscheduled. The board has no `bug` type, so I filtered by impact high in physics and infra subsystems.

## Owner decisions needed (plain words)

1. **Does the tag mean "the planet is done, peoples ship as they are"?** I recommend yes, and I recommend labelling peoples as a preview in the release notes. The alternative is to hold the tag until the peoples fixes you approved in D20 (fit-weighted contest, local founding, split-teleport fix, density by way of life) land and are re-measured. That would add roughly a day or two, with no gain to the planet. Under the default D&D preset humans already hold 58 to 71% of people. The 85% failures happen only in small authored trees.
2. **PW-508: should a server restart in the middle of a make job resume the tectonic run?** On 10-29 you said reliability bugs come into v1. The cheap half is already merged: a killed run keeps its folder and checkpoints. The resume half needs keyframes saved as the run goes. It is medium to large work (half a day to a day) and the cost of not having it is losing up to about 30 minutes of an L7 run after a crash. I recommend moving it to v2 and saying so in the release notes. Your call, since it sits against your 10-29 ruling.
3. **PW-1119: is 25% of land under ice fine as the "glacial maximum" line for the tag?** You already said it is a good placeholder. Only the literature check is left. It affects a report flag, never a pass or fail. I suggest closing it at the tag with the source noted, or moving it to v2. No decision needed unless you want a different number.
4. **Is the hard-bar evidence enough?** The 0/18 result is one roll of 18 L6 draws. PW-932 shows a single roll swings by up to about 6 passes. I propose a pooled 36-draw L6 roll plus about 6 L7 draws as the tag gate, with a bar of zero hard failures. If you would rather accept the 18-draw result, step 1 below is skipped and about 1.5 hours of compute is saved.

No other item needs you.

## Verdict per open v1 ticket

Cost figures use docs/coordination.md's run-cost table and the measured L6 5:40 wall for 1 Gyr on current main (PW-801 note). L7 1 Gyr was 28:52 wall solo, with a peak of 9.9 GB RAM, so no more than 3 or 4 L7 runs should run at once. /tmp is RAM.

| Ticket | Tag blocker? | Milestone suggestion | Effort and cost | Depends on |
|---|---|---|---|---|
| PW-244 epic (V1) | No. It is the umbrella, closed by the tag | Stay v1, close at tag | xs | all the below |
| PW-825 pre-tag checks | **Yes** (release chore) | Stay v1 | s. L7 earth_check a few minutes; scorecard `--seeds 1..6 --myr 1000` at L6 about 10 to 15 min wall; PW-290 L7-vs-L6 pairs 3 seeds, L7 about 45 min wall in parallel | final code frozen |
| PW-814 star-anchor docs | **Yes** (docs; stale text describes the old star) | Stay v1 | xs, 30 min, Haiku | none |
| PW-816 overview s3, s2.6, decisions:33, README biome line | **Yes** (docs; overview has stale Earth numbers and wrong CO2 text) | Stay v1 | s, 1 to 2 h, Haiku or Sonnet. Its dependency PW-821 is closed as a v1 limitation, so it can go now | PW-821 (closed) |
| PW-932 roll noise | No. It is a merge-bar rule, not a product defect | Close with a one-line rule in the coordinator playbook ("pool two re-rolled offsets"); or v2 | xs | none |
| PW-508 resume a make | No (see decision 2) | **v2** | m to l; needs incremental keyframes (PW-801 territory) | PW-801 |
| PW-969 largest plate peaks 44 to 57% | No. Average is 26% against Earth about 20%; peaks last tens of Myr; Earth is an anchor | **v2** | m, about half a day plus a 5-seed tectonics check at L6 (about 6 min per run) | PW-958/827 history; relates to PW-1158 |
| PW-980 land 35% of surface | No. Warm-shift half is obsolete (lane 28b); land 34.6 to 34.9% against target 29 to 33 is a plausibility miss, not a failure | **v2** | m; paired 36-draw judge about 35 min | PW-970 (done) |
| PW-1115 Greenland too cold | No. Owner ruled the smaller Greenland accepted; ice flow is v2 (PW-1157) | **v2** | m, probes only | PW-1157 |
| PW-1119 glacial maximum line | No (report flag only) | Close at tag, or v2 | xs | none |
| PW-1156 frozen spells start with an 8-fold CO2 drop | **No unless the step 1 tally shows frozen-in-window failures.** It predates PW-1142. 0/18 frozen in window after it | **v2** (promote back to v1 only if step 1 fails) | m. A written read of the source variance. Zero CPU if only a paper check | PW-1142 (merged), PW-1158 |
| PW-1158 carbon source runs low late | No. Lane 80 says it cancels against the bare-ground reference bias (about -1.6 C against +1.6 C). To be fixed together | **v2** (together with PW-1163) | m; needs a paired 36-draw judge about 35 min and a decision on the source | PW-969, PW-980, PW-1163 |
| PW-1151 dwarves stranded in the hominid cradle | No | **v2** | s; a data change plus a 2 to 3 world check | decided by D20 (local founding) |
| PW-1152 split inherits dragons' world range | No | **v2** | s; already approved (no inherited ranges) | PW-1181, PW-1184 |
| PW-1153 viewer dials for surge | No (viewer polish) | **v2** | s; one viewer file, no CPU | none |
| PW-1173 humans hold two thirds in even_six | No (needs decision, but the owner approved density by way of life on 10-31) | **v2** | s | PW-1189 |
| PW-1174 kobold lowlands ride the inherited range | No | **v2** (fold into PW-1152 and PW-1181) | xs | PW-1152 |
| PW-1176 viewer shows learned country | No | **v2** | s, no CPU | PW-1155 (merged) |
| PW-1180 humans take small trees | No. Only authored small trees fail; default presets are 58 to 82% | **v2** | m; lane 83 (fit-weighted contest, approved in D20) | D20 |
| PW-1181 make local founding the default | No. xs, approved in D20, rides with lane 83 | **v2** | xs plus a peoples suite re-run | PW-1184 |
| PW-1182 losers pinned at the refuge floor | No | **v2** | s | none |
| PW-1183 portal arrivals skip free-room siting | No. Only when portals are on | **v2** | s | lane 78 (merged) |
| PW-1184 split whose stem is gone founded at the world's best habitat | No | **v2** | s; high impact for peoples quality, not for the planet | PW-1181 |

Totals: 3 yes (PW-825, PW-814, PW-816), 1 umbrella that closes at the tag, 19 no. 17 of the 23 should move to v2. PW-244 stays. PW-932 and PW-1119 are close-at-tag items that would otherwise move to v2. PW-1156 is the only ticket that can come back.

### What I checked outside the v1 milestone

- High-impact open tickets in tectonics, surface, climate, ocean, hydrology and infra: PW-054, 464, 465, 846, 013, 015, 016, 026, 434, 452, 453, 558, 575, 582, 593, 626, 791, 807, 809, 815, 865, 894, 996, 1099, 1157, 1161, 801, 247, 252. Each is v2 or unscheduled, or an in-progress item under the climate-done ruling. Several are known soft misses (rain, Fennoscandia, summer winds). The owner has repeatedly ruled these as v2.
- PW-801 (L7 peak 9.9 GB) is the one worth a mention. It is not a tag blocker, but the release must say that L7 needs about 10 GB per run, and the checks below respect it.
- docs/wiki/state.md is partly stale. Its v1 section lists 15 tickets and old provenance tickets (PW-938/939/940/942 are now v2). Refresh it at the tag.

## Cut plan

Everything below happens on main in order. Where steps can overlap, it says so.

### 1. Physics (a single serial lane, only if needed)

There is no physics work that must happen. Order if the first check fails:

1. **Hard-bar confirmation (this is the gate).** Pooled 36 L6 draws (two re-rolled offsets, as PW-932 asks) plus about 6 L7 draws, using the existing judge (`docs/review/base-climate/v1-finish-12/passrate4.py`, `tools/ice_criteria.py`). Report frozen-in-window, hellhouse or boiled, ocean loss and CO2 crash counts. Bar: zero hard failures. Soft pass 60 to 70% at L7 and about 70% at L6. Cost: L6 36 draws at 12 at once is 3 batches of about 10 to 12 min, so about 35 min wall. L7 6 draws at 3 at once is two batches of about 30 to 45 min, so 60 to 90 min. Total about 1.5 to 2 h, run it concurrently with step 3.
2. If it fails on frozen-over, diagnose that world only and decide per the two-tier rule. PW-1156 comes back to v1 as a diagnosis and then a fix. Candidates are the source variance (PW-1158 and PW-1163 together). Add 1 to 3 days.
3. If it fails only on the soft bar, accept it per the owner's L7 60% ruling. No physics step.

### 2. Release checks (PW-825 and friends)

| Check | Command or source | Cost (wall) |
|---|---|---|
| L7 earth_check | `uv run python tools/earth_check.py --level 7` | a few minutes |
| Scorecard on 6 seeds | `uv run python tools/scorecard.py --seeds 1 2 3 4 5 6 --myr 1000 --jobs 7` (L6) | 10 to 15 min |
| PW-290 pairs (L7 drier than L6) | 3 seeds, L6 and L7 each | about 45 min, L7 limited to 3 at a time for RAM |
| Hard-bar tally | step 1 above | 1.5 to 2 h (overlaps the above) |
| Full test suite | `uv run pytest -q` (last merge: 854 passed) | 13 to 22 min under load |
| Optional health sweep (PW-246) | `tools/health.py` | about 50 min; skip unless the tally is marginal |

If two L7 earth_check or scorecard results disagree with the 10-30 climate numbers (Earth Köppen group about 70%, golden unchanged), stop and diagnose before anything else. Do not retune.

### 3. Docs (can run in parallel with step 2)

PW-814 and PW-816 as one Haiku lane, about 2 to 3 h. Also: refresh `docs/wiki/state.md` and `decisions.md`; refresh `docs/plan_next.md`; add the release notes (what is in, what is a preview, and the known limits: PW-1115 Greenland, ice flow, rain on the coasts PW-1099, L7 about 60% pass, L7 needs about 10 GB). Add the one-line PW-932 rule to the coordinator playbook.

### 4. Showcases, then the tag

1. Rebuild the showcase set on the final code: 4 L6 plus 4 L7 (the PW-202 recipe) with worlds and zooms, and the peoples run on each. L6 is about 6 min each in parallel. L7 is 30 to 50 min each, 3 at a time, so two batches, 1.5 to 2 h wall including worlds and zooms. Run it after step 2 passes, because it needs frozen code. Clear /tmp to keep at least 40 GB free first.
2. Owner glance at the showcase set in the viewer (the owner's 10-26 bar: casual-to-moderate scrutiny). An item for your desk.
3. Milestone moves (the coordinator applies them from the table above), close PW-244, `git tag v1.0` locally. Never push.

### Calendar estimate

| Scenario | Calendar time |
|---|---|
| Clean path: checks pass, docs in parallel, showcases rebuilt, owner glance | **about 1 working day** (compute 4 to 5 h wall, mostly overlapping; docs 3 h; a showcase glance) |
| Plus lane 83's peoples fixes landing before the tag (decision 1, alternative) | 2 to 3 days |
| Step 1 shows a hard failure (frozen over in window) | 3 to 5 days: a diagnosis, a fix lane of about half a day to a day, and a re-run of the whole tally |
| Plus PW-508 resume kept in v1 | add 1 to 2 days |

The owner's wish for finishing v1 physics sooner is met by the finding that it is already finished. The one thing that could prove otherwise is the step 1 tally, and that is cheap to run first.
