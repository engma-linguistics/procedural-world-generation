---
id: PW-1737
title: "Languages: check pass rates over several worlds and seeds run concurrently, not single draws on a24559"
type: story
status: done
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, tools/language/real_inventory.py, "planet/language/checks.py::run_all", "run a24559", "run de1cc6", docs/review/language/calibration.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: every language constant was tuned on one world (a24559). A fresh pass on de1cc6 fails 3 of 17 checks, and single-draw pass/fail flips on unrelated commits (making HUNDRED/THOUSAND 3x more borrowable flipped three checks). Daniel 11-11: run against a few worlds concurrently.
Build a matrix tool (tools/language/matrix.py or similar): N peoples runs x 2 seeds, each `planet languages RUN --out scratch --seed S`, run concurrently within the half-machine cap (e.g. 3 worlds x 2 seeds at 4 workers each = 24 cores, ~10-15 min wall, each under systemd-run MemoryMax), then a table of every check per cell and a pass rate per check. Pick the worlds: a24559, de1cc6 and one or two other dnd peoples runs present in runs/ (a Seven Meals run as a stress cell if cheap). A lane's acceptance becomes the matrix pass rate (bar to set with the first baseline, e.g. each non-horizon check passing in >= 70% of cells, per the seed-pass-rate convention), not a24559 alone.
Same lane (honest checks, from the assessment):
- [x] matrix tool + recorded baseline; for-daniel and wiki status cite it
- [x] horizon judged on the smoothed/logistic reading against the owner's ruled band (~11 kyr and up close enough, decisions 11-08), so it stops being permanently red
- [x] label the six wiring checks (proto inventories, long generations, hubs, WOLD, contact kind, doublets) as guards, not realism evidence; raise the doublet bar near the output or drop it; areal check must fail when there are no pairs
- [x] re-record the real-inventory benchmark baseline with 2-3 absolute bars (back harmony < 25% of daughters, >= 4 of 7 languages keep character)
- [x] test that --workers does not change output; drop the absolute checkout path from constants.generation_overrides.spec
- [x] judge whether de1cc6's sisters dip since lane 16 (0.476-0.513 vs 0.53-0.55 before) is a regression, and fix if so

## Updates
- 2026-11-11: Created.
- 2026-11-11: Lane 18: matrix tool + baseline (docs/review/language/matrix/), all checklist items done; de1cc6 sisters: lane 16 dip mostly undone by lane 17 (-0.01 vs lane 15 on paired seeds), not diffusion, no fix. Pass bar and benchmark keep-character bar filed as drafts.
- 2026-11-11: Done in lane 18 (merged e4c31aeb; suite 2146 passed): tools/language/matrix.py (4 runs x 2 seeds, --compare), baseline docs/review/language/matrix/baseline-2026-11-11.md, horizon judged on the logistic reading (fails only < 6 kyr), check kinds labelled, doublet bar 0.5, areal fails without pairs, worker-count test, repo-relative spec path, benchmark re-recorded with absolute bars. de1cc6 sisters: not a regression after lane 17 (0.520/0.567 vs lane 15's 0.530/0.579). Pass bar on the Language Desk as card m.bar (PW-1747).
