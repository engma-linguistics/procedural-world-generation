# Lane A handoff A9 (2026-10-22, ~95 tool calls)

## State of the branch
- Main is merged in, and so is `worktree-agent-ab29d25d923997afd` (PW-582 attempts 1 and 2, and the lakes-test
  harness).
- Rulings 1–3 are commit 17335b3 (stages.md, "PW-582, attempt 3 of 3"). `uv run pytest -q` passes (568), and the
  goldens are regenerated. The scorecard line follows in its own commit.
- The bar is missed: Fennoscandia −6.5 against ±6, the Barents frozen (−13.3), and Iceland −11.6 against −7.8.
  Overall it is an improvement: the Nordic Seas −3.1, the Norwegian coast's sea air 3.4 C, Baffin's warm bias gone,
  NH 11.9 Sv at 91% open polar sea, and the weak southern worlds stronger.
- PW-582's three attempts are used. What is left is in `issue-tracking/inbox/draft-barents-still-frozen-after-pw582.md`
  (needs-decision).
- `issue-tracking/inbox/draft-timezoom-index-zero-drift-spread.md`: the I = 0 drift ranges from −0.1 to −29 m over
  plausible worlds, so the 25 m bound is inside the spread. The harnessed test passes today because the first
  plausible seed is under it. The next ocean change may pick another seed, which is still a coin toss on the bound.
- PW-579 and stage 3 are not started. The notes in `handoff-A6.md` still stand.

## Tools (`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA9/`)
- A8's tools pointed at this worktree: `probe.py` / `pr.sh`, `nordic.py` / `nr.sh` (now also maps `icelid`),
  `meas.sh` (lighter thread counts), `melt.py`, `tz.sh`, `walin.py`.
  - `probe.py` and `nordic.py` take `WT=<tree>` to probe another tree. `head/` is HEAD before attempt 3 and `main/`
    is main; both are extracted with `git archive`.
- `tzseed.py ROOT SEED MYRS` / `tzrun.sh ROOT TAG MYRS seeds...`: the cold_moment's precondition stats and its I = 0
  drift per seed (`tz_*.txt`: main, br = attempt 2, a3).
- `strait.py`: `_straits`' cross-sections at named straits, and a map of the Arctic.
- `headmeas.sh`: the before-measurements on `head/`.

## PW-579 (next)
The `handoff-A6.md` notes still stand. Two things to keep in mind:
- The Arctic branch adds lid-edge cells to `m` in `ocean.overturning`. The deep-water reference uses `mo`, the open
  cells only. A ρ_d entrainment reference should keep to open cells too.
- dad91b's south is now 2.36 Sv (was 0.87), and 7082f5's 15.1.
