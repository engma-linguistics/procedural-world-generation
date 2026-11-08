---
title: "After the merge: rebuild the a24559 languages, regenerate the sketches and demo, and have a fresh linguist agent read them cold"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: high
found_by: lang-design (grammar D, polish lanes, queue.md, 2026-11-08)
blocked_by: []
relates: [PW-986]
refs: [docs/review/language/queue.md, docs/review/language/grammar-gaps.md, docs/review/language/handoff.md, docs/review/language/demo-read-4.md, docs/review/language/sketches/, tools/language/sketch.py, tools/language/demo_page.py, "run a24559"]
---

## Description
In plain words: the language pages Daniel will read (the per-language sketches and the demo page) were last
regenerated before the grammar D, faiths, polish and sound-pass-2 work, and every review so far was done by the lanes
that wrote the code. Before the language work is called done, a fresh agent with a linguist's brief should read the
regenerated pages with no context and list what looks fake. If skipped, the pages Daniel sees are stale and the only
reviews are by the authors.

**Now.** `runs/a24559/languages.json` is from the finish lane (11-08 morning); later lanes ran scratch passes only.
`docs/review/language/sketches/` tracks that file. Demo version 4 (https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs)
predates the polish lane; its regenerated build is in the polish lane's scratchpad. Queue rows "cold review" and the
grammar-gaps Phase D item "a last-pass reviewing linguist" are open.

**Wanted.**
- [ ] after lang-design is on main: `planet languages a24559` in place (note lanes-rebuild-shared-runs: do it from main,
  not a worktree), then `tools/language/sketch.py` and `demo_page.py`; all checks but the accepted horizon pass
- [ ] republish the demo to the same artifact URL
- [ ] a fresh agent (read-only, no lane history) reads 6-12 sketches and the demo as a historical linguist; findings
  written as one review file in docs/review/language/ and folded into the page-slips ticket or new drafts
