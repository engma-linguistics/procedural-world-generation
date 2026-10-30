---
id: PW-1033
title: Peoples editor keeps hand-copied option lists that have gone stale (no \"food\" setting, two traits and five goods missing)
type: task
status: done
parent: null
milestone: null
subsystem: viewer
effort: s
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-795, PW-990, PW-992]
refs: [viewer/lineages.html, planet/lineages/spec.py, planet/lineages/land.py, planet/server.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The peoples editor in the viewer keeps its own copy of the lists of traits, goods and settings, and that copy is out of date. You can't tick "aggressive" or "hunter", five land goods are missing, and the dragon density menu has no "food" option (your 10-29 choice), so opening the D&D tree shows "from the prey (default)" even though the tree says food. The editor only writes a setting when you change it, so nothing has been lost yet, but what you see is wrong.

Verified on main b36c9581: `viewer/lineages.html:100-123` mirror lists vs `spec.TRAITS` (adds `aggressive`, `hunter`), `land.GOODS` (adds `fish`, `shellfish`, `salt`, `salt_rock`, `sea_mammals`), `spec.MEGAFAUNA_NATURAL = ('food','prey','mesotherm','mammal')` with default `food`. The select at `lineages.html:627` offers prey/mesotherm/mammal only, labels prey the default, and its tooltip still says "Candidates until the owner's review (PW-967)". The era select at :490 still says "nothing reads it yet", but techtree caps at `meta.era`. No fields for `way`, `realm` (PW-795), `megafauna`, `mass_kg`, `group_size`, `rivalry`; `BODY_FIELDS` has no `grain`.

Fix: a `GET /api/lineage-schema` built from spec (TRAITS, PLACES, GROUPS, WAYS, BODY_DEFAULT/choices, DEMOGRAPHY, MEGAFAUNA_NATURAL with labels and default, dragon schedules) and land.GOODS; the editor renders its lists from it. Add a test that the editor has no literal copies left (or, at minimum, a JS-vs-Python parity test in the style of test_projection_js.py).
- [ ] traits, goods, megafauna modes and defaults come from the server
- [ ] stale "candidates" and "nothing reads it yet" texts gone
- [ ] parity or no-literals test

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Status todo -> done. Fix lane 49: GET /api/lineage-schema (lineages.run.editor_schema: spec TRAITS, PLACES, GROUPS, WAYS, REALMS, BAND, DEMO_DEFAULT, DEMOGRAPHY, BODY_DEFAULT, BODY_CHOICES, TOXINS, ERAS, MODES, PORTAL_MODES, MEGAFAUNA_NATURAL with new spec.MEGAFAUNA_NATURAL_LABELS, dragon_ages SCHEDULES and GENERATION, land.GOODS labels, and the defaults). viewer/lineages.html loads it first (loadSchema) and renders traits (aggressive and hunter now there), goods (33, with fish, shellfish, salt, salt_rock, sea_mammals), body fields (grain and milks now there), era, mode, arrivals, megafauna density (food, the default), dragon ages (younger, the default: the editor said base), dragon generation, and the density / viable population / land pull defaults from it; only menu wording stays in the page. Stale 'Candidates until the owner's review' and 'nothing reads it yet' texts rewritten (also spec.ERA_DEFAULT's comment and dnd.toml's era comment). Test: test_viewer.test_peoples_editor_has_no_copied_option_lists (no two neighbouring values of any schema list appear as a literal sequence). Checked live (test server, headless Chrome): no page errors, dnd tree shows food and younger selected. Fields for way, realm, megafauna, mass_kg, group_size, rivalry: inbox draft (new UI).
- 2026-10-29: Created from inbox draft draft-peoples-editor-reads-spec-schema.md (found by code-audit-2026-10).
