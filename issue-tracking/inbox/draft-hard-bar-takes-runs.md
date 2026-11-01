---
title: hard_bar.py and scorecard.py cannot judge a stored run
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: lane110
blocked_by: []
relates: []
refs: [tools/hard_bar.py, tools/scorecard.py, tools/ice_diag.py, "docs/review/v010-showcases/notes.md"]
---

## Description
In plain words: the tools that say whether a finished planet passes the hard bar only read the files made by the paired-judge harness, so a planet someone already built can only be judged by simulating it a second time.

`tools/hard_bar.py DIR LEVEL` reads `DIR/m_r*_*/seed*_L<level>.json.gz` written by `tools/ice_diag.py` (paired.sh). `tools/scorecard.py` runs its own level-6 sims. Neither accepts a run id. Lane 110 judged six level-7 showcase runs by converting each run's stored keyframe stats into the ice_diag shape with a scratch script (fields: sea_ice, sea_tect, sea_level, dT_end = true_temp_c minus PREIND_T, iced_land, land, star from `star_forcing`, co2). That is a stand-in: `dT_end` and the star control are not the exact diagnostic values.
- [ ] `hard_bar.py --run <id>` reads a stored run directly (and says which fields it approximates), or `ice_diag.py` can export the file from a stored run.
