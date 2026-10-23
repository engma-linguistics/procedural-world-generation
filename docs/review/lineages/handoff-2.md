# Lineages lane 2: handoff (2026-10-23, ~100 tool calls)

Design and the lane-2 mechanisms: `docs/proposals/lineages.md` ("Lane 2 additions"). Code: `planet/lineages/` (new: `crossing.py`). Tests: `tests/test_lineages.py` (9, ~1.5 s). Showcase: `docs/review/lineages/showcase-2.md`.

## Built
1. **Sea crossings**: land bridges stay implicit in each epoch's land, and are now named as events. Long crossings work as a Poisson chance per step and per landmass a line doesn't hold yet: rate x exp(-gap / L) by way (`spec.HOPS`: raft, coastal, swims, flies, seafaring). The gap is the sea distance from the line's own coast, found by a sea-only BFS in numba, so island chains act as stepping stones. Crossings are drawn about once a kyr. Each arrival on a present-day landmass is recorded (`meta.lineages[].reached`) with when, how and the gap.
2. **Mixing concentrated by mechanism**:
   - A contact value per cell (`crossing.corridor`).
   - Territorial competition: alpha_eff -> 1.4 in closed country for peoples with alike ways of life.
   - Displacement: a people held above its room declines toward it.
   - Late mixing scaled by contact.
   - Farmers push only on farmland.
   - Safeguards: split founders hold 400 km of suitable country; living lines hold a refuge instead of vanishing; split origins need habitat.
3. **Globe**:
   - Overlay "Peoples' origins and tracks": rings at the origins and centroid tracks up to the current frame; a picked people only, if one is picked.
   - A `peoples overlay` layer (templates, contact hybrids).
   - Hover rows: this frame's leading people, share and mix count, the overlay, and every people's share at the present (`presence_present.bin`, fetched lazily).
   - The picked people's story in the panel; the mixing summary and empty continents in the panel.
4. **Server**:
   - `POST /api/lineages` is queued on the job queue (`api.lineages_job`, `api.parse_lineages_request`); the editor polls `/api/jobs/<id>`.
   - `store._run_item` carries `phase/timezoom/world`. `family.py` nests phase runs under their time zoom, and `navigator.js` labels them ("Peoples on world X", "Recent pass") with an "Open its tree in the editor" link (PW-600 lean A).
5. **Wishes and stories**:
   - New place wishes `jungle`, `steppe`, `desert`, `tundra`, `island_chain`. The editor lists them, and the preset adds goblin-jungle and orc-steppe (weight 0.5).
   - Place-wish scores combine coverage and enrichment.
   - Per-people game-ready stories (`meta.lineages[].story`, `meta.present.stories`, `run.txt` "Stories").

## Numbers (dnd preset, L6, one try each, lane 1 -> lane 2)
- Mixing area at the present: 119973 58 -> 27 Mkm² (38% -> 18% of the land); 81aced 74 -> 57 (44% -> 34%); c00ebf 61 -> 24 (45% -> 17%). Corridor land is 25-66% mixed; closed land is 10-17%.
- Island wishes (new score): 119973 tortle 0.82, aarakocra 0.03; 81aced aarakocra 0.81-1.0, tortle 0.48-0.71; c00ebf aarakocra 0.57, tortle 0.15. Lane 1 scored 0.0-0.17 by its own measure (share of range on islands).
- Empty continents: on 119973 the 18 Mkm² continent is 4300 km of ocean away. It was held 0.79 in one try and empty in others. c00ebf: empty in some tries.
- Cost: ~27 s a try at L6 (lane 1 ~20 s). L7 is ~6-10x slower.

## Not done / next
- L7 is slow: the per-line competition matvecs over all cells dominate (`history.run` ~60% of the time). Restricting the per-line arrays to land cells would cut it ~3x. That is a refactor of `History`; flag it for a yes.
- Inbox drafts: `draft-lineages-near-wishes-after-exclusion` (needs-decision), `draft-lineages-empty-remote-continents` (needs-decision), `draft-lineages-corridor-tuning`.
- Owner decisions still open: PW-598..601 (leans kept).

Stored outputs: the showcase runs are listed in `showcase-2.md` (kept). Test run 2c86b7 was deleted. Showcase runs kept: 037790 (1144ce), 06a854 (31926a), 2dcc80 (91448a), dfcbd2 (3e0b0a).
