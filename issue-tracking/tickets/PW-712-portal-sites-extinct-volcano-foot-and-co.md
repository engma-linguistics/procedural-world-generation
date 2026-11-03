---
id: PW-712
title: "Portal sites: extinct-volcano foot and coral reef are approximated (young volcanic ground, coral coast good)"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: xs
impact: low
found_by: fun4
blocked_by: []
relates: [PW-697, PW-607]
refs: [planet/lineages/history.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Portals at "interesting sites" (`meta.portal_mode = "sites"`, `History.portal_cells`) use what the tags and goods give:
forest and desert depth are exact (successive erosions of the tag, so the deepest part of the largest patch); "reef" is the
land cell with the highest coral-coast good (a reef lies offshore; the portal sits on the nearest coast); "volcano" is
the land ring around the world's volcanic ground (land.goods `volcanic`, young volcanic ground and volcanoes), not
specifically an extinct cone (the world has no active/extinct flag per volcano). Also not yet possible: the "arrival-site
crystals" of PW-607 (a likelihood layer around the portals, a world-side feature that needs the portals stored with the world, not the peoples run).
Next: if the volcano list in the world meta gains an age, prefer extinct ones; put the reef portal on the sea cell and found the people on the nearest coast;
store the portals where a world-side crystal layer can read them.

## Updates
- 2026-10-23: Accepted as approximations for now; store portals world-side when PW-607's arrival-site crystals are built.
- 2026-10-23: Created from inbox draft draft-portal-sites-extinct-volcanoes-and-reefs.md (found by fun4).
