---
id: PW-339
title: "Zoom drainage tie-break jitter isn't planet-fixed: drop counts and networks move with the grid"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch2
blocked_by: []
relates: [PW-319, PW-321, PW-125]
refs: [planet/zoom.py, "world 592f2a"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The landscape pass breaks ties in the priority flood with `jitter = np.random.default_rng(seed).random(npx)`:
one random number per pixel *index*, so the same planet point gets a different tie-break in a zoom of
another size, centre or halo (PW-321 added a halo, which reshuffled it everywhere). Everything else in the
zoom's noise is sampled at 3D planet positions.

Measured on world 592f2a (zoom batch 2): reseeding only this jitter moves the undesigned-drop count
(`stats.falls` kind `drop` >= 100 m) on the 8 showcase zooms from 33 to 31-39 without a halo and 36-44
with it (5 seeds on 5 zooms: no halo 31-39, mean 34; halo 36-44, mean 40); the arc zoom alone 25-28 vs
29-33. So the "33 drops" baseline is one draw of a +-4 spread, and overlapping zooms of one place don't
share their drainage tie-breaks (part of PW-125's tile mismatch).

To try: sample the jitter from planet-fixed noise at the pixel's position (`ZK.fbm(Pk, ~res, ...)` or a
hash of the rounded 3D position), so overlapping zooms tie-break alike; and measure drop counts as a mean
over a few seeds.
- [ ] jitter planet-fixed; drop counts reported as mean +- spread over 3-5 seeds

## Updates
- 2026-10-16: Status in-progress -> done. Done (46c192b): planet-fixed tie-break noise (zoom.tie_jitter); overlapping zooms share 42% of receivers (was 31%).
- 2026-10-16: Status todo -> in-progress. Zoom batch 3 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-drainage-jitter-not-planet-fixed.md (found by zoom-batch2).
