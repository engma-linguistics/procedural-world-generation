---
title: Shrink the L7 presence table on disk (uint16 deltas) - needs peoples runs re-cut
type: task
status: todo
parent: null
milestone: null
subsystem: store
effort: s
impact: low
found_by: lane111
blocked_by: []
relates: [PW-1269, PW-1259]
refs: [planet/lineages/output.py, planet/lineages/brief.py, viewer/globe/colours.js, "run b4d502"]
---

## Description
In plain words: lane 111 made the viewer's demes picker download one frame (about 0.74 MB raw, 0.22 MB gzipped, at L7), so the table's
size on disk is now only a disk cost: 103 MB of cell ids and shares in b4d502 (82 MB of it uint32 cell ids), plus 41 MB of demes_all.
Storing each line's ascending cell ids as uint16 deltas would cut the ids to about 41 MB (gaps over 65535 need an escape on the sparse
lines), saving about 40 MB (3%) of a 1.3 GB L7 run. It changes the on-disk format, so the five owner runs (b4d502, a24559, 3c1caf,
cc22df, 622c00) would not read unless the reader keeps both formats (against the no-backward-compat rule) or they are re-cut. Not done
for that reason. Worth doing only when the owner runs are re-cut for another reason.
- [ ] write_presence stores deltas; read_presence, `read_presence_frame`, brief and the viewer decode them
- [ ] a round-trip test with gaps over 65535
