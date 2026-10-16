---
id: PW-367
title: "Time zoom: marine ice margins have no shelves or ice streams: West Antarctica collapses unforced, shallow shelves ground"
type: task
status: done
parent: null
subsystem: timezoom
effort: m
impact: med
found_by: tzbatch-2026-10-16
blocked_by: []
relates: [PW-361, PW-241, PW-295, PW-114]
refs: [planet/timezoom.py, docs/review/timezoom/batch-2026-10-16.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The time zoom's marine fronts lose ice at `calving` x water depth (m/yr of retreat) and any floating ice
breaks off at once: no ice shelves (no buttressing) and no ice streams (the shallow-ice flow at ~110 km
cells moves ~100-200 m/yr at a front, real ice streams 0.4-4 km/yr). Two symptoms with opposite signs:
- **Deep fronts retreat.** Earth L6 from today with the orbit held fixed (`obliquity_amp=0 ecc_mean=0
  ecc_100=0 ecc_400=0 orbit_ref=start`): West Antarctica's whole marine sector goes in ~10 kyr (95 of 1003
  Antarctic ice cells, all on beds below the sea, median -670 m; Amundsen and Siple coasts), 2.3 Mkm3 and
  -3.8 m of sea-level equivalent above flotation; then Antarctica stays at ~22.1 Mkm3 for the rest of a
  1 Myr zoom (the true bed since PW-354 made this visible: the floored bed had no marine ice). A front
  ~670 m deep needs ~670 m/yr of inflow to stand; the flow can't supply it. Unbuttressed, a marine sheet
  on a retrograde bed is unstable (Schoof 2007), so this is the model's physics, not a bug in it; the real
  sheet stands because the Ross, Ronne and Amundsen shelves hold it back.
- **Shallow fronts advance.** Around Greenland the ice grounds on 37 shelf cells in 20 kyr (unforced), and
  from a run's cold moment the sheets ground on ~440 shelf cells (median 540 m deep, PW-241). Ice flowing
  off a land margin into a few hundred metres of water is thicker than flotation and the depth-scaled
  calving is slow there. (The run's ice doesn't ground on shelves at all, so a time zoom from a run's
  moment grows onto them at first.)

Options:
- A. **Cold-ocean buttressing:** where the sea beside a marine front stays frozen in summer (an ice shelf
  can survive: `ocean.open_share` ~ 0), calving is reduced (a shelf's buttressing factor, ~0.2-0.5);
  elsewhere tidewater calving as now. Keeps West Antarctica, still collapses it under a warm Eemian-like
  summer; one new factor.
- B. **Flotation calving criterion** (van der Veen 1996, Vieli et al. 2001): a front stands where its ice is
  more than (1 + q) x flotation thick and calves what is thinner. West Antarctica's coastal marine cells
  are ~460 m above flotation (median), so they'd stand; but fronts on shallow shelves would advance more
  easily (PW-241 the wrong way).
- C. **Accept** it as the model's (an unbuttressed marine sheet is unstable) and document; an Earth time zoom
  then loses West Antarctica in its first ~10 kyr whatever the orbit (+3-5 m is what the Eemian did, but
  it shouldn't happen at today's orbit).
Lean: A, because it adds the missing process (shelves) with the right sign at both kinds of front; tie
the factor to the observed buttressing (Fürst et al. 2016: Antarctic shelves carry most of the
grounding-line resistance), not to a sea-level score.
- [ ] an unforced Earth time zoom keeps West Antarctica's marine sector for 20 kyr (within ~10% of its cells)
- [ ] a warm Eemian-like start can still lose it

## Updates
- 2026-10-16: Status in-progress -> done. Done (85a7b96, 2bd5d6e): cold-ocean buttressing (0.8, Fürst 2016; air over sea < -10 C, ramp to -5 C, Morris & Vaughan 2003) plus floating shelves (thinner than flotation past the grounding line: no bed load, no sea level; Weertman spreading) and sub-shelf melt (10 m/yr per C). Earth unforced 20 kyr: WAIS keeps 136/149 marine cells, 10 shelf cells ground (was 96). +4 C Eemian: shelves break up, Amundsen keeps 24/35 at 20 kyr, 13 at 50 kyr (winter water never warms: new ticket). Unforced drift -11 m from Greenland's cold bias and Arctic margins. 1 Myr low point -24 -> -64 m.
- 2026-10-16: Status todo -> in-progress. Agent started (option A).
- 2026-10-16: Status needs-decision -> todo. Owner 2026-10-16: option A as the coordinator sees fit. Coordinator: A (cold-ocean buttressing tied to observed shelf buttressing, Fürst et al. 2016), scheduled with the next time zoom batch.
- 2026-10-16: Created from inbox draft draft-timezoom-marine-margins.md (found by tzbatch-2026-10-16).
