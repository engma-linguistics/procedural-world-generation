---
title: "Backlog housekeeping: merge 6 duplicate pairs, rescope 3 overlapping tickets, close 2 stale ones"
type: task
status: todo
parent: null
subsystem: docs
effort: s
impact: low
found_by: docbacklog
blocked_by: []
relates: [PW-048, PW-172, PW-095, PW-185, PW-083, PW-187, PW-097, PW-077, PW-188, PW-071, PW-129, PW-088, PW-131, PW-098, PW-155, PW-089, PW-051, PW-191, PW-096, PW-047, PW-186, PW-056, PW-135, PW-039, PW-112, PW-037, PW-189]
refs: [docs/backlog.md]
---

## Description
Found while writing `docs/backlog.md` (§3.11), from reading every open ticket on main at 382b370.
Coordinator edits only. No code involved. Each item can be applied independently.

**Merges (close the first ticket into the second, carrying anything unique across):**
- [ ] PW-048 into PW-172. PW-172 is the diagnosis of PW-048's one-frame 12+ km spikes, with options.
- [ ] PW-095 into PW-185. Both are soils. PW-185's soil set includes cryosols (permafrost) and histosols (peat). Add "permafrost extent (continuous / discontinuous)" and "wetlands" to PW-185's checklist. Zoom wetland drawing is also PW-178 / PW-094.
- [ ] PW-071 into PW-129. "Finer zooms at 100-250 m" and "nested fine zoom at 100-250 m" are one feature.
- [ ] PW-088 into PW-131. PW-131 is the concrete fix for big checkpoints. Keep PW-088's "dead plates keep full-grid arrays" idea.
- [ ] PW-077 into PW-097 (coast form), after the rescope below.

**Rescopes (retitle and edit the description):**
- [ ] PW-083: retitle to "Satellite (true-colour) view of the globe and zooms". Drop the vegetation part (now PW-187). Add `blocked_by: [PW-187]` and consider parent PW-184. Its old condition "after PW-005 and PW-001" is met (both done).
- [ ] PW-097 / PW-077 / PW-188: mangroves are in all three, reefs in two. PW-188 owns the biology: reefs on non-volcanic coasts, mangroves, kelp, seagrass. PW-097 becomes coast *form*: cliffs vs beaches, spits, beach ridges, dendritic tidal channels (from PW-077), and barrier islands beyond coastal plains (the zoom has drawn barrier islands and lagoons on coastal plains since PW-012).
- [ ] PW-098: move the resource list to the PW-155 epic. Retitle PW-098 to "Static hazard maps: earthquake, volcanic, tsunami, flood zones" (low priority per the owner's 2026-10-14 note).
- [ ] PW-096: dune fields are done (landform class, PW-176; zoom synthesis, PW-012). Retitle to "Loess downwind of outwash and deserts". PW-177 stays as its child.

**Stale or likely done (verify, then close):**
- [ ] PW-089: `timeline.slice_world` already warns when the run's code differs ("The replay may not reproduce it"), and `ReplayMismatch` says "use --force". That was the ticket's ask under the no-backward-compatibility rule. Close as done.
- [ ] PW-051: the "-250 m clip" is gone. PW-053 (0fd35e5) replaced it with a 30-Myr smoothing and a tanh limit, and set equilibrium start ages (mean 60 Myr). Re-measure the L6 mean ocean age (`tools/sealevel.py`). If it's near Earth's, close into PW-191, which holds the remaining L7 few-plate ageing.
- [ ] PW-047 (ragged ocean plate boundaries): last checked on v1 worlds. Look at a current showcase's plate layer and close it if it's no longer visible.
- [ ] PW-182: close at the next showcase run (it resolves itself).

**Links and blockers:**
- [ ] PW-187: add `blocked_by: [PW-186]` (the model waits for the approved proposal).
- [ ] PW-091: consider `blocked_by: [PW-031]` (finished worlds would be buried in ice otherwise).
- [ ] PW-056: relates PW-135 (rift-flank uplift is its stated likely fix). PW-039: relates PW-112 (same warm polar bias).
- [ ] PW-037: note that PW-189 owns the depression and rebound mechanism; the imprint only records it.

**Informational:** 13 open tickets still have a parent epic that is done: PW-001 (PW-116..119) and PW-005 (PW-130, 132, 135, 136, 147, 165, 168, 175, 179). It's valid, but `tree` lists them under closed epics. Either leave them or set `parent: null`. PW-117 is the only `needs-decision` left; under the owner's north star the coordinator could take its lean (A).
