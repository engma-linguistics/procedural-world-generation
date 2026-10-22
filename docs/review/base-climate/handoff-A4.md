# Lane A handoff A4 (2026-10-22)

## State
- This branch is stage 2b plus PW-578 attempt 2 (see stages.md, "Stage 2b, step 2"). Main is merged in.
- The mechanisms are in `planet/climate.py`:
  - `_sea_half` derives the sea's own swing and the coupling c ≈ 0.42; TUNE `sea_half` is gone;
  - stable summer land air: `open_sea` per season, (1 − land_air) in the summer half.
- The goldens are regenerated, and the scorecard line is appended.
- pytest: two tests fail unchanged, both knife edges, with inbox drafts:
  - `test_ocean::test_meltwater_weakens_the_overturning` (+0.001 Sv at the moc_k cap);
  - `test_zoom_soils::test_zoom_soil_layers` (0.488, main 0.519).
- Earth: r 0.619 (≥ 0.617); group 69.6 (< 71). The gap is stage 2b's temperatures (D→E), not the rain.
- The PW-575 winds are still parked on `laneA3-winds-wip`.

## Next (attempt 3, or the coordinator's ruling)
1. Rule on the two knife-edge tests (drafts give options). Without a ruling, the cleanest physics change is the
   meltwater draft's option A (the cap's density difference). That is ocean / stage-1 code.
2. The D→E summers of high-latitude near-land seas (draft-stage2b-koppen-group-d-to-e).
3. The experiment copy with every switch (x_form, x_c, x_st, x_km, x_rq, x_part, x_sa) is
   `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA3/exp/`.
   Its runners are `.../laneA3/par.sh` and `.../laneA4/diag4.sh`; `.../laneA4/melt.py` and `.../laneA4/soilplain.py`
   probe the two tests.
