# Climate stability, round 1 (lane 158, 2026-11-03): is the self-balancing climate too touchy?

A diagnosis and a proposal. Nothing under `planet/` changed. Baselines: "main" is lane 140's frozen main code
(4abc1707), the code every existing judge output in this note was made with. "Today's Earth" is the climate model's
dT = 0.

## In plain words

Daniel's worry: a tiny change early on swings a planet between "fine" and "frozen over", so the climate looks like
it wheels off course too easily. What I found:

1. **The thermostat is not weak.** Rock weathering is the planet's slow thermostat: a cold planet weathers less rock,
   so volcanic CO2 builds up and warms it back. Ours needs about **6-8 C of warming to absorb a doubling of volcanic
   CO2**. The classic models need 3-5 C (stronger). The newest data-driven estimate for the real Earth needs about
   10 C (weaker). Ours sits between them. Making it much stronger would make our planets less like Earth, not more.
2. **The thermostat is not slow either.** It answers a push within about 10 Myr. I pushed one of the coldest test
   planets 8 C colder for 60 Myr. The thermostat cancelled about four-fifths of the push. When the push stopped, the
   planet was back with its unpushed twin within 10 Myr. Nothing locked in. No snowball, no runaway.
3. **The ice is not the main cause.** After a do-nothing nudge, three-quarters of the temperature difference
   between twin planets comes from CO2. Ice reflecting sunlight adds a sixth, and methane a tenth. The CO2
   difference comes mostly (nearly nine-tenths) from **the volcanoes**. Once the twins' climates differ at all, their
   plate histories split apart. Within 50-200 Myr they have different rifts, ridges and arcs, so they outgas different
   amounts of CO2: about 25% apart, typically. That is real chaos, and Earth's plates are chaotic too.
4. **Why it feels touchy.** A self-balancing carbon cycle does not hold a set temperature. It holds a *balance*
   between how much CO2 the volcanoes put out and how easily the rock takes it up. Every 10% change in either moves
   the temperature by about 1 C, on Earth as in our model. So a planet whose volcanoes wander by tens of percent
   *must* wander by a few degrees. Earth did far more than that: over the last 485 Myr its mean temperature ranged
   from 11 to 36 C (Judd et al. 2024; today's Earth is about 14-15 C).
5. **The part that is not physics: the yardstick.** Each planet measures its own "normal" volcanic output and
   weathering rate in its first 300 Myr, and keeps them. Those yardsticks are a lucky or unlucky sample. Their spread
   between re-runs of the same planet (0.16) is nearly the whole spread between different planets (0.18). So the
   yardstick is not a property of the planet; it is a dice roll. Each 0.1 of it is 1.1 C of the planet's whole
   later climate. That dice roll is most of why re-runs of one planet disagree by 2 C on average.
6. **The judge reads the worst moment of a wandering signal.** The frozen-over check takes the single worst moment
   of a 116 Myr window and draws a line through it. On one cold test planet I have five histories, all equally
   valid. Two of them peak above the 40% line and three don't. All five end the run below it, and none stays frozen.

So I think we are chasing the wrong thing in two places:
- **We chase each planet's exact temperature.** That temperature is set by chaotic plates and a dice-roll yardstick.
- **We judge single moments.** We should judge what Daniel actually named: whether a world *ends up* frozen, and
  whether it comes back when pushed.

What I'd do (section 6): **(A)** replace each planet's dice-roll yardstick with one fixed number per grid level;
**(B)** judge whether a world ends frozen or stays frozen, not its worst moment; **(C)** while re-anchoring, let the
weathering read plant *cover*, not plant *growth* (PW-1332 option B), so plant fixes stop moving the climate by
degrees. I would not make the thermostat stronger (D). A first check of A on three of the coldest test planets (section 5): with the yardstick pinned to the average, they ended 3-5 C warmer, as forecast, and their worst land ice fell from up to 43% to 3-27%.

## 1. How strong is our thermostat, compared with Earth's?

"Gain" here means how much the weathering sink grows, in ln units, per C of global warming at equilibrium, adding
the direct temperature-and-runoff effect and the CO2 effect (each degree of warming needs more CO2, and CO2 speeds
weathering by itself). "C per doubling" is the warming that absorbs a doubling of the volcanic source:
ln 2 / gain. Higher gain means a stronger thermostat and a smaller swing for the same volcanic change.

| model | temperature + runoff, per C | CO2 effect | total gain | C per doubling of outgassing | source |
|---|---|---|---|---|---|
| **Ours, by design**, planted ground | 0.070 (0.09 per local C x 0.6 + runoff 0.016) | 0.2 / 4.33 = 0.046 | 0.116 | **6.0** | `earth.py` WEATHER_K, START_RESPONSE, RUNOFF_PER_C, WEATHER_FERT, co2_sensitivity 3 |
| Ours, by design, bare ground | 0.070 | 0.5 / 4.33 = 0.115 | 0.185 | 3.7 | WEATHER_CO2_BARE |
| **Ours, measured on a saved planet** (temperature leg only, CO2 fixed) | **0.0697** | | | | `probe.py` on r0.0005 l6fix 957317 at 300 Myr, dT +1.5..+9.5 |
| **Ours, measured in the runs** (all feedbacks: ice, methane, the plants) | | | 0.093 / 0.085 | **7.4 / 8.2** | re-runs: late dT -10.7 C per unit of yardstick (36 runs, `yard.py`, as lane 140d); twins: dT +11.8 C per unit of outgassing difference (`share.py`) |
| Walker, Hays & Kasting 1981 | 0.073 (W ~ exp(dT / 13.7)) | 0.3 / 4.33 = 0.069 (P^0.3, with today's 3 C per doubling) | 0.142 | 4.9 | their eq. 1 |
| GEOCARB III (Berner & Kothavala 2001), cold periods, planted | 0.119 (ACT 0.09, RUN 0.045, exponent 0.65) | 0.2 / 4.0 = 0.050 (FERT 0.4; Gamma 4.0 C per e-fold) | 0.169 | 4.1 | their eq. 2 and standard run |
| GEOCARB III, bare ground (CO2^0.5) | 0.119 | 0.5 / 4.0 = 0.125 | 0.244 | 2.8 | |
| Krissansen-Totton & Catling 2017, posterior median | 0.029 (e-folding 34 K; 90%: 17-48 K) | 0.33 / 8.1 = 0.041 (alpha 0.33; Earth-system sensitivity 5.6 K per doubling) | 0.070 | 9.9 | their Table 1; continental weathering only |

- Krissansen-Totton & Catling fit the last 100 Myr of Earth's records with a Bayesian inversion. They find that
  "15–31 °C (1σ) surface warming is required to double the continental weathering flux, versus 3–10 °C in previous
  work". In their words, Walker et al.'s overall e-folding is 13.7 K, GEOCARB III's is about 9.2 K, and the "widely
  used range ... of Te=5–15 K is incorrect".
- Maher & Chamberlain 2014 say the feedback's strength is itself variable: "Climate regulation by silicate
  weathering is thus strongest when global topography is elevated ... and lowest when global topography is more
  subdued". They take runoff to rise 2.3-6.8% per C of global warming. Ours is 2.6% (`RUNOFF_PER_C`'s note),
  at their low end.
- The thermostat's speed: CO2 settles within `CO2_TAU / slope`, about 1 Myr, and the temperature follows over
  5 Myr (`global_temperature`'s last line). Climate updates come every 4-8 Myr, sooner when dT moves by 1 C. The
  pulse test (section 4) shows it settles within about 10 Myr.

**Answer: ours is neither weak nor slow.** It is weaker than the 1980s-2000s models (by about a third) and stronger
than the best current estimate for the real Earth (by about a third to a half). Weakness is not why the climate
drifts.

## 2. Where the chaos comes from

Lane 144's forked twins are ideal for this. Each pair shares everything up to 300 Myr, including the yardstick and
the random wander (the "drift" term is identical, 0.000 difference throughout). One twin then gets +0.00001 or
+0.00002 C. Six cold test planets, two nudges: 720 paired 10-Myr means over 400-1000 Myr (`share.py`; per era in
`decomp.py`).

The climate's target temperature is CO2's warming + the ice's whiteness + methane and N2O. Of the twins'
difference in it (sd 4.6 C):

| part | share |
|---|---|
| CO2 | **75%** |
| ice reflecting sunlight | 16% |
| methane and N2O (both follow the climate) | 10% |

CO2 follows the balance of volcanic source against weathering sink. Of the twins' difference in that balance:

| part | share |
|---|---|
| **volcanic outgassing (ridges, arcs, plumes)** | **+88%** (twins' ln outgassing differs by sd 0.25, i.e. ~25%) |
| erosion supply of fresh rock (incl. ice covering it) | +17% |
| plants' weathering factor | +21% |
| weathering's temperature response | **-26%** (the thermostat pulling back) |

- How fast the outgassing splits: ln outgassing difference rms 0.004 at 300-350 Myr, 0.08 at 350-400, 0.21 at
  400-500 and 0.25-0.32 from 500 Myr on (`decomp.py`). A bigger push splits it faster: in the pulse runs it was
  already 0.17-0.27 apart within 20-30 Myr (`pulse_parts.py`). Within one run, the outgassing's 10-Myr means wander
  with sd 0.18 in ln (median of 36 runs; `gain.py`), with a memory of about 45 Myr. The twins' 0.25 is that wander,
  fully decorrelated (0.18 x sqrt 2). The repo's earlier sizing of the outgassing found it on GEOCARB's spread of
  volcanic CO2 (`params.py` climate_drift note: ridges and arcs sd(ln) 0.2-0.45).
- Ice is an amplifier, not a switch. Peak land ice in the twins moves 2.1 points per C, smoothly (`share.py`). No
  test history shows two separate states (a "stuck" snowball and a normal one), and the pulse test finds no
  lock-in (section 4).
- **The yardstick, separately.** Over lane 140's 36 main runs (8 planets, 4-6 re-runs each; `yard.py`), the frozen
  yardstick y = ln(source reference / sink reference) has sd 0.175 overall and 0.162 between re-runs of the same
  planet. Re-rolling it explains 77% of the re-runs' late-climate spread (late dT -10.7 C per unit of y). Without it,
  0.94 C would be left. It is learnt as a 100-Myr running mean of a signal with a ~45-Myr memory, so it holds only a
  few independent samples, and its noise is the source's own wander.

**Answer:** three things in series. (1) The plates are chaotic. Any climate difference reaches them through erosion
and the crust, and their outgassing splits by ~25% within 50-200 Myr. (2) The thermostat, at Earth-like strength,
turns that into 3-4 C (the ice adds a sixth). (3) On top, each re-run draws its own yardstick, worth another 1.7 C
(sd). The thermostat's slowness and the ice's bistability are not the cause. The yardstick is a sampling artefact.
The plate chaos is physics.

## 3. Is the chaos confined to timing? Mostly, but the judge doesn't read it that way

One cold test planet (r0.001 l6c_p 957317) has five valid histories: lane 144's forked main and two forked nulls,
and my two pulse runs (`attractor.py`):

| history | peak land ice 884-1000 (the hard bar) | mean dT 600-1000 | mean land ice 600-1000 | time at >= 40% ice | longest stretch >= 40% |
|---|---|---|---|---|---|
| main (fm) | 19.7 | -1.59 | 17.0 | 0% | 0 Myr |
| null +1e-5 C (fn) | 24.2 | -0.88 | 11.8 | 0% | 0 |
| null +2e-5 C (fn2) | **43.0** | -3.53 | 25.4 | 18% | 52 |
| pushed -3 C, 700-760 Myr | **43.9** | -4.63 | 29.3 | 24% | 98 |
| pushed -8 C, 700-760 Myr | 24.8 | -3.07 | 21.6 | 0% | 0 |

- Two of five fail the frozen-over check. All five are below 21% land ice by 980-990 Myr. None ends frozen.
- Even the 400-Myr averages differ (mean dT -0.9 to -4.6 C). The plates' wander has a long memory, so a planet has
  no single climate to find: it has a spread of histories. A fixed yardstick (option A) narrows that spread but
  cannot remove it.
- Earth's record has the same shape: long warm and cold eras, the Cryogenian snowballs (the planet fully frozen
  for millions of years), and recovery each time.

## 4. Does a pushed planet come back? (the pulse test, 2 runs)

`pulse.py`: lane 144's 300-Myr state of r0.001 l6c_p 957317, main code at the same thread count. It equals lane
144's forked main bit for bit up to 700 Myr (checked). Then a push of -3 C or -8 C on the climate from 700 to
760 Myr, then none. Compared with the unpushed run, 10-Myr means (`pulse_read.py`, `pulse_parts.py`):

- **-8 C push:** the planet cooled by only 1.4 C on average over 720-760 Myr. CO2 rose by 1.2-1.9 e-folds (3-7x),
  so **the thermostat cancelled ~80% of the push**. The small-signal design cancels about half
  (1 - a / (gain_T x G + a), with gain_T 0.07 per C, G 4.7 C per e-fold of CO2, a 0.2-0.5). The extra came from the
  outgassing, which happened to rise as well.
- **-3 C push:** the planet cooled by 3.2 C. CO2 hardly rose, because the outgassing happened to *fall* by 0.17-0.29
  in ln at the same time (a cooling of about 2-3 C by itself). The weathering did what the design says: its sink fell
  0.08 per C of cooling, 0.045 of it the temperature leg and 0.035 the ice covering rock. The chaotic outgassing
  happened to outweigh it.
- **Recovery:** in both, within 10 Myr of the push ending the planet was back within 1 C of the unpushed run
  (760-780 Myr: +0.9 / -0.4 C and +0.6 / +0.7 C). After that, each wandered like any nudged twin. The -3 C history
  froze over in the hard window 100+ Myr later, as the do-nothing fn2 did.

So the attractor is sound: a push is answered within ~10 Myr and nothing locks in. **The failure mode is
"a different but equally valid history", not "a planet that ran away".**

## 5. Option A checked on three cold test planets (3 runs)

`pin.py`: the same 300-Myr states and code as lane 144's forked main. The only change is that the frozen yardstick
is set to the 36-run mean (y = 1.316; the source reference is kept and the sink reference rescaled). Forecast
from the re-runs' slopes: late dT +10.7 C and peak land ice -25.8 points per unit of y removed.

`pin_read.py`. "Unpinned" = lane 144's forked main and two forked nulls of the same draw (three histories, each
with the planet's own drawn yardstick).

| draw | yardstick y | late dT 600-1000: unpinned (fm, fn, fn2) | **pinned** | shift vs unpinned mean (forecast) | peak land ice 884-1000: unpinned | **pinned** |
|---|---|---|---|---|---|---|
| r0.001 l6c_p 957317 | 1.649 | -1.59, -0.88, -3.53 | **+0.97** | +2.97 C (+3.6) | 19.7, 24.2, 43.0 | **8.7** |
| r0.001 l6c_0 819014 | 1.788 | -7.64, -2.62, -3.52 | **+0.82** | +5.41 C (+5.1) | 32.3, 16.7, 40.5 | **2.9** |
| r0.0005 l6c_0 819014 | 1.581 | -3.59, -1.15, +0.71 | **+1.59** | +2.94 C (+2.8) | 33.5, 11.5, 15.3 | **27.0** |

- The shifts match the forecast within the chaos (+3.0 / +5.4 / +2.9 C against +3.6 / +5.1 / +2.8). The forecast
  slope (10.7 C per unit of y) holds when the yardstick alone is changed.
- With the yardstick pinned, these "cold" planets are not cold. Their late climate is +0.8 to +1.6 C, near the
  36-run mean (+1.4 C). Their worst hard-window moment is 3-27% land ice, against up to 43% unpinned. Two of these
  three draws are the ones that failed PW-1261's judge and lane 144's do-nothing re-run (PW-1404). **Main's cold tail
  is mostly the yardstick's dice roll.**
- Caveat: one pinned history per draw, and these were picked for high y. On the full set, about half the draws have
  y below the mean, so they cool by the same rule. The forecast puts the 36 runs' worst late mean at -2.5 C,
  against -7.5 now. The hot side should be checked on the full set, as the confirming experiment does.

## 6. What to chase instead, and the options

The target, in Daniel's words, is "reasonably stable and not prone to exploding when nudged". In model terms:
- a negative feedback that brings each world back within some Myr: **we have it** (section 4);
- chaos confined to the timing of glacials, not to whether a world ends frozen: **true of the physics** (section
  3), **not true of the judge**;
- planet-level yardsticks that aren't noisy samples: **not true today** (section 2).

### A. One yardstick constant per grid level, not a per-planet sample (physics-neutral calibration)
- What: after the spin-up, set the sink reference to source reference x exp(-Y_level). Y_level is a constant per grid
  level: the mean y over a reference ensemble (1.316 at L6 on main 4abc1707). The source reference stays learnt; it
  only sets units. A tool re-fits Y_level whenever a change moves the weathering's or the outgassing's size, the same
  way `MODEL_EARTH_ICE` is probed.
- Effect: removes the yardstick's 1.7 C (sd) from every planet. Forecast on the 36 runs (`yard.py`): the spread of the
  late-climate mean (600-1000 Myr) across all runs falls from sd 2.64 to 1.32 C (range -7.5..+6.6 to -2.5..+4.3 C).
  The spread between re-runs of one planet falls from 2.0 to 0.9 C. Peak hard-window land ice: sd 9.0 to 6.7
  points, worst 33.5 to 26.6%. Main's cold tail is cold mainly because its yardsticks drew high: lane 144's six
  coldest have y 1.42-1.79, against 1.32. So the margin to the 40% line widens: section 5 measured it on three of them (worst land ice 3-27%, was up to 43%).
- What it de-couples: the planet's whole later climate from the luck of its first 300 Myr. It also makes the
  forked judge (PW-1403) unnecessary, because the arms can no longer differ in their yardstick.
- Cost: small. One change in `global_temperature` and one probe tool, then re-run the golden tests and the judge.
- Risk: a change that alters the weathering's or outgassing's size no longer cancels itself out through the
  yardstick. It shifts every planet until Y_level is re-fit. That is honest bookkeeping, but it is a step in every
  such merge. Real differences between planets now show (more mountains relative to volcanoes gives a colder planet).
  Their spread is small at L6: the between-planet part of y is sd ~0.07, ~0.7 C. L7 and non-default stars need their
  own Y or a check that one Y fits.
- Physics: the reference was a numerical convenience (model units to a balance), not a measured property. A single
  constant is closer to how GEOCARB and Walker et al. work: one present-day flux balance, applied to every state.

### B. Judge whether a world ends frozen or stays frozen, not its worst moment (judging change: needs Daniel's yes)
- What: the hard "frozen over" failure would mean one of two things. Either the world is frozen when the run ends
  (no finish moment passes for ice, and land ice is at or above 40% at the end), or it stays at or above 40% from
  some time to the end without coming back. The window peak (884-1000) moves to the soft scorecard as a colour.
  Optionally, for a draw that fails, a recovery check: a forked -8 C push for 60 Myr, which must come back to its
  unpushed twin within ~20 Myr.
- Effect: on the five histories in section 3, 0 of 5 fail (now 2 of 5). This reads Daniel's own target: whether a
  world ends frozen, not when its glacials fall.
- What it de-couples: the merge judge from glacial timing.
- Cost: small (`tools/judge.py`, `tools/hard_bar.py`, `tools/ice_criteria.py`). The recovery check is ~1 run per
  failing draw.
- Risk: a world that is genuinely too cold, but never quite stuck, could pass. Keep the soft scorecard's
  ice measures (time at >= 40%, mean land ice), and keep the finish moment's own ice checks for the shown world.

### C. The weathering reads plant cover, not plant growth (PW-1332 option B), in the same re-anchoring
- What: `plant_factor` from the planted share of the ground (cover, or roots present) instead of NPP / 500.
- Why it belongs here: today, a fix to the plants' growth model moves the climate by several degrees (PW-1332: 3-5 C
  from one grass fix). The weathering reads NPP, and the learnt yardstick absorbs such a change only partly. Under A,
  every such shift would need a re-fit, so the less the weathering hangs on fine plant details, the better. The
  plants' factor is also 21% of the twins' carbon-balance difference. GEOCARB's plant factor for the time before
  vascular land plants (f_E 0.25, `PLANT_WEATHER`'s note) is about plants being there at all, not about their yield.
- Cost: medium (one function, then a re-fit of Y). Risk: a desert's sparse cover and a rainforest's would weather the
  same per covered area. The climate factor (runoff, temperature) still separates them.

### D. A stronger thermostat (not recommended)
- To halve every spread, the gain would have to double, to ~0.23 per C (3 C per doubling of outgassing). That is
  beyond GEOCARB III on planted ground and more than three times Krissansen-Totton & Catling's estimate for Earth.
  Matching GEOCARB's runoff term (0.045 per C against our model's own 0.016) would give about +25% gain and about
  -20% spread. That would be a tuning toward older models against our own climate's runoff, so it would be chasing
  the metric. Maher & Chamberlain point the other way: the real thermostat weakens on low-relief continents.

### On judging the attractor more broadly
The paired judge already prefers continuous late-window measures over the pass count (PW-994). A and B make that
easier: with no yardstick noise, the late 400-Myr mean differs between re-runs by ~0.9 C instead of 2 C, so smaller
changes show. A hard bar on single draws will always read some plate chaos. With A, the remaining chance that a
cold-tail draw crosses 40% in its window is what B's "ends or stays frozen" rule protects against.

## 7. Lean, and the one cheap experiment

**Lean: A + B, with C folded into A's re-anchoring.** A is the root fix of the part that is not physics. B makes the
bar read what Daniel asked for. C stops plant fixes from moving the climate. None of them makes the planet less
Earth-like. D would.

**The confirming experiment, before any lane builds A:** section 5 is its first slice. The full version: lane 144's
`paired_fork.sh` states for all 36 draws (or the 18 of one roll), each continued twice from 300 Myr with the
yardstick pinned to Y (pin.py). That is about 36-72 continuations, ~0.75 run each, ~1-2 h at 8 cores. Pass if the
spread of late dT between re-runs of the same planet falls from ~2.0 to <= 1.2 C, and the cold six's hard-window peak
ice falls by the forecast (about -25 points per unit of y) within the chaos.

## Files and sources
- Scripts (read-only on lane 140/144 outputs in the session scratchpad `l140/judge`, `l144/judge`): this folder's
  `tools/`: `decomp.py`, `share.py` (section 2), `yard.py` (yardstick, option A forecast), `probe.py` (temperature leg on
  a saved planet), `pulse.py`, `pulse_read.py`, `pulse_parts.py` (section 4), `attractor.py` (section 3), `pin.py`,
  `pin_read.py` (section 5). `gain.py` and `gain2.py` (run-time regressions, confounded by trends; not used for any
  number above except the outgassing's wander and memory) stay in the scratchpad.
- Runs (L6, 1 Gyr, scratch, deleted at the end of the lane): 2 pulse runs, 3 pinned runs.
- Walker, J. C. G., Hays, P. B. & Kasting, J. F. (1981) JGR 86: 9776-9782 (read: eq. 1, W/W0 = (P/P0)^0.3 exp(dT/13.7)).
- Berner, R. A. & Kothavala, Z. (2001) GEOCARB III, Am. J. Sci. 301: 182-204 (read: eq. 2, ACT 0.09, RUN 0.045 /
  0.025, Gamma 4.0 / 3.3).
- Maher, K. & Chamberlain, C. P. (2014) Science 343: 1502-1504 (read: abstract; runoff 2.3-6.8%/C; feedback strongest
  in active, high-relief regions).
- Krissansen-Totton, J. & Catling, D. C. (2017) Nature Communications 8: 15423 (read: Table 1, Te 34 K, alpha 0.33,
  ESS 5.6 K; GEOCARB III's effective Te ~9.2 K, WHAK's 13.7 K).
- Judd, E. J. et al. (2024) Science 385: eadk3705 (abstract via the publisher's listing and press: GMST 11-36 C over
  485 Myr; Earth-system sensitivity ~8 C). Not read in full.
