# More god domains (PW-1523, lane 236, D68 note "We need more domains in general")

**In plain words.** The gods had 20 domains in five groups. There was no moon, no healing, no law, no kingship, no trade, no wine or
feast, no wisdom or writing, no winter and no earthquake. This lane adds ten domains. Each one comes from something the model already
knows, so it turns up where it fits: winter where the land is cold, the earthquake on plate boundaries, wine and beer gods where the
brewing techs exist (which the crops gate), kingship where a culture rules others, trade where the goods ledger lists goods to trade.
Every scale is a JUDGEMENT. The sources only show that each domain recurs across many unrelated pantheons, and what it tends to go with.

## The thirty domains (gods.GROUPS)

| group | domains (new ones in bold) |
|---|---|
| water | sea, river, rain, flood |
| sky | sky, sun, **moon**, storm, **winter** |
| land | mountain, fire, **earthquake**, forest, desert |
| life | herd, hunt, harvest, fertility, **feast**, **healing** |
| human | hearth, smithing, **craft**, death, war, ancestors |
| order (new) | **kingship**, **law**, **wisdom**, **trade** |

The group matters because a god drifts within its group (gods._drift): a sea god taken inland becomes a rain god. The new "order" group
holds the domains of the state and the town. A kingship god can drift into a law god as a realm gains law and writing, but never into a
storm god.

## Drivers (gods.salience; every scale is JUDGEMENT)

- **moon**: 0.25 everywhere, because every world has a sky with a moon in it. Calendars, astronomy and tide lore add 0.2, a coast adds up
  to 0.2, and hunting adds up to 0.15. [LUNAR] ties moon gods to calendars ("Many cultures are oriented chronologically by the Moon").
  The tide and hunting terms are JUDGEMENT. The only sourced tide link is Alignak, the Inuit god of "weather, water, tides, and eclipses"
  [EARTH].
- **winter**: the share of the culture's land in subarctic or polar climate classes, full at COLD_FULL = 0.4. [WINTER] lists 17 winter
  and 17 ice-and-snow deities. Skaði is "associated with bowhunting, skiing, winter, and mountains" [SKADI].
- **earthquake**: the share of land on or next to a plate boundary (the world's `plate_boundary` layer), full at QUAKE_FULL = 0.25.
  Wikipedia has no list page for earthquake gods. [EARTH] and [QUAKE] give Poseidon (Greece), Rūaumoko (Māori), Namazu (Japan), Tē-gû
  (Taiwan), Geb (Egypt) and Alignak (Inuit). That most of these come from active margins is our reading, not a claim the sources make.
  This is the thinnest-sourced domain.
- **feast** (wine, beer, mead): 0.1, plus 0.15 for feasting, 0.3 for any brewing or wine tech (beer, wine, mead, chicha, palm wine, rice
  wine, hopped ale), and 0.1 for fermentation. In the tech tree each drink is gated by its crop, so the crop drives the domain. [WINE]
  lists about 25 cultures (Ninkasi, Dionysus, Ægir, Osiris, Mayahuel), and names Bes the "patron of beer brewers".
- **healing**: 0.15, plus 0.25 for herbal medicine, 0.15 for surgery or trepanation, and up to 0.3 for the share of people in towns
  (crowding and disease: JUDGEMENT). [HEALTH] lists about 31 cultures (Asclepius, Dhanvantari, Sekhmet, Gula, Eir, Ixchel). [ASKL]
  counts over 300 healing temples in Greece.
- **craft**: pottery, weaving, the potter's wheel and guilds each add 0.15, and towns add up to 0.2. [ART] lists about 25 cultures with
  pottery and weaving gods (Panthoibi, Mamiyo, Hephaestus). Bait Pandi is the "goddess of weavers who taught women weaving". Smithing
  stays its own domain.
- **kingship**: chiefdoms add 0.1, the kingship tech 0.35, and towns up to 0.2. Ruling cultures of other peoples, in a state, empire or
  dragon realm (gods.rule_table), adds KING_RULER = 0.3 while the rule lasts. [SACRED] covers sacred kings in about 20 cultures. Gods
  there come to kingship through rulers claiming them ("An emperor might also adopt a major deity as his personal patron", [TUT]).
  Dumézil's first function is sovereignty [TRI].
- **law**: the law tech (or tide councils) adds 0.3, writing 0.15 and bureaucracy 0.15. In Egypt the pharaohs "were believed to rule
  through [Maat's] authority", and the Maat temple at Karnak "was also used by courts to meet" [MAAT]. [JUST] lists about 86 justice
  deities.
- **wisdom** (writing and lore): writing, proto-writing, shell script or runes add 0.3, libraries or schools 0.2, and calendars or
  astronomy 0.1. [KNOW] lists about 25 cultures (Thoth, Seshat, Nabu, Nisaba, Tir, Itzamna). Seshat is "credited with the invention of
  writing".
- **trade**: the trade tech adds 0.15, markets, coinage or commodity money 0.15, and towns up to 0.2. The goods ledger (trade.py) adds
  up to 0.4: the goods a culture has beyond the average plus the goods it lacks, full at six (TRADE_FULL). The ledger covers only the
  land-use window, the last ~12.5 kyr; before that only the techs and towns count. [COMM] lists 16 commerce gods (Hermes, Mercury,
  Turms, Ek Chuah, Ebisu, Veles). Mercury's temple stood by the Circus Maximus, "a major center of commerce" [MERC].

## Also D68 5A: second and third gods rise

The second and third gods by devotion (RISE_N = 2) now reach the faith techs' ceiling without the high god (kingship 0.6, temples 0.45)
where their own domain is salient: full at RISE_SAL = 0.6, otherwise by the old devotion rule. A war god where war fills life, or a
harvest god on farmland, can now reach temple rank and sit in a pantheon's seat. The leading god, and so every conversion, is chosen as
before.

## Left out, on purpose

- **Trickster**: the most widespread figure of all [TRICK], about 85-90 traditions. But it is a kind of character, not a domain the land
  or the techs would drive, so it belongs with names and myths (PW-986).
- **Love**: [LOVE] lists about 29 cultures. The model has nothing that would make love salient in one land and not another, so for now
  fertility stands in for it.
- **Night**: [NIGHT] lists about 13 cultures, and the list overlaps the moon and death heavily.

## Sources (fetched 2026-11-08 by the lane's source agent; the long pages were read in part)

- [LUNAR] Lunar deity, https://en.wikipedia.org/wiki/Lunar_deity, and List of lunar deities, https://en.wikipedia.org/wiki/List_of_lunar_deities
- [WINTER] Category: Winter deities, https://en.wikipedia.org/wiki/Category:Winter_deities
- [SKADI] Skaði, https://en.wikipedia.org/wiki/Ska%C3%B0i
- [EARTH] List of earth deities, https://en.wikipedia.org/wiki/List_of_earth_deities
- [QUAKE] Earthquake ("In culture"), https://en.wikipedia.org/wiki/Earthquake
- [WINE] List of deities of wine and beer, https://en.wikipedia.org/wiki/List_of_deities_of_wine_and_beer
- [HEALTH] List of health deities, https://en.wikipedia.org/wiki/List_of_health_deities
- [ASKL] Asclepeion, https://en.wikipedia.org/wiki/Asclepeion
- [ART] List of art deities, https://en.wikipedia.org/wiki/List_of_art_deities
- [SACRED] Sacred king, https://en.wikipedia.org/wiki/Sacred_king
- [TUT] Tutelary deity, https://en.wikipedia.org/wiki/Tutelary_deity
- [TRI] Trifunctional hypothesis, https://en.wikipedia.org/wiki/Trifunctional_hypothesis (the page is flagged for possibly machine-written text; used only for the three functions)
- [MAAT] Maat, https://en.wikipedia.org/wiki/Maat
- [JUST] Category: Justice deities, https://en.wikipedia.org/wiki/Category:Justice_deities
- [KNOW] List of knowledge deities, https://en.wikipedia.org/wiki/List_of_knowledge_deities
- [COMM] Category: Commerce gods, https://en.wikipedia.org/wiki/Category:Commerce_gods
- [MERC] Mercury (mythology), https://en.wikipedia.org/wiki/Mercury_(mythology)
- [TRICK] Trickster, https://en.wikipedia.org/wiki/Trickster
- [LOVE] List of love and lust deities, https://en.wikipedia.org/wiki/List_of_love_and_lust_deities
- [NIGHT] List of night deities, https://en.wikipedia.org/wiki/List_of_night_deities
- [COMP] Comparative mythology, https://en.wikipedia.org/wiki/Comparative_mythology

**Joint gods (D68 1C, pantheons.JOINT_P).** Matching two gods is routine. Rulers "regularly [identified] local deities in various parts
of their domains" [SYNC], and Mercury was matched with Wotan and Lugus [MERC]. A brand-new joint god is rare and comes from a ruler's
policy in a realm of several peoples. Serapis was spread "on the orders of ... Ptolemy I Soter" as "a means to unify the Greek and
Egyptian subjects", although the cult may have existed before him [SER]. Hermanubis, a combined name, "was not common in traditional
Greek religion" and is known from only "a handful" of sources [HERM]. So pantheons.py makes a joint god only under a ruler of several
peoples (an empire hub), and only with JOINT_P = 0.1 of new seats. The rarity is sourced. The number is a JUDGEMENT: no source gives a
rate.

- [SER] Serapis, https://en.wikipedia.org/wiki/Serapis
- [HERM] Hermanubis, https://en.wikipedia.org/wiki/Hermanubis
- [SYNC] Syncretism, https://en.wikipedia.org/wiki/Syncretism

## Results on the stored L7 runs (lane 236, read-only replays, 2026-11-09)

Pantheons living now (D68 3A target: 2-8 per world, under a third of the land), with the empire threshold HUB_SUBJ = 2.0:

| run | world | living pantheons (ever) | land in reach | seats now | adopted / joint gods |
|---|---|---|---|---|---|
| 0141d1 | D&D | 5 (16) | 4.7% | 9 | 1 / 0 |
| a24559 | D&D | 3 (16) | 2.5% | 7 | 2 / 0 |
| a2b637 | D&D | 1 (15) | 0.1% | 0 | 1 / 0 |
| 3e0eb4 | D&D, missionary dwarf faith | 0 (23) | 0% | 0 | 1 / 0 |
| 07c755 | Seven Meals tree, earthlike | 15 (39) | 10.5% | 52 | 9 / 6 |
| 216848 | Seven Meals world (frozen: measured only) | 0 (30) | 0% | 0 | 2 / 3 |

Before HUB_SUBJ, any ruler of a second people was a hub: 0141d1 then had 39 pantheons over 42% of the land. With HUB_SUBJ 0.5, 1,
2 and 4 it had 20, 13, 5 and 4. a24559 and a2b637 did not change (their hubs are towns).

The new domains, compared with the same runs on main (c2e54f2b..a1db4525 code): living beings rise from 1,709 to 2,880 on 0141d1, and
from 1,712 to 2,895 on 3e0eb4. Most of the rise is the order, feast and craft gods of cultures that have the techs. On 0141d1, 279
cultures have gods. A being's leading domain is feast in 242 cases, trade in 238, law in 203, craft in 201, kingship in 191, moon in 85,
winter in 33, earthquake in 28, wisdom in 14 and healing in 11. At temple rank (individuation 0.45 or more), trade has 92 beings, moon
66, feast 53, winter 13 and earthquake 4 (main: none). The four order domains drift into one god per culture ("power of trade and
wisdom"), because a god drifts within its group. Conversions on 0141d1 go from 42 on main to 36. On 3e0eb4 they go from 203 to 191. On
0141d1, 80% of cultures keep the same faith as on main (64% on 3e0eb4). The leading gods are still nature gods, so the change comes
through the schisms and core moves.
