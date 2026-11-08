# Climate stability, round 2 (lane 160, 2026-11-03): the full check of option A (one yardstick per grid level)

A measurement. Nothing under `planet/` changed. Round 1 (`round1.md`, lane 158) proposed pinning every planet's
carbon-cycle yardstick y = ln(source ref / sink ref) to one number per grid level (1.316 at L6) and named a pass line:
the spread of the late climate between re-runs of the same planet should fall from about 2.0 C to 1.2 C or less.

**Baselines.** "Unpinned" is lane 140's main runs of the same 36 draws (`l140/judge/main_*`, code 4abc1707, each
planet with its own drawn yardstick). On lane 144's six cold draws there are also the forked histories fm, fn, fn2
(the same 300-Myr state, unpinned, nudged by 0, 1e-5 and 2e-5 C). "Late dT" is the mean dT over 600-1000 Myr; dT is
relative to today's Earth in the model (dT = 0).

## In plain words

1. **It does not pass.** With the yardstick pinned, re-runs of the same planet still disagree by **1.8 C** (sd of the
   late climate), against **2.0 C** unpinned. The pass line was 1.2 C and the forecast 0.9 C.
2. **Why: the plates' chaos is bigger than round 1 thought.** Two pinned histories that start from the very same
   300-Myr state, with the same yardstick, still differ by **1.4 C** (sd), and this is on all 36 draws. Round 1 estimated
   that about 0.9 C would be left once the yardstick was removed. The yardstick was worth less than forecast and the
   chaos more.
3. **Across all 36 planets the spread did shrink:** sd **1.7-1.9 C**, against **2.6 C** unpinned (the forecast was
   1.3). The range narrowed from -7.5..+6.6 C to -4.2..+4.8 C. The cold tail is gone as forecast: the six coldest
   draws warmed on average by +2.5 C (forecast +2.7) and their worst hard-window land ice fell by 9 points on average
   (forecast about 7).
4. **The hot side is fine.** No pinned planet's late climate goes over +5 C (the warmest is +4.8 C; unpinned had two,
   +5.5 and +6.6 C). Nothing comes near hell: the hottest single moment after 600 Myr is +11.9 C, against the
   +15.5 C line, and no late median comes near +10.5 C.
5. **Hard bar:** one pinned history out of 72 is frozen over by the current rule (r0.001 l6c_p 733847, first
   history: 41.6% land ice at its worst moment in 884-1000 Myr). Its twin peaks at 15.9%, and unpinned it peaked at
   7.8%. It ends at 30% and is not frozen at the end, so under PW-1425's "ends frozen" rule it passes. No pinned
   history ends frozen, boils, loses its ocean or crashes its CO2. Unpinned main: 0 of 36 on every hard failure.
6. **Soft passes:** 33 and 31 of 36 pinned, against 30 of 36 unpinned. That is within chance (McNemar p 0.51 and 1.0).

So option A does what it says on the yardstick: it removes the yardstick's dice roll and the cold tail with it, and it
does not tip any planet hot. But it does not make re-runs of one planet agree to within 1.2 C. The rest of the spread
is the plates' chaos (round 1 section 2), which is physics. A judge that reads single draws will keep seeing about
1.4-1.8 C of it whatever we do to the yardstick.

## The experiment

- For each of the 36 judge draws (paired.sh's 18 draws x rolls 0.0005 and 0.001), the 300-Myr state of lane 140's
  main code (l144/code/main, 4abc1707). Six are lane 144's fork states (`l144/judge/fork`). The other 30 were spun
  again here with `paired_fork.sh`'s `fork.py spin` at the same 3 threads; all 30 are identical to lane 140's runs at
  300 Myr (every recorded field).
- Two pinned continuations from each state to 1000 Myr, y set to 1.316 (source reference kept, sink reference rescaled):
  **P** = `tools/pin.py` exactly (`tools/pin2.py` with DOFF 0), **P2** = the same plus 1e-5 C on climate_offset after
  the fork (as lane 144's forked null fn). 72 runs, 1 thread each, 12 at once.
- Check: P reproduces lane 158's three pinned runs (section 5 of round 1): peak land ice 8.7, 2.9 and 27.0, the same.
- Read-outs: `tools/pin_full.py` (the per-draw table and spreads, as `yard.py`), `tools/hard_bar.py` on symlink roots,
  `tools/judge.py paired` with main against P and P2.

## 1. Spread between re-runs of one planet (the pass line)

Within-seed sd of late dT (as `yard.py`: the same seed across its 4-6 draws; 8 seeds):

| arm | within-seed sd | pass line 1.2 C |
|---|---|---|
| unpinned (lane 140 main) | **2.02 C** | |
| pinned P | **1.79 C** | fail |
| pinned P2 | **1.76 C** | fail |
| P and P2 pooled (up to 12 histories per seed) | 1.81 C | fail |
| round 1's forecast for pinned | 0.9 C | |

Twins from one state (the chaos alone, no yardstick difference possible):

| set | sd of one history about its draw's mean |
|---|---|
| pinned P vs P2, all 36 draws | **1.41 C** (median gap between the two 1.03 C) |
| unpinned fm / fn / fn2, lane 144's six cold draws | 1.83 C |
| pinned P / P2, the same six | 2.25 C |

The chaos alone is about 1.4 C on the full set (more on the six cold draws, pinned or not). That is above the pass
line by itself, so no yardstick fix can reach 1.2 C on single draws. Round 1's 0.94 C "left after y" came from a
regression on the 36 unpinned runs; the direct measurement says the residual is larger.

## 2. Spread across all 36 planets

| arm | mean late dT | sd | range |
|---|---|---|---|
| unpinned (lane 140 main) | +1.41 C | **2.64 C** | -7.52..+6.55 |
| pinned P | +1.06 C | **1.91 C** | -4.16..+4.75 |
| pinned P2 | +1.45 C | **1.73 C** | -1.95..+4.41 |
| round 1's forecast | | 1.32 C | -2.5..+4.3 |

Paired with unpinned main (`judge.py paired`, median of P - main): late dT -0.83 C [-1.63, -0.15] for P, -0.39 C
[-1.13, +0.57] for P2; P against P2 +0.19 [-0.48, +0.93]. So the pinned climate's centre is the same as main's
within the twins' chaos (P's small cooling is not repeated by P2).

The cold six (lane 144's coldest draws; y 1.42-1.79), against the mean of their three unpinned histories:

| draw | y | late dT unpinned -> pinned (shift, forecast) | peak land ice 884-1000: unpinned mean -> pinned mean (forecast) |
|---|---|---|---|
| r0.0005 l6c_0 819014 | 1.580 | -1.21 -> +0.43 (+1.6, +2.8) | 20.1 -> 31.9 (-6.8) |
| r0.001 l6c_p 957317 | 1.648 | -1.87 -> +0.96 (+2.8, +3.6) | 29.0 -> 11.8 (-8.6) |
| r0.001 l6c_0 819014 | 1.789 | -4.55 -> +2.30 (+6.9, +5.1) | 29.8 -> 4.1 (-12.3) |
| r0.001 l6c_0 53669 | 1.510 | -1.53 -> +0.68 (+2.2, +2.1) | 28.3 -> 19.6 (-5.0) |
| r0.0005 l6fix 957317 | 1.468 | +0.28 -> +0.04 (-0.2, +1.6) | 21.6 -> 16.7 (-3.9) |
| r0.001 l6fix 957317 | 1.419 | -1.06 -> +0.61 (+1.7, +1.1) | 25.1 -> 15.3 (-2.7) |
| **mean** | | **+2.5 C (forecast +2.7)** | **-9.1 points (forecast -6.6)** |

Round 1's second pass condition (the cold six's peak ice falls by about the forecast) holds on average; one of the six
(r0.0005 l6c_0 819014) went the other way, inside the chaos.

## 3. Hard bar on the pinned runs

`tools/hard_bar.py` (current main's tools) on P and P2; unpinned main for the baseline:

| failure | unpinned main | P | P2 |
|---|---|---|---|
| frozen over (>= 40% land ice, worst moment in 884-1000) | 0/36 | **1/36** | 0/36 |
| ends frozen (land ice >= 40% at 1000 Myr; PW-1425's variant) | 0/36 | 0/36 | 0/36 |
| boiled / hell | 0/36 | 0/36 | 0/36 |
| ocean loss | 0/36 | 0/36 | 0/36 |
| CO2 crash (below the plants' compensation point) | 0/36 | 0/36 | 0/36 |
| (secondary: pCO2 under 100 ppm) | 2/36 | 0/36 | 0/36 |

The one frozen-over history, r0.001 l6c_p 733847 P (y 1.380, a near-mean yardstick, so pinning changed it little):
late dT -4.16 C, peak 41.6%, 30.3% at the end. Its twin P2: -0.57 C, peak 15.9%. Unpinned: +0.53 C, 7.8%. This is
the chaos of round 1 section 3 on a fresh draw, not the yardstick. With the yardstick pinned, the frozen-over check
still fails about 1 history in 72 by glacial timing alone.

## 4. The hot side

Round 1 could not check this. The human range is -6..+5 C of today's Earth.

| | unpinned main | P | P2 |
|---|---|---|---|
| late dT (600-1000 mean) above +5 C | 2 (+5.54, +6.55) | **0** (warmest +4.75) | **0** (warmest +4.41) |
| late dT median above +5 C | 2 | 0 | 0 |
| dT at 1000 Myr above +5 C (a single moment) | 6 | 6 | 4 |
| hottest single moment after 600 Myr (hell line +15.5) | +12.4 | +11.9 | +11.9 |
| late median above +10.5 (hell) | 0 | 0 | 0 |

Pinning pulls the warm tail in as well as the cold one: the planets that drew a low yardstick (y 0.93-1.12) and ran
hot, such as r0.0005 l6fix 619496 (+6.55 C unpinned, y 0.931), are now +1.7 and +1.9 C. No planet is pushed over the
warm edge or toward hell. The end-moment count above +5 C is unchanged (single moments of a wandering climate; the
finish-moment check, which picks the shown moment, is in the soft pass below).

## 5. Soft passes

The judge bar plus the finish moment (`judge.py paired`, the pass count):

| | passes | against unpinned main |
|---|---|---|
| unpinned main | 30/36 | |
| pinned P | 33/36 | both 27, main only 3, P only 6; McNemar p 0.51 |
| pinned P2 | 31/36 | both 25, main only 5, P2 only 6; McNemar p 1.00 |
| P against P2 | | both 28, P only 5, P2 only 3; p 0.73 |

Within chance: P against P2 (a do-nothing nudge) moves 8 of 36 draws, as many as pinning does (9 and 11), and lane
24's null change moved 15.

## What this means for PW-1424

- **Option A is sound but its forecast was too optimistic.** It removes a dice roll that is not physics, it narrows
  the across-planet spread by about a third (2.64 to 1.7-1.9 C), it removes the cold tail and the warm tail, and it
  breaks nothing on the hard bar or the soft passes. Those are reasons to build it.
- **It cannot reach 1.2 C between re-runs of one planet**, because the chaos from one identical state is already
  1.4 C. Judging by single draws will keep a spread of about 1.4-1.8 C. That strengthens round 1's options B (judge
  "ends frozen", PW-1425) and the paired, continuous judge (PW-994): one history in 72 failed frozen-over here purely
  on glacial timing, and none ends frozen.
- The forked judge (PW-1403) is still made unnecessary for the yardstick, but not for the chaos.

## Files
- `tools/pin2.py` (pin.py + an optional after-fork nudge), `tools/pin_full.py` (the read-out); runs, spins, symlink
  roots and outputs in the session scratchpad `l160/` (`judge/P_*`, `judge/P2_*`, `fork/`, `hb_*.txt`, `pj_*.txt`,
  `ana.txt`, `extra.txt`).
- Run cost: 30 spins (300 Myr, 3 threads) and 72 continuations (700 Myr, 1 thread, ~20 min each), about 3.3 h on 12
  cores.
