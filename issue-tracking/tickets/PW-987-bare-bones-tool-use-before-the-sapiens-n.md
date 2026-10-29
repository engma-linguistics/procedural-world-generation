---
id: PW-987
title: Bare-bones tool use before the sapiens node is the same knapping and handaxes for every stem with hands
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-44
blocked_by: []
relates: [PW-971, PW-978, PW-947]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml]
created: 2026-10-29
updated: 2026-10-29
---

## Description
PW-971 gates the tech tree on a stem's sapiens node: before it only techs marked `bare = true` arise (knapping, handaxes; the Lomekwi/Oldowan/Acheulean shape). That gives the felines, goblinoids, hominids and the avian stem the same two techs on the human dates (knapping from 3.3 Myr, handaxes from 1.76 Myr), and the dragons none (no hands). Two things are crude:
- The avian stem (6 Myr, node 2 Myr) has a long pre-mind run of "knapped stone" and "shaped handaxes", where crows and capuchins would use found tools, hooks and flaked hammerstones. A separate bare tech for birds (probing and hooked tools, Weir 2002) would read better.
- The cat stems (feline) have hands in the model, which is itself doubtful.
Also gesture and call systems are gated by the node (a dragon's kit still brings them with innate_magic). If the owner wants animal calls to be ungated, `gesture` can take `bare = true`; then language alone waits for the node.
Lean: leave as is until the language project (PW-947); then give each body plan its own bare tool.

## Updates
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: birds use found tools before sapience, not knapped stone. Felines have hands once genetically modern, and so do the bird-peoples. So each body plan gets its own bare tool: found or probing tools for avian stems, with knapping only where hands exist pre-node.
- 2026-10-29: Created from inbox draft draft-bare-bones-tools-for-handless-and-bird-stems.md (found by fun-lane-44).
