# Minority faiths, round 1 (lane 205: PW-1489, D57)

## In plain words

**What you asked for.** Daniel, 11-07 (D57): keep the even missionary chance, and "some way to track minority religions in a people/region".
Until now each culture held exactly one faith.

**What it does now.** Each culture holds a **share of each faith**. The faith named everywhere else (the map, the timeline, the taboos, the
culture briefs) is still the one held by **more than half**, and it is exactly the same faith as on main: same conversions, same dates, same
counts, on all three runs checked. What is new is what sits under it:

- **Before a culture converts**, a faith pressing on it (a missionary neighbour, a temple faith next door, a ruler) wins its first converts
  and grows to **at most about a tenth** of the culture. That is the plateau Bulliet found in Iran before the take-off.
- **When the culture converts** (the same random event as on main), the newcomer passes **half**, and the old faith **stays on as a minority**.
- **After that**, the minority fades. The culture itself wins it over: in a millennium or two at middling tolerance, within centuries if the
  culture is intolerant, and over ten thousand years or more if it is very tolerant. Neighbours and rulers of the new faith speed this up.
  Recently converted or conquered cultures therefore carry large minorities, and long-settled ones carry almost none.
- **Daughter cultures** carry their parent's minorities. **Merged cultures** pool their faiths by land.
- **States and peoples** add up their cultures by land, so a conquered empire shows how mixed it is.

**What you see.** For example, "aarakocra of Hizam" on run 0141d1 now reads *faiths: the mountain schism of first goliaths of Hizam 94%,
the mountain faith of first aarakocra of Tozes 6%*.

**The numbers (today's present, same worlds, new code compared with main):**

| run | living cultures | with any minority | with a minority faith above 10 % | of those, ever converted |
|---|---|---|---|---|
| 0141d1 (D&D) | 279 | 208 | **17 (6 %)** | 16 |
| 3e0eb4 (D&D, your dwarf faith) | 267 | 149 | **14 (5 %)** | 14 |
| 07c755 (Seven Meals, measured only) | 272 | 217 | **28 (10 %)** | 27 |

Total minority share in a culture, by its history:

| run | converted by rulers (conquered): median / mean / 90th pct | converted by neighbours or missionaries only | never converted |
|---|---|---|---|
| 0141d1 | 2.0 / 11.0 / 37.8 % (n=35) | 6.0 / 10.3 / 35.4 % (n=27) | 1.0 / 2.5 / 5.5 % (n=217) |
| 3e0eb4 | 0.8 / 3.8 / 9.9 % (n=92) | 1.0 / 3.9 / 9.1 % (n=67) | 0.6 / 2.0 / 5.7 % (n=108) |
| 07c755 | 4.0 / 11.7 / 39.2 % (n=57) | 3.5 / 7.2 / 17.7 % (n=42) | 1.8 / 3.2 / 8.0 % (n=173) |

"Converted" means it ever took a faith by a conversion event. A culture converted long ago has had time to absorb its minority, so the median
is low and the tail is long. The tail is the cultures converted in the last millennium or two, and those are the ones with large minorities.
Of the 498 never-converted cultures across the three runs, only 2 carry a single minority above 10 % (one on 0141d1, one on 07c755; a
never-converted culture can only get a large minority from a merge or from its parent).

**States are faith-plural.** On 0141d1 and 07c755 the ruling culture's faith holds under half of its own realm in 227 of 258 and 217 of 286
states (median 31-32 %). On 3e0eb4, where your missionary dwarf faith rides with its rulers, that drops to 83 of 267 (median 67 %). This is
not new behaviour: it is today's majority faiths, read out by land. Ethnic (non-missionary) rulers push their faith at a tenth of the rate
(ETHNIC_RULE), so their subjects mostly keep their own gods. Before, there was no way to see it.

## The mechanism (planet/lineages/gods.py)

- `Pantheons.comp[c]`: `{faith: share}` summing to 1. The culture's faith (`faith_of`) always holds at least half. That is an invariant,
  and the tests check it.
- **Same events, no new random draws.** The Gillespie loop in `_conversions` already works out the links (`_links`) between events. The
  shares are advanced over each waiting interval with those same links (`_shares`), plus the pulls of a culture's own faith (`_pulls`). The
  exponential waits and the choice of link draw exactly the numbers they did on main. The test
  `test_minorities_do_not_change_the_majority_history` checks this, and all three runs agree to the event.
- **Pressing a culture (before it converts).** For each link (rate r per kyr), the pressed faith's share follows a logistic at
  k = r x SHARE_SPAN from SHARE_SEED = 1 %, toward SHARE_PLATEAU = 10 %. SHARE_SPAN = ln(99) is chosen so that, without the plateau, a link's
  mean wait 1/r would carry 1 % to half. That is the reading of Stark that TAU_MISSION already rests on.
- **Why a plateau, not a climb to half.** The conversion event is memoryless (an exponential wait). If the share kept rising to half while
  the event had not yet come, the two would disagree. My first try did exactly this, with no plateau. A third of all cultures then sat at
  50/50, waiting for an event that a long tail of exponential waits had not delivered. The plateau makes the event the take-off. Nudging it
  to 5 % or 20 % changed the count of cultures with a minority above 10 % from 17 to 17 and 18 (0141d1).
- **Conversion (`_join(..., "flip")`).** The newcomer is set to max(its share, 50 %), and the rest is scaled down proportionally. Founding,
  schisms and written faiths rename instead: the culture moves as a body and keeps its minorities.
- **Assimilation (`_pulls`).** Once a culture holds a faith, its own faith presses its minorities at
  ASSIM_RULE x the rulers' push at the culture's own tolerance: 1 / (TAU_FORCED^(1-tol) x TAU_TOLERANT^tol) x 0.1. That is ~2.5 kyr at
  tolerance 0.5, ~0.5 kyr at 0.1 and ~15 kyr at 0.9. Every neighbour of the same faith and every ruler of it add their link rates, using the
  same formulas as the conversion links. Without this, a minority nobody pressed stayed frozen for 250 kyr. Nudges on 0141d1: ASSIM_RULE 0.05
  gives 24 cultures with a minority above 10 %, 0.1 (chosen) gives 17, 0.2 gives 12. The count moves smoothly, and the majority faiths are
  identical in every arm.
- **Split** copies the parent's shares. **Merge** pools both cultures' shares by their cells at the last frame. The survivor's faith stays
  the merged culture's faith, as on main. If the pooled share of that faith falls under half, it is set to half and the rest are scaled down
  (`share_counts.merge_capped`: 35 / 23 / 22 merges on the three runs). This is a judgement call, filed as a draft (below).
- **Roll-ups (`share_rollup`).** The states, empires and dragon realms that rule at the last polity step get their cultures' shares weighted
  by each culture's cells inside the polity (`rule_table()["now"]`). Peoples get theirs weighted by each living culture's cells.
- Output: `cultures[c].shares` = `[[faith, share], ...]` (its faith first, then the largest SHARE_TOP-1 = 3, then `[null, the rest]`), and a
  top-level `shares` = `{rule, states, peoples, summary}`. The format is now `procgen-gods/2`.

## What changes downstream

- **Majority faiths, histories, events and counts: nothing.** They are identical on 0141d1, 3e0eb4 and 07c755 (`fhist`, `faith_now`, every
  conversion event with its date and how, and `summary.faiths`).
- **Faith end (`ended_kyr`)** still means "no culture holds it as its faith". A faith can now end while it survives as a minority somewhere.
  The timeline still says "no followers left" for it, which now reads slightly wrong: it means no *majority* anywhere. This is left as is.
- **The server (`planet/server.py::gods_doc`)** serves a saved `gods.json` only when it is `procgen-gods/2`. The disk cache key includes the
  format. The saved `gods.json` of every existing run is `/1`, so the first Religion-tab open of each run replays it: ~80-105 s per run,
  measured here, then cached. Regenerating with `planet gods` (it writes into the run) avoids that wait. That is the coordinator's call.
- Replay time is unchanged within noise: 82 / 81 / 89-105 s against 85 / 84 / 90 s on main.

## How Daniel sees it in the viewer

- **Peoples workbench → Results: pick the run → Religion → Minorities** (new, between Timeline and Taboos). It has three tables:
  - **States now**: each state, empire or dragon realm with its kind, size, ruling culture and faiths, e.g. "Razukum (humans) 32 · state ·
    the rain schism of first lizardfolk of Razukum 31%, the forest faith of first green dragons of Luki 23%, ..., others 14%".
  - **Cultures with minorities**: the largest minorities first.
  - **Peoples**: each people's faiths by land.

  The bar above them reads, for example, "279 cultures with a faith now: 208 hold a minority faith, 17 one above 10%".
- **Religion → Taboos**: the culture card's line "faith: X" is now "faiths: X 94%, Y 6%".
- **Cultures tab**: the gods column gains a grey line "faiths: X 78%, Y 15%, others 7%" for each culture that holds a minority.

## Not done (left for a later pass)

- A **regional map of minorities** (the Map view still colours each cell by its culture's majority faith). Colouring by share would need
  `faithmap.py` to dither or hatch, which is not cheap.
- Minorities do **not** feed back into anything: taboos, gods, schisms and conversion rates all read the majority faith only.
- **Minority shares over time** are not stored (only now). A history would need a per-frame snapshot.

## Sources (fetched for this lane, 2026-11-07)

- **Bulliet 1979**, *Conversion to Islam in the Medieval Period*. I could not fetch the book. The figures used are as reported in Wikipedia,
  "Spread of Islam" (https://en.wikipedia.org/wiki/Spread_of_Islam, fetched 2026-11-07). It quotes Bulliet's "conversion curve": "a relatively
  low rate of conversion of non-Arab subjects during the Arab centric Umayyad period of 10%", Muslims growing "from around 40% in the
  mid-9th century" with "almost the entire population being converted by the end of the 11th century". The same page reports the
  persistence of minorities under tolerant rule: "the continuing existence of large minorities of Christians during the Abbasids", "Syria
  may have had a Christian majority until the Mongol invasions of the 13th century", and Hourani: Christians, Jews and Zoroastrians "were not
  forced to convert, but they suffered from restrictions". A search result (Goodreads/OEAW listings of the book) confirms the S-shaped
  curve and the chapter "The Curve of Conversion in Iran". The book is also cited in docs/review/culture/attitudes/round1.md.
- **Stark 1996**, *The Rise of Christianity*. I could not fetch the book. Its figures are as summarised by Scott Alexander, "Book Review: The
  Rise Of Christianity" (https://www.astralcodexten.com/p/book-review-the-rise-of-christianity, fetched 2026-11-07): "In 40 AD, there were
  maybe a thousand Christians", "some historians have tentatively suggested a 10% population share" by 300 AD, "about 6 million people",
  and "From 1,000 to 6,000,000 in 260 years implies a 40% growth rate per decade".

## Reproduce

Scratch scripts (not kept): replay each run read-only with `gods.derive(run_dir)` on main and on this branch, then compare
`cultures[c].faiths`, `faith_now`, the conversion events and `summary.faiths`. Nudges: override `SHARE_PLATEAU` or `ASSIM_RULE` on the
module before `derive`.
