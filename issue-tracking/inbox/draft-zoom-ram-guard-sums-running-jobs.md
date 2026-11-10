---
title: Zoom RAM guard checks MemAvailable per request, not the sum of the jobs already queued or running
type: task
status: todo
parent: PW-1299
milestone: v1.0
subsystem: zoom
effort: s
impact: med
found_by: lane283
blocked_by: []
relates: [PW-1674, PW-1438, PW-1337]
refs: ["planet/api.py::zoom_estimate", "planet/api.py::free_ram_gb", "planet/api.py::Jobs.active_where", "planet/server.py::submit", docs/review/zoom/lod-plan.md]
---

## Description
**In plain words.** The zoom guard added in PW-1674 refuses a zoom when the free memory (Linux MemAvailable) at the
moment of the request is below the zoom's expected peak plus 8 GB, and it allows only one section-sized zoom at a time.
But a job that is queued, or has only just started, has not allocated its memory yet, so MemAvailable still looks
free: a 2 km section (25 GB) running beside three 1,000 km zooms or a refine, all submitted within a minute of each
other, each pass the check on their own and together can pass the cap. If never done, the guard protects against one
big click but not against several medium ones.

Fix to try: in `server.submit` add the expected peaks of the queued or running zoom (and refine) jobs, from
`api.zoom_peak_gb` / `refine.cost`, to the need before comparing with MemAvailable (subtract what the running ones have
already taken: their RSS, or simply count each job's full peak for its first minutes). Keep the one-section-at-a-time rule.
- [ ] a test with a fake `Jobs` holding two running 2 km sections' worth of peak and `free_ram_gb` patched shows a third request refused with the summed need in the message
