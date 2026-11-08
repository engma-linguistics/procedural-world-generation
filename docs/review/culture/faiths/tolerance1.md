# Religious tolerance, towns and a faith's appeal, round 1 (lane 219: PW-1520)

Baseline: main at `c2e54f2b`, the same three runs (0141d1, 3e0eb4, 07c755), gods.json rebuilt into a scratch folder with `planet religion --out`.

## In plain words

**What you asked for (Daniel, 11-09).**
1. A separate tolerance of other faiths, so a tolerant ruler lets faiths mix.
2. Bigger towns making a culture more tolerant.
3. Faiths that spread partly on their own merits.

**What it does now.**

- **Every culture has two tolerances.**
  - The old one is now tolerance *of outsiders*. Conquest in the history and the trade tolls still read it.
  - The new one is *religious tolerance*. Both start from the same temperament and history. The religious one is lowered a little when the culture's own faith is missionary (an exclusive faith that seeks converts). It also wanders on its own random draws, so the two can drift apart.
  - Religious tolerance now sets three things:
    - how hard a ruler pushes its faith on its subjects;
    - how readily a culture takes a neighbour's faith;
    - how fast a culture's own faith absorbs its minorities.
  - It also adds one new thing: a ruler that is more tolerant than its subjects shields their minorities in the land it rules (the protected faiths of the caliphates).
- **Towns raise both tolerances.** Each culture's share of people living in towns and cities comes from the settlement ledger. A culture with a tenth of its people in towns gains +0.1 on both tolerances. That is as much as the widest contact gives. A culture with no towns gains nothing. The ledger covers only the last ~12,000 years, so this only counts from then on.
- **A faith's own appeal now counts** when it spreads to a neighbour. A ruler's push is force, so appeal does not change it. Appeal has two parts:
  - **Organisation.** A church whose leading god is a moralizing high god spreads at the rates already sourced (Stark's early Christianity). A faith with only temples spreads at about half that pace.
  - **Fit.** A faith whose leading god would suit the neighbour's land and way of life better than the neighbour's own god spreads up to 1.5 times as fast. One that suits it worse spreads as slowly as half the pace.
  - Missionary effort was already in the model: a missionary faith wins neighbours ten times faster than an ordinary one. I added nothing to it.

**What changed in the numbers.** Each figure is a mean over six re-rolls of the faith draws, main's code against the new code on the same runs:

| | 0141d1 main | 0141d1 new | 3e0eb4 main | 3e0eb4 new | 07c755 main | 07c755 new |
|---|---|---|---|---|---|---|
| cultures with a single minority faith above 10 % | 6.6 % | 6.0 % | 5.7 % | 5.6 % | 5.3 % | 6.1 % |
| states with two or more faiths at 10 %+ | 97 % | 97 % | 51 % | 59 % | 98 % | 99 % |
| states where the ruler's faith is under half | 87 % | 87 % | 29 % | 31 % | 91 % | 93 % |
| conversions: all | 66 | 52 | 217 | 197 | 63 | 55 |
| conversions: by neighbours (contact) | 27 | 18 | 23 | 18 | 18 | 12 |
| conversions: by missionaries | 0 | 0 | 71 | 61 | 0 | 0 |
| conversions: forced by rulers | 39 | 34 | 124 | 118 | 46 | 43 |
| living faiths now | 84 | 86 | 43 | 50 | 73 | 78 |
| tolerance (of outsiders), 10th / 50th / 90th percentile | .26/.51/.80 | .27/.53/.83 | .21/.48/.81 | .26/.54/.86 | .29/.58/.88 | .30/.60/.90 |
| religious tolerance, 10th / 50th / 90th | (same as tolerance) | .27/.52/.83 | (same) | .25/.52/.84 | (same) | .31/.60/.91 |
| town cultures (3 %+ in towns): tolerance / religious | .55 / .55 | .59 / .59 | .44 / .44 | .54 / .50 | .65 / .65 | .69 / .71 |
| rural cultures (under 1 % in towns): tolerance / religious | .44 / .44 | .45 / .45 | .49 / .49 | .51 / .50 | .49 / .49 | .49 / .49 |

The single draw that `planet religion` makes gives the same picture:

| | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| minority above 10 %, main → new | 18 → 14 of 279 | 23 → 23 of 267 | 14 → 17 of 272 |
| states with two or more faiths at 10 %+, main → new | 244 → 252 of 258 | 178 → 250 of 278 | 282 → 277 of 284 |
| conversions, main → new | 53 → 42 | 223 → 203 | 57 → 52 |

How to read this:

- **Towns now clearly raise tolerance.** Town cultures are now 0.04 to 0.10 more tolerant than they were on main. Rural ones barely move. Town cultures were already more tolerant on main on two of the runs, because they rule more and touch more peoples. On 3e0eb4 they were *less* tolerant than rural ones (0.44 against 0.49): its missionary dwarf faith rides with the town-building rulers. The towns now flip that to 0.54 against 0.51 on tolerance of outsiders. On religious tolerance they come out about even, 0.50 against 0.50, because a missionary faith lowers the religious axis.
- **Fewer conversions, more faiths alive.**
  - Conversions by neighbours fell by a quarter to a third. A temple-level faith next door now has to be well organised and suit the land to win converts. That is the appeal rule working as meant.
  - Forced conversions fell 4-14 %, inside the re-roll noise. The split alone changes little here, because rulers already read the one tolerance.
  - Living faiths rose by 2 to 7 on every run.
- **Minorities are not measurably larger.** The share of cultures with a minority above 10 % stays inside the spread of the re-rolls on all three runs. There are two reasons, and they pull against each other:
  - A tolerant culture still absorbs its minorities more slowly. It also takes a neighbour's faith more readily, and that existing rule is unchanged.
  - The appeal rule cuts conversions, and every conversion is what creates a large minority (the old faith stays on).
  - The new ruler's shield adds only +0.1 to +0.25 points (measured by switching it on alone). On 3e0eb4 the share of states with several faiths rises from 51 % to 59 %, but the re-rolls range from 28 % to 90 %, so this is not a clear signal.
  - **What would make minorities grow** under a tolerant ruler is something the model lacks: free movement and mixing *between* the cultures of one realm. For example, a town's people drawn from several cultures would each bring their own faith. That needs the towns-and-minorities model PW-1369 deferred. It is drafted below.
- **Which faith each culture leads with does change.** On the same draw, 27-41 % of cultures lead with a different faith than on main. But re-rolling main's own draws changes 30-47 %. So the change is about the size of chance, and no faith family systematically wins or loses. Comparing by faith family, following each faith back through its schisms, gives the same figures.
  - Why is it this large? Every conversion is a random waiting time. Change any rate slightly and the first waiting time differs, and then every later draw differs as well.
  - The systematic part is in the table above: fewer neighbour conversions, so more cultures keep the faith they founded.

**What you see in the viewer.**

- **Religion > Minorities:** the states table has a new *ruler's religious tolerance* column, and the cultures table a *religious tolerance* column. Hover the column header for what it means.
- **Religion > Taboos culture card:** it reads, for example, *tolerance 0.68, of other faiths 0.49, aggression 0.96, 11.0% in towns*.
- **Gods format** is now `procgen-gods/3`, so the server re-works out any older gods.json on first view (a few seconds plus the inputs read). Stored gods.json files on the owner's runs are older; rebuild them with `planet religion <run>` when convenient.

## Sources

I fetched each of these. The *direction* of the town effect is sourced; its *size* is a judgement.

- **Huggins, C. M. & Debies-Carl, J. S. (2015).** "Tolerance in the city: the multilevel effects of urban environments on permissive attitudes". *Journal of Urban Affairs* 37(3): 255-269. doi:10.1111/juaf.12141. Abstract fetched from the University of Kentucky scholars page. It finds that "local urban environments promote tolerance cross-nationally", while urbanization at the level of a whole society does not always help. That is why the model reads each culture's own towns, not a world-wide urban rate.
- **The urbanism-tolerance literature: Wilson (1985), "Urbanism and tolerance: a test of some hypotheses drawn from Wirth and Stouffer", *American Sociological Review* 50(1).** Seen in search results with summaries of Stouffer 1955 (urbanites more tolerant; the Wirth-Stouffer link to a city's size, density and heterogeneity). One summary adds that Williams, Nunn and St. Peter's 1976 replication found city size significantly associated with tolerance. Another adds that Abrahamson and Carter 1986 found the net city-size effect declining after 1947-82, and usually smaller than region's.
  - I could not fetch the full texts or a numeric effect size: the PDFs were paywalled, and the GSS report was scanned images. So URBAN_TOL is a JUDGEMENT, set no larger than the existing contact step (CONTACT_TOL 0.1), because Wirth's mechanism is concentrated contact.
- **"La Convivencia", Wikipedia (fetched 2026-11-08).**
  - In Cordoba, Christians and Jews "took part in the royal court and contributed to the city's rich intellectual and cultural life".
  - Non-Muslims could practise their religion "on condition of submission to Muslim rule and payment of jizya". That protected status is the basis of the ruler's shield.
  - The Almohads "rejected the mainstream Islamic doctrine that established the status of dhimmi" and "forced Christians and Jews to convert". So the same cities turned intolerant under intolerant rulers, which the model allows: a ruler's religious tolerance, not the city, sets the push.
  - The page also records the scholarly debate (Nirenberg, Cohen, Manzano Moreno) over how real the tolerance was. That is a reason to keep the city bonus modest.

## The mechanism

All of it is read-out only. The peoples history is untouched: `polity_live` passes no towns and no faiths, so the history's tolerance and aggression draw exactly as before.

- `attitudes.py`:
  - `Attitudes.rel[c]` holds the religious tolerance. It drifts as an Ornstein-Uhlenbeck walk with the same TAU_ATT and DRIFT_SD, on its own random generator `(seed, 904, 1520)`, so the other two axes draw exactly what they did. A test checks this.
  - `target()` returns `[tolerance, aggression, religious tolerance]`. MISSION_TOL now lowers only the religious one.
  - Both tolerances gain URBAN_TOL x min(1, urban / URBAN_FULL), where URBAN_TOL = CONTACT_TOL = 0.1 and URBAN_FULL = 0.10, both JUDGEMENT.
  - The ledger's urban share of the present cultures on 0141d1: median 1.8 %, 90th percentile 3.7 %, top 1 % over 12 %, highest 29 %. None before ~5 kyr ago.
  - The read-out's `now` is `[tolerance, aggression, religious tolerance]`, with `urban` beside it. The track rows gain a fourth number. `trade_flow._tolerance` reads the first two as before.
- `gods.py`:
  - `urban_reader()`: for each frame in the land-use window, the people in ledger sites at or above their holder's town size, as `trade._urban` counts them, divided by the culture's heads (meta.eraq density x cell area). A cell shared by two cultures splits half and half. Each frame carries `urban`, and `Pantheons.frame()` hands it to the attitudes.
  - Every rate that read `tolerance` now reads `religious()`: a ruler's push (`_links`), a taker's receptiveness (`_links`, `_pulls`), and a culture's own faith absorbing its minorities (`_pulls`, ASSIM_RULE).
  - `_pulls` also shields a subject: it absorbs its minorities at its own religious tolerance plus share x (ruler's - its own), when the ruler is the more tolerant.
  - `Pantheons.appeal(x, lx, ly)` multiplies only the neighbour links (contact and missionaries). It is organisation x fit:
    - organisation: the converter's leading-god individuation / ORG_REF, where ORG_REF is the top faith tier, 0.9;
    - fit: 1 + FIT_W x (fy - fx) / (fy + fx). Here fy and fx are the *settled* fits (`_settled_fit`) of the converter's leading god and of the taker's own leading god to the taker's salience. Settled means each group's weight moved onto the taker's salient domains of that group, the end point `_drift` already models: a sky god serves under any sky, a sea god only where there is water. FIT_W = 0.5 is a JUDGEMENT, so the fit never drops the pull to nothing (a faith is its church and promise as much as its god's domain).
- Tests: `tests/test_faith_spread.py`.
  - Appeal rises with organisation and fit.
  - Towns raise both tolerances, and the missionary term lowers only the religious one.
  - The religious axis does not disturb the other two.
  - A ruler's push follows religious tolerance, not tolerance of outsiders.
  - A tolerant ruler shields its subjects' minorities.
  - The missionary-wait test now puts both cultures on the same land, so their fit is even. It still checks that a missionary faith wins a neighbour within centuries.

## Measuring (reproducible)

Scratch scripts, deleted with the scratch folder:
- `variants.py`: the split, the towns and the appeal switched on one at a time, on one draw.
- `reroll.py`: six seeds, main's package from `git archive c2e54f2b` against this branch.
- `rr_measure.py`: the tables above.

Main-vs-new on one draw can mislead here. Any change of rate re-rolls every later conversion, so read the means over re-rolls.
