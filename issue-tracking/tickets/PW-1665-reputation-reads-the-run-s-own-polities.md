---
id: PW-1665
title: "Reputation reads the run's own polities: a people ruled by another's state for centuries remembers it as 'resented'"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane276
blocked_by: []
relates: [PW-756, PW-731, PW-785]
refs: ["planet/lineages/reputation.py::_view", "planet/lineages/reputation.py::parse_events", planet/lineages/output.py, "planet/lineages/polities.py::derive", "planet/lineages/polities.py::step_view", "planet/lineages/history/params.py::POLITIES_LIVE", "tests/test_lineages.py::test_an_authored_polity_is_resented_by_the_ruled_and_compact_ranges_give_a_direction"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Lane 276 added a 'resented' memory: "these people ruled us". Today only a hand-written `[[event]] kind = "polity"` row in a tree
makes it. The run's own states and empires (the polities map) never do, so the map can show the antelope-kin ruling humans for
five centuries while the humans' reputation row calls the antelope-kin by their own name, as peaceful neighbours.

## Description
`reputation.build` runs inside the peoples run (`output.py`, `meta.present.reputation`), from the contact record. The polities are
derived later, at read time (`polities.derive`; `POLITIES_LIVE` is off by default), so the reputation pass cannot see who ruled whom.
What breaks if never done: the brief's and the viewer's "what the peoples call their neighbours" contradicts the polities map and the
invasion read-out on every run with states. The authored `polity` anchor only covers trees whose author wrote the row.

What to try: a read-time pass (beside the polities read-out, cached with it) that turns each polity's subject peoples (the people of
the ruled cells, `step_view`'s `subjects`) and its ruling people (`peoples` spans) into resented candidates: strength from the share
of the subject people's land ruled and the years ruled, fading from the fall like the authored kind (`EFOLD_KYR` x the era scale).
Then authored polity rows become the fallback, as authored conquests already are for derived incursions. Mind the cost: per subject
people per polity over ~126 century steps.
- [ ] a people ruled by another's polity for at least N centuries carries a 'resented' row naming its rulers, with the dates
- [ ] authored `polity` rows stand only where the run's own polities found no rule of S over O
- [ ] the brief and the Peoples tab read the same rows (no second table)

## Updates
- 2026-11-10: Created from inbox draft draft-resented-from-the-runs-own-polities.md (found by lane276).
