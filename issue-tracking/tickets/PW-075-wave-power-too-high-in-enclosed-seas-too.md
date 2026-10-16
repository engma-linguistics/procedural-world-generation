---
id: PW-075
title: Wave power too high in enclosed seas, too low on India's west coast
type: task
status: in-progress
parent: null
subsystem: coast
effort: s
impact: low
found_by: deltas
blocked_by: []
relates: []
refs: [planet/coast.py, tools/coast_check.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
Wave power is ~2× too high in the Mediterranean, Baltic and Black Sea (fetch limits), and India's west
coast is too low (no monsoon swell). Faint straight streaks appear in the lee of islands (16 ray
directions).

## Updates
- 2026-10-16: Coast batch: stopped, needs a decision (draft draft-wave-storm-winds-over-land-locked-seas.md). The cause is the wave-driving wind, not the wave growth. Against rough climatological 10 m winds the model's U is 1.6-2.0x over the Mediterranean, Baltic, North Sea and Black Sea, 1.15-1.8x on NH open coasts and 1.0-1.3x on SH ones. The enclosed seas are in the NH and fetch-limited, so they get the NH storm excess (PW-074) plus storms that keep their strength behind land. Sound coast-side constants don't fix it (open-ocean refit each time): L_RECOVER 100 / 200 km take the enclosed rms from 1.61 to 1.55 / 1.44; T_STORM 24 / 36 h to 1.28 / 1.24, but the open rms goes from 0.53 to 0.69 / 0.83. India W is the weak July monsoon wind (PW-233). No code change.
- 2026-10-15: Status todo -> in-progress. Coast batch agent started.
- 2026-10-15: Smalls2: 24 ray directions with jitter, 1200 km fetch recovery; enclosed seas still high, India low from monsoon wind (drafts).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Coast.
