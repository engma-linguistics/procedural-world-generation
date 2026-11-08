---
id: PW-1493
title: "Minority faiths: when a culture merges into a smaller one of another faith, should the merged culture keep the survivor's faith?"
type: task
status: wontdo
parent: null
milestone: v4
subsystem: culture
effort: s
impact: low
found_by: lane205
blocked_by: []
relates: [PW-1489, PW-1477]
refs: ["planet/lineages/gods.py::Pantheons.merge", "planet/lineages/gods.py::Pantheons._set_share", docs/review/culture/faiths/minorities1.md, "run 0141d1", "run 3e0eb4", "run 07c755"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: when two cultures merge, the merged culture has always kept the faith of the culture that survives the merge, even if the
culture it absorbed was larger. Now that each culture holds faith shares (PW-1489), the pooled shares sometimes put the absorbed culture's
faith over half. To keep "its faith is the majority" true, the survivor's faith is then set to exactly half and the rest scaled down.
That happened in 35 / 23 / 22 merges on runs 0141d1 / 3e0eb4 / 07c755 (`share_counts.merge_capped`). It leaves a few cultures shown as
"faith A 50%, faith B 50%" until assimilation sorts them out, and the shares are slightly wrong in those cultures (the absorbed faith's share
is understated).

If never decided: those cultures keep reading as 50/50 for a millennium or so, and the absorbed faith's real weight is hidden.

Options:
- A (now): the survivor's faith stays the merged culture's and holds at least half. No change to any majority faith or downstream readout.
- B: the merged culture takes whichever faith is larger after pooling (a conversion-like flip, recorded in its faith history). This is more
  faithful to the people, but it changes majority faiths and counts against today's main.
- C: keep A, but pool by population instead of land, once polities give per-culture population.

Lean: A for v1-v4 (the cap is rare and fades); B only if Daniel wants merges to read as "the larger faith wins".

## Updates
- 2026-11-07: Status needs-decision -> wontdo. Coordinator 11-07: low impact; keep today's rule (the surviving culture keeps its faith, lane 205's lean). Reopen if Daniel wants the larger faith to win.
- 2026-11-07: Created from inbox draft draft-merged-culture-faith-cap.md (found by lane205).
