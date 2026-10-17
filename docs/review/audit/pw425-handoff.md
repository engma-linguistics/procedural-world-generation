# PW-425 / PW-424 handoff: natural meander trains, no hairpins

Branch `worktree-agent-a0b8d885889258e9f`, not merged. `uv run pytest -q` passes.

## What changed
- New `planet/zoom_fine_meander.py` builds the meander trains.
  - Each bend is a Kinoshita curve: theta = w sin phi + w^3 (Js cos 3phi - Jf sin 3phi).
  - The curves are tabulated over (w, Js, Jf). The table gives the offset along the axis (xi) and across it (y), the amplitude, the neck and the tightest radius.
  - Swing, skew, flatness and arc length vary from bend to bend. They are smooth value noise in the channel phase phi.
    - Swing: 1.2 x (1.0 + 0.3 N + 0.75 max(N, 0)^3), at most 1.95.
    - The flatness sometimes passes 1/(3 w^2): the apex turns back, a compound loop.
  - phi is the parent network's planet-fixed valley phase psi, warped. So sibling and nested zooms draw the same bends.
  - The warp keeps the mean wavelength over every 3 wavelengths, so it stays local (no accumulation down the course).
  - A tight loop takes less valley: its valley length goes as (the curve's valley length per arc)^0.6. Plus 30% arc scatter.
  - Caps, applied as shares and eased over a quarter wavelength (a step in a swing would be a step in the offset):
    - room in the floor: in a narrow floor all bends shrink together, so the big ones stay the biggest;
    - bend radius at least 1.3 x R_MIN: skew and flatness are let down first, then the swing;
    - necks stay at least 1.2 w + 3 px apart.
  - Cutoffs: a half-bend swinging past CUT_OM = 1.6 has a 50% planet-fixed chance of having been cut off.
    - Its swing drops to 0.3 over that bend and its neighbours' halves.
    - The old apex arc is returned as an oxbow.
- `zoom_fine._courses`:
  - The train's offsets come from `ZFM.train` (along + across the smoothed axis normal).
  - The PW-424 limiter: wherever the drawn centreline's bend radius over a +-max(1.5 w, 3 px) chord is under max(1.5 w, 2.5 px), the swing is let down over a quarter wavelength, up to 10 passes, multiplicatively.
  - The parent-px wander is no longer added under drawn meanders. At a fine parent its 4 px bends are shorter than a meander wavelength.
  - The phase is interpolated along the course's arc length and evened over a parent px.
  - The meander belt allows for the biggest bends (`ZFM.belt_amp`).
  - Oxbow arcs are collected (new `oxbows` out-param).
- `zoom_fine.build` 4b: oxbow arcs that lie on the floor, at least 1 px from the channel, become shallow pools.
  - Water 0.3 d below the floor, bed 1 d below it.
  - New stat `floodplain.oxbow_km2`.
- `_meander_y` was removed. `_MEANDER` (the sine-generated table) still sets the node-level room swing and the belt.

## Metrics (scratch: `scratchpad/pw425/metrics_after.txt`; before = `scratchpad/pw412/store_after`)
352c76 (310 m^3/s, 25 m/px):

| | before | after |
|---|---|---|
| switchbacks | 5 (0.096/km) | 0 (0.000/km); target <= 0.027 |
| turn p95 | 62.3 deg | 53.8 deg |
| sinuosity_gentle median / p90 | 1.70 / 1.87 | 1.48 / 1.83 |
| wavelength | | +-20% (p10/p90 0.8/1.2 lambda, synthetic) |
| oxbow lakes | | 2 (0.013 km2) |

Block rms: 1.61 -> 1.62. Edge errors are 0. Other zooms are unchanged within noise: 980612, b570c2, 2b1dab, 3453b8, 97b3e7, 3e74b0.

## Images
In `scratchpad/pw425/img/`:
- `352c76_v1_overview.png`: left is the PW-412 baseline, right an early iteration. Not regenerated after the final tuning.
- `352c76_final_detail_mid.png`: before and after.
- `352c76_final_detail_oxbow.png`: before and after, with oxbow lakes.
- `synth_7.png`, `synth_8.png`: synthetic straight-axis trains (`synth.py <seed> [CUT_P]`).

## For PW-416 (migration)
Evolve the train's state, not the pixels. `ZFM.train` returns, per axis sample: `phi`, `omega`, `js`, `jf`, `X` (the local wavelength), plus the oxbow arcs.
- Migration down-valley: shift phi with time. A planet-fixed rate per reach, e.g. ~1-2% of a channel width per year.
- Growth: raise omega toward the cap.
- Cutoff: when the neck (`prop("neck")` x X) closes below about a channel width, drop that half-bend's omega as the cutoff code does now, and keep the old arc as an oxbow.
The axis B, the floor and the belt stay fixed. Keep the caps as eased shares.

## Follow-ups
- `issue-tracking/inbox/draft-oxbow-crescents-and-scroll-bars.md`: oxbows are small blobs; no scroll bars or meander scars.
