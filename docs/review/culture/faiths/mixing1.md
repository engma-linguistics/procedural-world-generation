# Faiths that come through towns, round 1 (lane 223: PW-1528)

Baseline: main at `18af4eee` (lane 219 merged). The same three runs as lanes 205 and 219 (0141d1, 3e0eb4, 07c755), each with six re-rolled
faith draws (the run's seed and the next five). The new code has a switch (`TOWNS_ON`); with it off, it is main. The first draw's off arm
on 0141d1 matches lane 219's single draw exactly: 14 of 279 cultures with a minority above 10 %, 42 conversions.

## In plain words

**What you asked for (Daniel, 11-08).** "Tolerant rulers allow more intermixing." Lane 219 found that minorities did not grow under
tolerant rulers, because a faith only ever moved between cultures by a conversion.

**What it does now.** Inside one realm (a state, an empire or a dragon realm), people move.

1. **A culture's towns draw people from the realm's other cultures, and under a tolerant ruler they keep their faith.**
   - Think of the Jewish, Greek and Armenian quarters of Ottoman Istanbul, or the Sogdian merchants in the Tang towns.
   - How much comes in depends on four things: the culture's share of people in towns (lane 219's reader of the settlement ledger), the
     ruler's religious tolerance, the culture's own religious tolerance, and how much of the realm holds other faiths.
   - Peoples who live in towns themselves (the trading peoples) send up to twice as many per acre of land. Cultures that touch the town's
     culture send twice as many as distant ones.
2. **From the town quarter, the faith wins converts in the land around it.** Early Christianity spread from the towns' diaspora
   communities outward, and the first converts to Islam in Persia were townsmen.
   - It spreads at the pace a neighbour of that faith would: a missionary faith in centuries, an ordinary one over millennia, faster if
     the faith is well organised and suits the land.
   - All the faiths that came through towns share one ceiling, about a tenth of the culture (Bulliet's plateau, as for any pressing faith).
     Each faith's part of that tenth follows its part of the people the towns draw.
   - It never tips the culture into converting. Conversions are still only the old events.
   - A closed faith (one that takes no converts) stays in its quarter.
3. **An intolerant ruler allows almost none of this.**
   - Its "protection" is its push on its own faith read the other way, on the same sourced scale. A fully tolerant ruler lets in 100 %, one
     at 0.7 about 28 %, one at 0.5 about 12 %, one at 0.3 about 5 %, and an intolerant one under 2 %. Think of the Almohads, or Castile
     in 1492.

**What changed in the numbers.** Each figure is a mean over six re-rolled draws, with the range across draws in brackets. "Tolerant
ruler" means the ruler of the state a culture mostly lives in has religious tolerance 0.6 or more; "intolerant" means under 0.4.

| | 0141d1 main | 0141d1 new | 3e0eb4 main | 3e0eb4 new | 07c755 main | 07c755 new |
|---|---|---|---|---|---|---|
| tolerant ruler: cultures with a minority above 2 % | 12.4 % [7.2-15.8] | **14.0 %** [9.6-17.3] | 22.6 % [15.9-28.6] | **26.4 %** [19.5-34.3] | 10.5 % [8.5-14.2] | **13.4 %** [11.7-15.5] |
| tolerant ruler: above 5 % | 9.8 % | 9.9 % | 14.8 % | **17.6 %** | 8.7 % | 8.9 % |
| tolerant ruler: above 10 % | 6.5 % | 6.5 % | 8.3 % | 8.2 % | 6.4 % | 6.4 % |
| tolerant ruler: mean minority share | 5.1 % | 5.3 % | 5.0 % | 5.4 % | 5.3 % | 5.6 % |
| intolerant ruler: above 2 % | 9.4 % | 9.4 % | 11.5 % | 12.0 % | 8.6 % | 9.6 % |
| intolerant ruler: mean minority share | 3.9 % | 3.9 % | 2.5 % | 2.5 % | 4.5 % | 4.7 % |
| cultures holding a faith that came through towns | 0 | 18-27 of 279 | 0 | 32-55 of 267 | 0 | 43-50 of 272 |
| states with two or more faiths at 10 %+ | 98.0 % | 98.0 % | 66.2 % | 66.4 % | 98.7 % | 98.7 % |
| conversions (all draws) | same | same | same | same | same | same |

The effect of the change itself, on the same draw (new minus main, for each of the six draws):

| | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| tolerant ruler, above 2 % (points) | +0.7 +2.0 +1.4 +1.4 +2.4 +1.4 | +5.7 +3.9 +2.8 +1.6 +3.5 +5.0 | +3.4 +3.6 +3.0 +2.7 +3.2 +1.3 |
| tolerant ruler, mean minority (points) | +0.2 on every draw | +0.2 to +0.6 | +0.3 to +0.4 |
| intolerant ruler, above 2 % (points) | 0 on every draw | 0 on five, +2.9 on one | 0 on five, +5.9 on one |
| intolerant ruler, mean minority (points) | 0.0 to +0.1 | 0.0 to +0.1 | 0.0 to +0.4 |

(The intolerant group has only 9-44 cultures, so a single culture is a 3-6 point step.)

How to read this:

- **Under tolerant rulers minorities grow, on every draw of every run.** About 1.5-4 more cultures in a hundred hold a minority above 2 %.
  - Measured on the same draw (the clean comparison: the majority faiths are identical), the gain is far outside the noise. Every one of
    the eighteen draws gains, and the intolerant group gains nothing on 16 of 18.
  - Measured across re-rolls, the means move by about half the re-roll range (7.2-15.8 % on 0141d1). The new mean is outside main's range
    only on 07c755's upper half. The re-roll spread of these counts is wide, because which cultures happen to be conquered and converted
    changes with every draw.
- **Under intolerant rulers, minorities stay as they were.** That is the bar.
- **The minorities that came through towns are small: a few percent, and none above 10 %.** That is the honest size.
  - The ledger puts a median of ~1.7 % of a culture's people in towns (90th percentile ~4 %). A town quarter of another faith is therefore
    a fraction of a percent of the culture, and its spread to the land about it stops under the shared tenth.
  - In real tolerant empires, the large minorities (Syria's and Egypt's Christians) are the conquered peoples' old faiths. The model
    already keeps those as conversion remnants, under the ruler's shield from lane 219. Diasporas were a few percent: the Jews of the
    Roman cities and the merchant quarters.
  - Whether you want mixing to make larger minorities (country migration, or a softer protection) is drafted below as a decision.
- **The leading faiths do not change at all.** On every draw of all three runs, every culture leads with the same faith as on main, and
  the conversions, their dates and their counts are the same. Re-rolling main's own draws changes a culture's leading faith 27 % (0141d1),
  45 % (3e0eb4) or 30 % (07c755) of the time. This is a read-out like the minorities: no new random draw, no conversion link, nothing that
  feeds back into the majority history.

**What you see in the viewer.** In the Peoples workbench, go to Results, then Religion, then Minorities.

- The cultures table has a new column, *came through towns*. Hover over its header for what it means. It lists each minority faith's part
  that settled through the towns or spread from them, as a faith name and a percentage of the culture.
- The bar above reads, for example, *272 cultures with a faith now: 227 hold a minority faith, 17 one above 10%, 43 one that came through
  towns*.
- The gods format is now `procgen-gods/4`. The server works out older gods.json files again on first view.

## Sources (fetched for this lane, 2026-11-08)

- **Istanbul's 1477 census:** "History of Istanbul", Wikipedia (fetched 2026-11-08).
  - The census found "9,486 houses occupied by Muslims; 3,743 by Greeks; 1,647 by Jews", "267 by Christians from the Crimea, and 31
    Gypsies". So 37 % of households were not Muslim, and 11 % were Jewish, a faith that was no one's majority in the realm.
  - Mehmed had "issued orders across his empire that Muslims, Christians, and Jews should resettle the city".
  - The city "was not to be entirely Muslim, at least not until the late 20th century".
  - This sets TOWN_MIX = 1, a town that draws from its realm as the realm is. It gives ~34 % for a ruler at religious tolerance 0.9, a town
    at 0.8, and a realm with ~60 % of other faiths. This is a sourced scale with a judged point: the census came a generation after a forced
    resettlement, not free migration.
- **Towns live on migrants:** the Cambridge Group's project page "Migration, mortality and medicalisation" (campop.geog.cam.ac.uk,
  fetched 2026-11-08).
  - Early modern cities were "demographic sinks with extraordinarily high mortality", and their highest mortality fell "among the young
    and migrants who were essential for city growth".
  - A search summary attributes to Wrigley that London needed over 8,000 net migrants a year. I could not fetch Wrigley's own text.
  - This supports TAU_TOWN = 0.1 kyr, a judgement: a town's mix follows its realm within generations.
- **Christianity spread from the towns:** Scott Alexander, "Book Review: The Rise Of Christianity" (astralcodexten.com, fetched 2026-11-08),
  summarising Stark 1996.
  - "Early Christianity was primarily an urban and upper-class movement".
  - About 5 million diaspora Jews were "concentrated in cities like Alexandria, Antioch, and Rome", and the first missionaries worked
    through those city networks.
  - The pace is already in the model (TAU_MISSION, from Stark's ~40 %/decade).
- **Islam spread from the towns:** "Spread of Islam", Wikipedia (fetched 2026-11-08).
  - In Persia, "conversion was fastest in urban areas where Arab forces were garrisoned", and Zoroastrianism later became mainly rural.
  - In West Africa, Islam spread "initially through the merchant class", and Arab merchants "became carriers of the new religion and
    propagated it wherever they went".
  - Under Muslim rule, Christians, Jews and Zoroastrians "were not forced to convert, but they suffered from restrictions" (Hourani).
- **Diasporas are a few percent:** "History of the Jews in the Roman Empire", Wikipedia (fetched 2026-11-08). It gives "perhaps 10 percent
  of the Roman Empire, or about 7 million people", but notes that "These population figures are very unreliable". It also says that
  "Many cities of the Roman provinces in the eastern Mediterranean contained very large Jewish communities".
- **Merchants of many faiths in a Tang port:** "Guangzhou massacre", Wikipedia (fetched 2026-11-08). Abu Zayd al-Sirafi gives 120,000
  "Muslims, Jews, Christians, and Zoroastrians" killed in 878-879. Morris Rossabi calls the figure "inflated". This is used only for the
  shape: one port held several foreign faiths at once.
- **The Sogdians:** "Sogdia", Wikipedia (fetched 2026-11-08). The Sogdians practised "Zoroastrianism, Manichaeism, Buddhism" and the
  Church of the East, and spread those faiths along the Silk Road. Their merchants appear in 29 of 35 commercial transactions in one
  Turpan tax document. The page gives no share of any Tang city.

## The mechanism (planet/lineages/gods.py)

All of it is a read-out. It adds no random draw and no conversion link, so `fhist`, the events and the counts are main's. A test checks this.

- `rule_table` rows gain a fourth field: the ruler culture's own land share inside the realm, so the ruler's towns count too.
- `Pantheons._towns(contacts, rule)`, once per polity stretch:
  - Each member y of a realm sends people in proportion to its land in the realm, times (1 + TOWN_SEND x min(1, its town share /
    URBAN_FULL)).
  - Members that do not touch the receiving culture x send at TOWN_NEAR.
  - x settles toward share(x) x urban(x) x TOWN_MIX x protection(ruler) x religious(x) x faith g's part of the draw, summed over its realms.
  - Faiths under half a percent in their own culture send no one. A community under TOWN_FLOOR = 0.01 % is ignored.
  - It also sets `spread`: for each member's majority faith, a rate equal to a neighbour link's (receptiveness x appeal / TAU_MISSION or
    TAU_CONVERT) x protection(ruler) x share(x), and a cap equal to SHARE_PLATEAU x that faith's part of the incoming draw. Closed faiths
    get none.
- `Pantheons._settle(town, dt)`, after each `_shares` step:
  - Each town share below its target relaxes toward it over TAU_TOWN.
  - Then each spreading faith follows the logistic toward its cap, starting from its own share or its town share (not jumping to the 1 %
    seed, so a faint quarter grows slowly).
  - It never pushes the culture's own faith under half.
  - A faith with a live town community is not folded away below SHARE_MIN (`_set_share`).
- `protection(tol) = (TAU_FORCED / TAU_TOLERANT)^(1 - tol)`. No new number.
- Read-out: `cultures[c].towns` = `[[faith, share], ...]`, the lesser of each faith's share now and all it ever gained through towns.
  `shares.summary.with_town_faith` counts the cultures that have one. `with_minority` now counts minorities of at least SHARE_MIN, which
  on main is the same thing.
- New numbers: TOWN_MIX = 1.0 (sourced scale, judged point), TAU_TOWN = 0.1 kyr, TOWN_SEND = 1.0 and TOWN_NEAR = 0.5. The last three are
  JUDGEMENT, and the code labels them so.
- Tests: `tests/test_faith_towns.py`.
  - Protection follows the push.
  - A tolerant realm's towns draw its other faiths, an intolerant one's 20 times less, and none without towns.
  - Town faiths settle and spread under a tolerant ruler while the majority history stays identical.
  - A closed faith keeps to its quarter.

## How I got here (the arms tried on 0141d1)

1. **Town quarters only.** The settled share is a fraction of a percent in almost every culture. Seven cultures out of 279 got one
   at 0.5 % or more, and nothing moved.
2. **A spread from towns seeded at the usual 1 %, with protection linear in the ruler's tolerance.**
   - The mean minority under tolerant rulers went from 5.1 % to 9.7 %, but under intolerant ones it went from 3.9 % to 7.3 % as well.
   - Every realm faith seeded 1 % in every member, so this was the seed, not mixing.
3. **The seed is the town quarter itself, and the protection is the push's log scale.** The intolerant group stays put, and the tolerant
   group gains as in the tables above.
   - The probe with linear protection on this arm raised the tolerant group's share above 2 % to 15.1 % (against 14.0 %), but the
     intolerant group's to 10.3 % (from 9.4 %). It is not adopted. The option is in the decision draft.

Scratch scripts (`reroll.py`, `measure.py`, `diag.py`) replayed each run read-only from cached inputs and are deleted with the scratch folder.

## Follow-ups (inbox drafts)

- `draft-town-faiths-small-at-ledger-town-shares.md` (needs-decision): keep the small town-borne minorities, add country migration inside
  a realm, or soften the protection.
