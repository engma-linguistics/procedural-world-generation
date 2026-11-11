---
title: "test_zoom_sections fails under every 16 GB-capped pytest: the section RAM guard now sees the cgroup cap"
type: task
status: todo
parent: null
milestone: v1.0
subsystem: zoom
effort: xs
impact: med
found_by: lane313
blocked_by: []
relates: [PW-1731]
refs: [tests/test_zoom_sections.py, planet/api.py::free_ram_gb, planet/api.py::zoom_estimate]
---

## Description
In plain words: the standard test command (pytest inside `systemd-run ... -p MemoryMax=16G`) always reports two
failures now, so a lane can't tell its own failures from these.

Since `api.free_ram_gb` honours a cgroup memory cap (PW-1731), `api.zoom_job`'s `_require_room` sees at most ~11 GB of room
under the 16 GB pytest scope. A 4000 km section at 2 km/px asks for about 25 + 8 GB, so
`test_section_builds_then_is_reused` and `test_listing_marks_built_sections` raise "not started: not enough free memory".
They stub the build (`stub_build`), so the guard is not what they test. Reproduced on an unmodified export of the lane313
branch base (eaa93062), run alone with `-n 0`: 2 failed, 7 passed.

The fix probably belongs in the tests: monkeypatch `api.free_ram_gb` the way the stubbed build is faked. The guard
itself should stay as it is.

- [ ] `uv run pytest tests/test_zoom_sections.py` passes inside a 16 GB scope
