# Lane A handoff A11 (2026-10-22, ~95 tool calls)

## State
- The branch has main 7d4cc7d merged in, plus docs only: this file, the stages.md section "Stage 3, attempt 3 of 3",
  `laneA11/` and three inbox drafts. No `planet/` change is committed.
- Stage 3's three attempts are used up. The decision is in `issue-tracking/inbox/draft-stage3-after-three-attempts.md`:
  - A: merge the green candidate without the fetch.
  - B: redesign the fetch first. This is my lean.
  - C: drop stage 3 for v1.

## Files (`docs/review/base-climate/laneA11/`)
- `stage3_attempt3_candidate.diff` is the green candidate. Apply it on main. pytest is green apart from the goldens.
  - The goldens need `--update-golden`, then the scorecard and `ckpt.sh` before any merge.
- `stage3_attempt2_toggles.diff` is attempt 2 with env toggles:
  - `S3_REACH=0` (the fixed 450 km), `S3_FETCH=0`, `S3_SPLIT=0` (with the old evap table back), `S3_MTN=0`;
  - `S3_FBASE=old|new`: the fetch on the land's annual mean (attempt 2), or built from the arriving sea air.
- `tools/`:
  - `endiag.py` with `rd.sh TAG ENV=..`: the endings fixture. Env DT4 shifts the −4 C and TZSET sets TZParams overrides.
  - `bands.py` and `eq.py`: where the leftover ice is, and whether the no-index run would grow it.
  - `clim3.py`: a fixed sheet's margins under each variant. `zs.py`: the zoom's own first-year SMB.
  - `ef2.py`: the AET/PET reference. `t2.sh`: the endings and cold-moment tests plus the Earth probe.
  - The scratch copies live in `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA11/`,
    with `p3.py`, `meas.sh` and `ckpt.sh` pointed at this worktree.

## If B (the fetch redesign)
- Build the land's swing from the arriving sea air: `sea_in + fetch × (land_full − sea_in)`. That's in the toggles diff
  as `S3_FBASE=new`. It fixes the summer-land-cools-sea-air flaw.
- Give the fetch its own continental scale, measured on the land's width (PW-573 names 1000–2000 km), instead of
  the 1-day boundary-layer time. Check that L4's 450 km cells don't make every land a coast. That is what moves the
  zoom's glacial ice to the poles and breaks the endings test.
- Keep the candidate's PET-referenced split. With the fetch back, re-check `test_cold_moment_has_sheets` and the endings test.
- Keewatin's +3.9 comes from the per-time reach (fixed reach: −0.6). The weak summer wind lets Hudson Bay's cold air
  reach less far. That ties to the bay's own summer air being 6.5 C too cold (handoff A10).
