---
id: PW-534
title: "Time zooms 7ec3fe and ae8f75 are identical (same seed, same moment): keep one?"
type: task
status: done
parent: null
milestone: v1
subsystem: store
effort: xs
impact: low
found_by: worktree-agent-a7b485e309b6e3a74 (PW-493 now-pick check)
blocked_by: []
relates: [PW-493]
refs: ["time zoom 7ec3fe", "time zoom ae8f75", "run 8ddaa4", "run bf5ee9"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Time zooms 7ec3fe (from run 8ddaa4) and ae8f75 (from run bf5ee9) both come from seed 941637, L6,
at 864 Myr with 300 kyr. Their frame stats are identical (`F.load_timezoom` gives the same
glacial index and sea level in every frame), and both source runs have the same seed, so the
duplication is deterministic, not a bug. Both were made in the same session (00:54 and 01:17).

Decision for the owner: keep one of them and delete the other (`planet delete`), or keep both as
a reproducibility check. Nothing was deleted.

- [ ] Owner picks which to keep, or says both stay.

## Updates
- 2026-10-21: Status needs-decision -> done. Deleted the duplicate chain (run 8ddaa4, time zoom 7ec3fe, world 7e1bb1 and its 4 zooms) plus rejected/scratch fine zooms f70544 27eaef c7b799 0766c8 cd45d0.
- 2026-10-21: Owner 2026-10-21 approved deleting duplicates.
- 2026-10-21: Created from inbox draft draft-duplicate-timezoom-7ec3fe.md (found by worktree-agent-a7b485e309b6e3a74 (PW-493 now-pick check)).
