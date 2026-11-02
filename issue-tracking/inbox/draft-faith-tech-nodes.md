---
title: "Tech tree: faith steps on the social track (moralizing high god after temples + kingship) and a divine-magic node on the arcane track, gated by gods mode"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: religion-doc-chat
blocked_by: []
relates: [PW-696, PW-675]
refs: [planet/lineages/samples/techtree.toml, docs/references/tech-catalogue/knowledge.toml, planet/lineages/techtree.py]
---

## Description
In plain words: big moralizing gods appear only once a society is organized enough, with temples and rulers. The tech tree
already has spirit_ritual -> temples (needs villages), kingship and writing on its "Social and ritual" track. Add the faith steps
there, and the gods' individuation reads them.

Daniel's ruling (religion doc, https://claude.ai/artifact/Tk4g2nkJPQpTJgeDXo6KoP (Claude Docs id d890d9ce-3695-47c4-add1-a21c3c1a3bf2); comment on "Big Gods"): put it on the tech tree, as a hazard (soft, never a law).
- Social track: a "moralizing high god" node (needs temples + kingship). The catalogue is real-world sourced: cite Norenzayan
  2013, and note that the Whitehouse et al. 2019 Seshat result was contested (check its retraction status before citing).
- Arcane track: a "divine magic" (clerics) node that needs temples. It exists only when gods_mode is faith_made or absolute. It is
  kept separate from the rest of magic (PW-696, v3) so that belief-only worlds still get the faith steps.
