---
id: PW-1246
title: "How dragons lose ground to people: thinned on the farmland they keep, or cleared from it like lions and tigers"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane99
blocked_by: []
relates: [PW-1232, PW-1221, PW-1068]
refs: [docs/review/dragon-numbers/report.md, planet/lineages/history/megafauna.py, docs/review/dragon-numbers/census.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** Real lions and tigers lost most of their land to people. Lions keep 6-13% of their old range and tigers under 7%,
but where they still live they are not rare. The model's dragons already end up with about the same share of their country for most
kinds. They get there in a different way, though. The kill never clears them from a place: it thins them, and they also stay out of
much of their country for other reasons (the food cap, rival kinds). Do you want the lion-and-tiger pattern made explicit? That would
mean cleared from busy farmland, safe in the wilds. Or should dragons stay thinned everywhere? The next lane needs your call before
tuning anything.

Evidence. These numbers come from the lane 99 census on main after D20 and PW-1229: six worlds at roll 7000, report section 3. They
are medians over the worlds.
- **How much of its country each kind holds at a tenth or more of its pre-people density.**
  - Six kinds hold 4-14%: red 12%, blue 14%, green 4%, white 9%, gold 13%, silver 5%.
  - Four kinds hold more: bronze 29%, brass 26%, copper 32%, black 68%.
- **Peopled country against empty country.** Several kinds hold far less of their peopled country than of their empty country:
  blue 9% against 73%, white 2% against 31%, silver 4% against 38%, gold 12% against 41%. But 82-100% of every kind's country is
  peopled, so the empty refuges are small.
- **On the cells they still hold.** There, the peoples' kill and overkill take dragons from ~134,000 (no people) to ~80,000 (today).
- **The kill itself.** The kill (`megafauna.dragon_kept`) is "never zero" by design (owner 10-29: never species-ending).
- **Lions.** Loveridge et al. 2022: 13% of the maximum historical range. IUCN 2025, via a news factbox: 6.13% (secondary).
- **Tigers.** Walston et al. 2010: under 7%. Sanderson et al. 2023: over 93% of the range empty of tigers.

Options:
- **A. Keep it.** The shares of country already sit near the lions' and tigers' for most kinds. The density where dragons do live is
  thinned, not left whole.
- **B. Local extirpation.** Where the kill would need births to rise more than some multiple (say BREED_X x 2), the dragons fade from
  that cell. Dragons would then live at near their natural density in fewer places: the lion and tiger pattern, without ending a
  species.
- **C. Habitat avoidance.** Leave the kill as it is, and have dragons read their habitat as poorer where people are dense. That gives
  the same pattern through habitat, not through killing.

Lean: A for now, and B if the viewer's dragon maps look too evenly smeared over farmland. The counts are already in the range the
analogues suggest. B changes where the dragons are, not how many there are, and it needs a threshold judgement from the owner.

## Updates
- 2026-10-31: Owner 10-31: inclined to B and/or C; wants more dragons and a per-run abundance lever; questions the KILL_Q anchor. Lane 103, one round.
- 2026-10-31: Created from inbox draft draft-dragon-range-loss-to-people.md (found by lane99).
