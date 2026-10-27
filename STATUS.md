# Fun lane 37 handoff (PW-924 megafauna, PW-923 density trial)

## Done (committed)
- 87fff4c6 PW-924: counted megafauna (planet/lineages/history/megafauna.py): Damuth / Carbone & Gittleman densities (dragons 0.0002 = 1 per 5,000 km2),
  generation_yr 200 / 65, `group_size`, `rivalry` (metallics 0.5), `line_mvp` (megafauna only), linked pockets in `_viable`,
  megafauna competing among themselves in full, giants flagged megafauna, white dragons in cold mountains.
  Output: present.megafauna (per pocket count/country/landmass/groups, by_landmass, suitable_reached, target_met), run.txt section,
  brief v10 "Megafauna (counted)", viewer peoples panel (row "~N in P pockets"; a picked kind shows a "Counted" pocket list).
- Next commit: `MG.scatter` (new pockets now and then within 3 reaches, SCATTER_RATE 0.2/kyr), two inbox drafts, first cut of
  docs/review/megafauna/density-trial.html (+ trial.json).

## To finish
1. Re-render the report. The script is in the scratchpad (trial_report.py). Dot sizes are now sqrt and the land is drawn larger, but the last run was refused by the
   worktree guard. Run it as: `uv run --with matplotlib python <scratchpad>/trial_report.py docs/review/megafauna` with PYTHONPATH set in a wrapper
   script. Needs trial/{1000,5000,10000}/2a7385-7000.npz; those are still in the scratchpad.
2. Check the viewer: the peoples run **0f819d** is saved in the main data root (2a7385, dnd, 1 try). Run `PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation
   uv run python -m planet serve --port 8799 --no-open`, then `uv run --with playwright python <scratchpad>/shot.py 8799 0f819d <prefix>`. Kill the server by PID.
   Afterwards `planet delete 0f819d`.
3. Commit the report. Run pytest -m 'not slow' (687 passed at 87fff4c6) and tests/test_lineages.py (91 passed with scatter).

## Findings (2a7385 dnd 7000, 1 per 5,000)
- ~18,100 coloured dragons, plus ~13,000 of no set colour (mostly the metallic stem). Metallics dominate: gold ~6,800, and chromatics are tiny
  (red ~23, black ~39, blue ~30). The cause is metallic rivalry 0.5 plus the broad stem niche. The regional 3,000 km square holds ~3,200 at
  1 per 5,000 and ~330 at 1 per 10,000, so "expect ~10 here" needs 1 per 10,000 or sparser, or narrower countries.
- Target (suitable_reached): dragons mostly 0.6-1.0 (chromatics 0.1-0.7). Giants fall short: hill 0.11, cloud 0.16, frost 0.51, fire 0.0-0.43.
- Storm giants: ~56,000 in open sea (draft draft-storm-giants-open-sea-not-coasts.md).

## Gnome remnants (PW-931, gnomes at 50 kyr; the code with PW-924), cells >= EST at the present
- 2a7385: 7000 3305, 7001 7243, 7002 **26**, 7003 641
- 1df1c3: 7000 986, 7001 170, 7002 **87**, 7003 2936
- Remnants (<100): 2 of 8 (2a7385 7002, 1df1c3 7002). Under 300: 3 of 8.
