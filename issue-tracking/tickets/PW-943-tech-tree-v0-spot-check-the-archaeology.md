---
id: PW-943
title: "Tech tree v0: spot-check the archaeology citations in techtree.toml (volumes, pages, dates)"
type: task
status: todo
parent: null
milestone: null
subsystem: docs
effort: s
impact: low
found_by: fun39-techtree
blocked_by: []
relates: [PW-938, PW-675]
refs: [planet/lineages/samples/techtree.toml, docs/review/techtree/techtree.md]
created: 2026-10-28
updated: 2026-10-28
---

## Description
The first tech tree (fun lane 39) cites about 45 archaeology and anthropology papers for the real-world firsts it relies on (Lomekwi 3, Wonderwerk, Kathu Pan, Blombos, Sibudu, Xianrendong, Shubayqa, Belovode, Plocnik, Botai...). The author, volume and page numbers were written from memory and not looked up. About 30 other dates are marked "unverified": textbook dates with no source checked. Under the provenance epic, check each cited row against the paper, then either fix the reference or downgrade it to "unverified".
- [ ] every `source` in techtree.toml checked or marked unverified
- [ ] the table in docs/review/techtree/techtree.md matches

## Updates
- 2026-10-28: Created from inbox draft draft-techtree-citation-check.md (found by fun39-techtree).
