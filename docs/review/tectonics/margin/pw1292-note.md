# PW-1292: sediment piles born continental (lane 112)

## In plain words

Daniel chose option A: a sediment pile on the ocean floor turns into continent only where it touches its own
plate's continent; isolated piles stay ocean floor however thick. A is in (`crust.birth_and_cratons`). But the trace
shows that isolated piles were never the problem. On main only about one pile birth in ten is isolated, and with the
sea-floor creep only one in fifty. The churn the ticket is about is margin wedges: sediment piled against the
continent's own edge reaches 20 km, turns continental, then thins below 20 km and is cut off again as a shred by the
coherence rule. A leaves that loop untouched, so A on its own does not cure the creep's churn.

## Where pile births happen (tracediag.py `births`, L6, 1 Gyr, cells / scale^2)

Every birth is classed when it happens: an arc (crust thickened mostly by arc rock), a pile next to continental crust
of its own plate (at least one world-grid neighbour), or an isolated pile. Shreds are coherence's thin continental
cells turned back to ocean floor; `shred_sed` counts those whose rock was SEDIMENT (born from a pile).

| arm, seed | arc births | piles touching | piles isolated | shreds (all) | shreds of pile rock |
|---|---|---|---|---|---|
| main, 1 | 428 | 193 | 23 | 1309 | 21 |
| main, 3 | 412 | 261 | 37 | 1103 | 26 |
| main + creep, 1 | 988 | 1064 | 22 | 3308 | 659 |
| main + creep, 3 | 1057 | 1406 | 32 | 3756 | 838 |

(600-1000 Myr. Creep = `neck_km=200 rise=1 slope_k=1000`. Isolated piles over the run, 0-1000 Myr: 54 and 76 cells on
main, 52 and 58 with the creep; under 2 of them on hotspots.)

Reading:
- Isolated piles are 11-12% of pile births on main and 2% with the creep. They are not where the creep's extra
  births come from.
- With the creep, pile births next to the continent rise five-fold, and about 60% of them come back as shreds of pile
  rock (659 of 1064, 838 of 1406). The loop: the creep and the rise feed the margin's foot to 20 km, the cell turns
  continental with one or two continental neighbours, the creep or erosion thins it, and below 20 km with at most 2
  continental neighbours it is a shred (`coherence`). The birth bound and the shred bound are the same 20 km, so the
  margin's outer cell can flip back and forth.
- What A changes in the budget: it removes 5-10% of pile births on main (23-37 cells per 400 Myr at 20-25 km, about 500-800 km x
  cells of the born flux of 13 000-14 500). With the creep it removes about 2%.

## Screens (L6, seeds 1 / 3, late = 600-1000 Myr, `born` and `coherence` from sim.budget, km x L5 cells)

| arm | land % | cont % | late dT (C) | pCO2 (ppm) | born | coherence |
|---|---|---|---|---|---|---|
| main | 33.3 / 34.7 | 40.7 / 41.1 | -1.3 / -1.2 | 819 / 753 | 13 200 / 14 500 | -6 200 / -4 300 |
| A | 34.6 / 33.3 | 40.4 / 40.9 | -0.1 / -0.9 | 1012 / 961 | 12 700 / 14 400 | -4 000 / -6 600 |
| main + creep | 31.5 / 31.0 | 41.8 / 41.1 | +0.4 / -3.2 | 961 / 528 | 42 100 / 50 600 | -41 200 / -46 200 |
| A + creep | 33.1 / 31.9 | 42.0 / 42.1 | +0.8 / -2.7 | 1146 / 581 | 43 000 / 43 500 | -40 700 / -39 900 |
| A3 + creep | 29.7 / 31.6 | 40.8 / 41.3 | -5.5 / -3.9 | 405 / 452 | 51 400 / 45 400 | -45 800 / -42 000 |

A against main: land +1.3 / -1.4, dT +1.2 / +0.3. At two seeds that is the noise of a changed plate history (the
deep dive's +-3 C per seed between arms). The born flux is the same within 5%. A + creep against creep: the churn
(born +43 000, coherence -40 000) is unchanged on seed 1 and 14% smaller on seed 3.

A3 is a screen-only variant (`pile_touch=3`): a pile is born only when at least 3 of its neighbours are its plate's
continental crust, so it is never a shred at birth (the coherence rule's own bound). It tests whether the churn is
the wedge-shred loop. It isn't: the churn stays (born +51 000 / +45 000, coherence -46 000 / -42 000), pile rock is
still shredded at the same rate (690 / 660 cells), and both seeds ran colder (-5.5 / -3.9 C). A3 is dropped.

## So where is the creep's churn?

With the creep, coherence shreds about 3300-3800 cells per 400 Myr against 1100-1300 on main, and only 660-840 of
them are pile rock. Births of the arc class (crust mostly basement, little cover) also double, 990-1060 against
410-430. No arc process doubles with the creep, so the likeliest reading is a flicker of the thinned margin: necking
(`neck_km`) and the creep stripping the cover leave the continent's outer cells near 20 km, which is both the birth
bound and the shred bound. A cell that thins below 20 km with at most two continental neighbours is shredded (it
keeps its thickness), and when sediment or crust flow brings it back to 20 km it is born again, as "arc" because its
crust is mostly basement. This isn't proven: the trace doesn't tag shredded cells. The cheap next check is to tag them
and count their rebirths. The fix would then be hysteresis between the two bounds (for example, a shred only below
~15 km, or a re-birth only above ~25 km). That's a draft (draft-margin-cells-flicker-at-the-20-km-bound), not part of
A.

The creep-on-A judge was not run: the screen shows A doesn't touch the churn (the brief's condition, "if the creep-on-A
screen looks promising", isn't met).

## Judge

(below, when it has run)
