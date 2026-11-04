# Climate stability, round 4 (lane 187, 2026-11-04): L7's carbon-cycle yardstick measured (PW-1458)

**In plain words.** Each grid level has one fixed carbon-cycle yardstick (`earth.YARDSTICK`, D47 / PW-1424 A). L7's
value, 1.542, was not measured. Lane 170 derived it from six older L7 store runs, made before D47 and before lane 181's
canopy-respiration change (KN_RESP 0.4). This lane measures it on current main by spinning stock L7 draws to 300 Myr,
the point where every run's yardstick is learnt, and re-checks L6 the same way. Each 0.1 the constant is off moves
every L7 world's later climate about 1.1 C, all in the same direction.

## Method
- Code: a frozen copy of main 78140574 (`git archive`). `planet/` is unchanged since lane 181's merge (98547e1e),
  so this is D47 + KN_RESP 0.4.
- L7: `fork.py spin` (docs/review/base-climate/v1-finish-16/) to 300 Myr, stock settings (`star_brightening=1.0`,
  `climate_offset=0`), 1 thread each, 6 at once. Draws are lane 170's eight judge seeds plus seeds from
  `random.Random(187)` (the draw list is in scratch `l187/draws7.txt`). The pin only acts after 300 Myr
  (`earth.REF_FREEZE`), so a spin to 300 Myr measures the learnt yardstick with no pin. `tools/yardstick.py` reads it.
- L6: lane 181's `kn` arm (36 straight 1-Gyr `paired.sh` runs of exactly this physics, scratch `l181/judge/kn_*`)
  already holds every draw's learnt y at 300 Myr. `tools/yardstick.py` reads it there, so no new L6 spins were
  needed. It is compared against lane 170b's `cand` spins of the same 36 draws (D47 without KN_RESP), which set 1.377.

## L6 (36 draws, current code)
- Learnt y mean **1.337**, sd 0.143, standard error 0.024. YARDSTICK[6] is 1.377 (standard error 0.035).
- Paired against lane 170b's spins of the same draws: KN_RESP shifts y by **-0.040** (paired sd 0.189, standard
  error 0.031), which is 1.3 standard errors. Unpaired, the two means differ by 0.040 with a joint standard error of
  0.042.
- Verdict: within error. L6 stays at 1.377.

## L7 (interim: 17 of 24 spins, paused about 11:50 for Daniel's quiet machine, still paused at 12:31)
- Learnt y mean 1.621, sd 0.164, standard error 0.040, against YARDSTICK[7] 1.542 (+0.079, 2.0 standard errors).
- With sd about 0.16, 24 spins give a standard error of about 0.033.

## Status (lane 187, handoff section)
- Done: L6 re-check (above). 17 L7 spins in scratch `l187/fork/L7_o0/` (each 21-27 min at 1 thread).
- Running, SIGSTOPped by the coordinator: 6 spins (`drive2.sh b2.txt 6`, pid in `l187/b2.pid`). 1 draw is still
  queued.
- Next: when all 24 spins finish, `uv run python tools/yardstick.py <scratch>/l187/fork/L7_o0/*_at300.json.gz`. If the
  mean is more than about 2 standard errors from 1.542, set YARDSTICK[7] and run the paired check: copy the code to
  `l187/code/new` with the new value, then `cont_one.sh main SEED` and `cont_one.sh new SEED` for 4-6 spins, at most
  4 at once. These continue the same 300-Myr spin under each value, so the comparison is exact.
