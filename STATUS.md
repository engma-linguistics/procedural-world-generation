# Fun lane 38 handoff (PW-936, PW-937, PW-931)

## Done (committed)
- 97cdb6f7 PW-923 owner ruling: `meta.dragon_km2` (default 5000) sets every dragon kind's density; workbench select + tooltip.
- Next commit: PW-936 fix 1 (megafauna.metapop_km: the viable fade links pockets within scatter reach, SCATTER_LINKS x link_km)
  and PW-937 (line_mvp for every line; also used by _jump founders and polycentric founder patches).

## PW-936 diagnosis (2a7385 dnd 7001, one roll)
- main: 7/15 kinds >= 0.5. Dragons were in reach of ~all their country and held ~all of it once; losses were the viable fade
  (red 0.64, black 0.50, copper 0.35) and competition (gold 0.39, silver 0.28).
- fix 1: 12/15. Short: hill 0.11, cloud 0.16, frost 0.43 giants: never in reach (walkers). Draft: draft-giant-coverage-reach-and-people-pressure.md.
- fix 1 + peoples press megafauna at MEGAFAUNA_PUSH: 13/15 but counts x3-40, elves 757 -> 222 cells. Not merged (in the draft).

## Still to do
1. Acceptance sweep, 6 planets x 4 rolls (7000-7003), dnd, one try each (~55-70 min per run; 5-6 at once):
   - base (main) results: scratchpad out/base-*.json (batch may have died with the agent; rerun missing ones)
   - after: code snapshot scratchpad after/ (fix1 + 937)
   - optional: p937/ (main + 937 only) to separate 937's effect on remnants
   Tools in the scratchpad (/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad):
   probe.py (DIAG=1 for per-kind loss attribution), run1.sh TAG CODEDIR WORLD SEED, batch.sh TAG CODEDIR NPAR "worlds" "seeds", patch.py.
   Example: `bash batch.sh after <scratchpad>/after 5 "2a7385 1df1c3 e71172 6909cb a12762 067778" "7000 7001 7002 7003"`
2. Report: main-people (human elf dwarf halfling gnome orc goblin) remnants <100 cells, per-people >=300-cell pass rate,
   megafauna coverage (kinds >= 0.5 on 2a7385/1df1c3 x 3 rolls) and counts per kind; gnomes at 50 kyr (PW-931).
3. PW-937 is needs-decision on the board: the sweep is its evidence for the owner.
