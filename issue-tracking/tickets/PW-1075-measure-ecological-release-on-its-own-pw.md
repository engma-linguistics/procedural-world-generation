---
id: PW-1075
title: "Measure ecological release on its own (PW-1024 B): lane 50's sweep changed A and B together"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: fun-lane-50
blocked_by: []
relates: [PW-1024]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/open-niches/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** Lane 50 made two changes at once:
- A widened some dragon kinds by hand and added a "tolerates" tier.
- B lets any kind spread a little into rich land next to its country when no rival holds it.

The sweep shows the sum: rich land nobody holds now has dragons in 90% of it, up from 52%. It does not show how much of that is B. The owner wanted B so that open niches fill on any world and any custom preset, so B's own share should be known.

What to do:
- Re-run the lane 50 sweep with one extra arm, `megafauna.RELEASE = False`. Add a probe flag `--no-release`, as `--no-cap` does.
- Use the same 6 worlds x rolls 7000-7001 and the base the merge lands on.
- Report the rich empty occupancy, the dragons and giants per kind, and the released cells per kind (K above the kind's own K_own).
- If B adds almost nothing on the dnd preset, check it on a custom tree whose kinds leave a gap (for example the dnd tree with gold dragons removed). That is the case B exists for.

The knobs are design judgements, with no sweep behind their values:
- RELEASE_K 0.3;
- RELEASE_PREY 2x the median;
- RELEASE_KM 300 km.

- [ ] A-only and A+B numbers side by side in docs/review/megafauna/open-niches/README.md

## Updates
- 2026-10-30: Created from inbox draft draft-ecological-release-measured-alone.md (found by fun-lane-50).
