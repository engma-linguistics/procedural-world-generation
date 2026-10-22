# Lane A handoff A10 (2026-10-22, ~90 tool calls)

## State of the branch
- Main f3767ad is merged in.
- **PW-579 is merged-ready**: commit de1a6a0 (entrainment below a dense pocket, `moc_entrain` 1.5) and its scorecard
  line in b67000b. `uv run pytest -q` passes (568), and the goldens are regenerated on purpose. See stages.md,
  "PW-579: entrainment below a dense pocket".
  - Earth's south goes 2.5 → 5.9 Sv and the NH 11.9 → 14.4 Sv (92% open). Fennoscandia's coldest month −6.5 → −6.0.
  - dad91b's south stays at 2.5 Sv, which is the straits' doing (`issue-tracking/inbox/draft-dad91b-south-is-straits.md`).
    I'd close PW-579 on option A.
- **Stage 3 is not on the branch.** Attempts 1 and 2 are used and both fail a time-zoom test. Attempt 2's diff (on
  de1a6a0) is `docs/review/base-climate/laneA10/stage3_attempt2.diff`. See stages.md, "Stage 3 ... attempts 1 and 2".
- The checkpoint (PW-570 step 4) ran on the PW-579 branch. Results are in stages.md, "Checkpoint".

## Tools (`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA10/`)
- `p3.py` / `p3.sh OUT 'k=v,..' ...` is the stage-3 probe, Earth L6, ~3 s per variant after the first. It prints:
  - the humid, dry and small-land boxes: warmest month and its bias, seasonal range against NCEP, and summer-half
    rain against the observed;
  - the mountains' coldest month;
  - continentality, summer heat by rain, and the near-land seas' summer air;
  - the ice rows.
- `efdiag.py`: summer AET, LE, cloud and ground sunshine per box, and the land means (where `ef_ref` and
  `cloud_ref` came from).
- `sheet.py` runs `test_sheet_air_is_carried`'s numbers under TUNE overrides. `sdiag.py` is the southern-sinking
  diagnostic per hemisphere.
- `meas.sh TAG` runs pytest, earth_check, climate_bias and the overturning report (Earth plus the 9 worlds) into
  `docs/review/base-climate/laneA10/*_TAG.txt`.
- `ckpt.sh` is the checkpoint, and `plug2/honest.py` is a pytest plugin that sets the honest TZParams as defaults
  (`-p honest`, with PYTHONPATH).

## Stage 3, attempt 3 (what I'd do)
- Apply `stage3_attempt2.diff` and re-run `p3.sh`. It should reproduce `stage3_probe_attempt2.txt`.
- The blocker is `test_glacials_grow_ice_and_endings_melt_it_fast`: 63.6 m are left 15 kyr after the ending,
  against an extra of 58.9.
  - Diagnose first: which of the three parts (per-time carry, fetch, energy split) moves it. Toggle each in the diff
    (they're separable: `fetch = 1`, `d_sum = None`, reach = `air_km_s`) and run only that test (~45 s with
    `-n 4`).
  - My guess is the fetch: zoom margins sit on coasts and narrow lands, and the fetch takes their summer heat off.
    If so, check whether an ice sheet's own margin should count as "land" for the fetch. Over the sheet the air is
    the sheet's (`damp_air`), and the sheet's dome isn't sea air.
- W Europe's −3.3 is the near-land seas' cold summer air (PW-580: North Sea/Biscay −3.8). The fetch exposes it. Fix
  PW-580 first, or accept it as a known regression with the owner's principle.
- HB lowlands (+5.2) and Labrador (+3.5) barely move. Hudson Bay's own summer air is 6.5 C too cold while its lowlands
  are 5 C too warm, so the bay's air doesn't reach them in summer. Look at the summer wind there.
- The summer rain in dry regions went down with every fetch variant (N 660 → 566, S 1623 → 1276 mm, obs ~170–200).
  That's because the rain's first pass sees the cooler summers.
- `sum_tau` = 1 day sets the reach, the fetch and the split's time. With 2 days the humid boxes and the SH get closer
  (`stage3_probe_sweep.txt`), but W Europe goes to −4.8 and the log-rain r to 0.614, under the 0.617 bar.
