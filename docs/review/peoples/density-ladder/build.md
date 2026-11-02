# The density ladder, built (PW-1275 step 2): lane 136 state for the hand-off

Lane 136, 2026-11-02. **Work in progress: built and tests green, not yet judged.** The before/after suite is running; the
results page for Daniel (plain words, tables, charts) is still to write from it.

## What is built (commit on this branch)

- `planet/lineages/ladder.py` (new): the shared ladder. Per line, per cell: density = kind x sum over its ways of life of
  (share living that way there) x (that rung there). Rungs and numbers are in its docstring and `TABLE` (sources: `ladder.md`):
  forager 0.036 at NPP 330, power 1.3 (Binford fit; Q3 C); fisher 1.2 x the fish good above 0.2; garden 5; plough 8 / 14 / 25 by
  stage, at most 35 a cell (Q7 A); irrigation 30 -> 240 per watered km2 on the floodplain share only (Q5 A); nomad 0.8 at grazing NPP
  263; agro-pastoral = a cell both farmed and herded; dwarven hold = valleys' farming x trade (cap 0.5 of food, placeholder) + 0.1
  mushrooms (Q6 A); den peoples forager x kind 1.2 / (1 - raid share), raid share capped at 0.3, half-cap at 5 farmers+herders /km2
  within 2 rings (Q4 A), farming at 0.1 weight.
- Who lives which way (Q2 A): cultivation known (a crop taken up) -> the fertile good / 0.5 of a cell farms; herding known (a herd
  animal) -> grazing land outside the fields herds; the rest forages or fishes. Tech stages inside the history are proxies (the tech
  tree runs after the history): plough stage from the time since a plough animal (iron +3.2 kyr, medieval +5.3, the tree's Earth dates),
  irrigation 3.5 kyr after cultivation, holds' terraces 6.5 kyr after cultivation; capped by meta.era.
- Spec: per-people `density` / `band_km2` are gone (parse raises with a pointer); `kind` (0.5-2, default 1) replaces it. dnd: goblin,
  kobold, troglodyte 1.2 (troglodytes get `denning`); tabaxi, leonin 0.8. DEMOGRAPHY trait densities removed.
- PW-1357: dnd groups removed (human farmer/herder/nomad/seafarer/arctic, steppe/forest orc, hill dwarf), their wishes and uses; the
  orc pair kept as a note in the dnd header for Seven Meals. City minorities (city goblins/kobolds) kept: they are not a way of life
  (judgement, ask Daniel). Seven Meals keeps its groups (only its densities removed).
- PW-1351: halfling way farmer, gnome horticulturalist, dwarf farmer; crops no longer exclude `subterranean` (holds and dens may farm).
- History: `model.py` builds `self.kx` (kind x band nudge) and `self.ladder`; `growth.py` refreshes the ladder each step (era dens and
  ERA_DENSITY removed); `dens[k]` is now the line's mean over held land (Q1 A). Land use per cell reads the ladder's farm/herd shares
  (`landuse.frame_inputs`); saved demography carries the realized density (landuse.derive, demes, techtree read it).
- Viewer: Peoples workbench shows "kind x" and "rung · /km2" (main rung, mean density; hover: its rungs and the whole ladder);
  results column likewise; schema gains `ladder` and `kind_range` (`run.py`).
- `tools/peoples_robust.py`: knob family moves the kind factor; per people it records `density` (people / held km2) and `ways`
  {rung: [people, held km2, people at full presence]}.
- Tests: obsolete density tests rewritten (`test_people_density_reads_the_ladder`); no-world tests set `h.dens` where they need a
  number (no world means no ladder). Lineage, peoples, niche and zoom-peoples tests pass (152); full `pytest -q -m "not slow"` not yet run.

## First look (one dnd run, seed 7, world 4360a3, before the fish/water fixes)

human 26%, hobgoblin 16%, kenku 11%, orc 9.5%, dragonborn 8.5%, halfling 8.3%, tabaxi 7.9%, elf 6.9%, leonin 3.4%; dwarves 0.03% (they
could not farm: fixed since by dropping crops' `subterranean` exclusion), troglodytes extinct. Everyone who learns cultivation farms,
so the hunting kinds (tabaxi, leonin, goliath, bugbear) now garden or plough over much of their land.

## Weird things to check (and warn Daniel about)

1. **Q1 A and presence.** Population = presence x density x area, presence <= 1, so a line's realized mean is below its rung's number.
   The suite now records the rung at full presence per rung (`ways[r][2]`): realized / that = mean presence. If it is far from 1,
   either divide by it (a calibration constant) or tell Daniel the rung is "at full habitat".
2. Irrigation was labelled on any riverside cell (flow >= 1: half the land). Raised to flow 5-200 (~15% of land); check its share.
3. Fishers took every cell with any fish good; now only above 0.2. Check foragers vs fishers.
4. The forager rung (Binford median fit, 0.036) is ~8x below the old 0.3 (upper quartile, D20): non-farming peoples fall a lot; small
   islands may lose sparse peoples to the viable-population fade.
5. Lactase: the human herders' milk share went with the groups; humans have none now (draft).
6. goblin_world (authored stress tree) lost its 6 / 1.5 / 5 densities (kind defaults now).

## Running (scratch: /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l136)

- Before: `base/` (git archive of main fc4e0398) -> `out_main/`, families base, jitter, subset, knob (48; 12 done earlier, plus
  some authored), `--jobs 2 --threads 1`, log `main_run2.log`.
- After: `branch/` (this branch's working tree as committed) -> `out_branch/`, same 48, `--jobs 2`, log `branch_run.log`.
- ~390 s a run, ~2.5 h each. Report: `tools/peoples_robust.py report --out DIR` from each snapshot dir, with
  `PLANET_DATA=/data/personal/repos/procedural-world-generation` and the worktree's `.venv/bin/python`.

## Next steps

1. When both suites end: species shares main vs branch (humans' share), ways of life by people (`ways`), density by rung vs ladder.md's
   ranges, extinctions / monopolies; PNG charts here (before/after shares; rung densities against the sourced bands); a short plain
   results page for Daniel at the top of this file.
2. Full `uv run pytest -q -m "not slow"`; goldens only if outputs changed on purpose (say why).
3. Inbox drafts to file (none written yet): Q1 presence calibration (if it stays); tech stages from the tech tree inside the history;
   lactase share for humans without herder groups; trade for holds (placeholder until trade exists); landuse.derive still uses static
   shares; city minorities as groups (ask Daniel); early-modern rung (already on the wishlist); raiding share unsourced as a number
   (sources below); goblin_world's lost densities.
4. Backfill refs on PW-1275 / PW-1350 / PW-1351 / PW-1357 (planet/lineages/ladder.py, this page).

## Raiding: the sources read (a subagent of this lane, 2026-11-02; quotes verified in the texts it opened)

No measured share of food from raiding was found; raiding is a top-up to a herding or foraging base.
- Opler 1941, *An Apache Life-Way* (U Chicago), p. 332 (Chiricahua): "For men, raiding approaches hunting in economic significance."
- *Encyclopedia of World Cultures* (Gale 2008), "Western Apache - Economy" (secondary): ~40% gathered plants, 35% meat, 25% horticulture;
  raided stock sits inside the meat share.
- Burckhardt 1831, *Notes on the Bedouins and Wahabys* vol. 1, pp. 71-72: herding alone does not cover the Aeneze's yearly costs; "war
  and plunder therefore become necessary".
- Khazanov 1994, *Nomads and the Outside World*, pp. 221-222: raids "an important supplementary means of livelihood", "too unreliable";
  p. 187: the Maasai raided agriculturalists, the Samburu (among pastoralists like themselves) could not; p. 155: raids among nomads only
  circulate livestock.
- Hendrickson, Mearns & Armon 1996, IDS Bulletin 27(3) (abstract only): Turkana raiding as livelihood-enhancing, turning predatory.
Cap 0.3 and half-cap 5 /km2 are judgements on these.
