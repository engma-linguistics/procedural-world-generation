"""The taboo catalogue (PW-1311): kinds of taboo, the specific rules a culture can draw within each, what makes each likelier, and where
each comes from. Data only; taboos.py draws from it. Food taboos keep their own logic in taboos.py (kind "food").

Sources, read by lane 133 on 2026-11-02 (web fetch; "read" = the page itself, "summary" = a summary of a study, "secondary" = an
encyclopedia page summarising others, "abstract" = only an abstract or a search snippet). Nothing here is cited from memory. Where a
source gives no driver, the drivers below are JUDGEMENT (marked "driver: judgement"), and every probability not tied to a D-PLACE count
is JUDGEMENT too.

Tags a culture carries (taboos.context): ways forage, hunt, herd, farm, sea; techs burial, temples, kingship, high_god, metal, writing;
its gods' leading domains as "g:<domain>" (gods.DOMAINS); "spells" when one of its gods grants them.
"""

from __future__ import annotations

SOURCES = {
    "wp_taboo": ("Wikipedia, Taboo", "https://en.wikipedia.org/wiki/Taboo", "secondary"),
    "wp_food": ("Wikipedia, Food taboo", "https://en.wikipedia.org/wiki/Food_taboo", "secondary (first half read)"),
    "wp_tapu": ("Wikipedia, Tapu (Polynesian culture)", "https://en.wikipedia.org/wiki/Tapu_(Polynesian_culture)", "secondary"),
    "wp_totem": ("Wikipedia, Totemism", "https://en.wikipedia.org/wiki/Totemism", "secondary"),
    "wp_dead": ("Wikipedia, Taboo on the dead", "https://en.wikipedia.org/wiki/Taboo_on_the_dead", "secondary"),
    "wp_naming": ("Wikipedia, Naming taboo", "https://en.wikipedia.org/wiki/Naming_taboo", "secondary (Chinese-sphere cases only)"),
    "wp_avoid": ("Wikipedia, Avoidance speech", "https://en.wikipedia.org/wiki/Avoidance_speech", "secondary"),
    "wp_incest": ("Wikipedia, Incest taboo", "https://en.wikipedia.org/wiki/Incest_taboo", "secondary"),
    "wp_menses": ("Wikipedia, Menstrual taboo", "https://en.wikipedia.org/wiki/Menstrual_taboo", "secondary (first ~100k of 282k chars)"),
    "wp_grove": ("Wikipedia, Sacred grove", "https://en.wikipedia.org/wiki/Sacred_grove", "secondary"),
    "wp_sumpt": ("Wikipedia, Sumptuary law", "https://en.wikipedia.org/wiki/Sumptuary_law", "secondary (first 100k of 141k chars)"),
    "wp_untouch": ("Wikipedia, Untouchability", "https://en.wikipedia.org/wiki/Untouchability", "secondary (first 100k of 192k chars)"),
    "wp_smith": ("Wikipedia, Blacksmith", "https://en.wikipedia.org/wiki/Blacksmith", "secondary (no smith taboos found in it)"),
    "ea036": ("D-PLACE, Ethnographic Atlas EA036 post-partum sex taboo", "https://d-place.org/parameters/EA036", "read (counts)"),
    "ea015": ("D-PLACE, Ethnographic Atlas EA015 community marriage organization", "https://d-place.org/parameters/EA015", "read (counts)"),
    "ea034": ("D-PLACE, Ethnographic Atlas EA034 high gods", "https://d-place.org/parameters/EA034", "read (counts)"),
    "ea066": ("D-PLACE, Ethnographic Atlas EA066 class differentiation", "https://d-place.org/parameters/EA066", "read (counts)"),
    "saucier": ("HRAF summary of Saucier 1972, post-partum sex taboo correlates", "https://hraf.yale.edu/documents/106", "summary (not the paper)"),
    "mishmi": ("Journal of Ethnobiology 40(2), hunting taboos of the Idu Mishmi",
               "https://bioone.org/journals/journal-of-ethnobiology/volume-40/issue-2/0278-0771-40.2.149", "abstract"),
    "colding": ("Colding & Folke 2001, Social taboos: invisible systems of local resource management", "(search result only)", "abstract"),
}

# kind -> (name, one line, sources, base chance a culture holds one, the most rules of it). Chances are JUDGEMENT unless the line says
# which D-PLACE count they come from.
KINDS = {
    "food": ("food", "animals, plants or parts not eaten (taboos.py: symbolic, identity, divine, purity origins)", ("wp_food",), 1.0, 0),
    "totemic": ("totemic and clan", "a clan's kin species, not harmed or eaten; clan mates do not marry", ("wp_totem",), 0.25, 2),
    "purity": ("ritual purity and the dead", "contact with the dead or with blood defiles until cleansed; the defiled keep from sacred things",
               ("wp_dead", "wp_tapu"), 0.6, 2),
    "speech": ("speech and names", "names and words not spoken: of the dead, of rulers and ancestors, of in-laws", ("wp_dead", "wp_naming", "wp_avoid"), 0.55, 2),
    "kinship": ("kinship and marriage", "who may not marry or lie with whom; who must avoid whom", ("wp_incest", "ea015", "wp_avoid"), 1.0, 3),
    "postpartum": ("birth and the marriage bed", "the post-partum sex taboo (EA036: 364 of 372 societies hold one)", ("ea036", "saucier"), 0.98, 1),
    "women": ("women, blood and birth", "menstruating or birthing women kept apart, from shrines, kitchens or men's things", ("wp_menses", "wp_tapu"), 0.8, 2),
    "place": ("sacred places", "groves, springs, peaks and graves set apart: no cutting, hunting or entering", ("wp_grove", "wp_tapu"), 0.6, 2),
    "time": ("sacred times", "spans under restriction: mourning, closed seasons, the gods' days", ("wp_tapu", "wp_dead", "wp_grove"), 0.5, 2),
    "resource": ("hunting and harvest", "limits on what may be taken and how: closures, the share left, respect to the kill",
                 ("wp_tapu", "mishmi", "colding"), 0.45, 2),
    "rank": ("chiefly and royal", "a ruler's person, food and things are dangerous to the lowly", ("wp_tapu", "wp_taboo"), 1.0, 2),
    "sumptuary": ("sumptuary", "dress, ornament and display kept to rank", ("wp_sumpt",), 1.0, 2),
    "caste": ("contact and caste", "groups ranked by purity: who may eat, draw water, touch or marry with whom", ("wp_untouch", "wp_incest", "wp_smith"), 1.0, 2),
}

# a kind's chance x these per tag the culture has (JUDGEMENT, with the driver the source states where it states one)
KIND_BOOST = {
    "totemic": {"forage": 1.6, "hunt": 1.3, "kingship": 0.6},  # driver: judgement (wp_totem states theories, no ecological driver)
    "purity": {"burial": 1.4, "temples": 1.3, "g:death": 1.3, "g:ancestors": 1.2},
    "speech": {"burial": 1.3, "kingship": 1.3, "writing": 1.2},
    "place": {"g:forest": 1.4, "g:mountain": 1.2, "g:river": 1.2, "burial": 1.2},
    "time": {"burial": 1.3, "temples": 1.4, "sea": 1.2},
    "resource": {"forage": 1.7, "hunt": 1.5, "sea": 1.3, "farm": 0.6},
    "rank": {"kingship": 0.85, "high_god": 0.95},  # only with kingship: chance 0.85 (driver: judgement, rank needs rulers)
    "sumptuary": {"kingship": 0.6, "metal": 1.3},  # only with kingship (wp_sumpt: to make rank visible)
    "caste": {"kingship": 0.25, "temples": 1.4, "metal": 1.3},  # only with kingship (wp_incest: stratified societies often endogamous)
}
# kinds that are only possible with this tag
KIND_NEEDS = {"rank": "kingship", "sumptuary": "kingship", "caste": "kingship"}

# EA036, read: post-partum sex taboo length, societies of 372
POSTPARTUM_EA036 = (("none", 8), ("up to a month", 74), ("one to six months", 120), ("six to twelve months", 39), ("one to two years", 73),
                    ("more than two years", 58))
# Saucier 1972 (summary): the long taboo goes with extensive farming and is rarer with herding, foraging, fishing and intensive farming.
# JUDGEMENT: the two long bins x LONG_FARM for farmers without kingship (extensive), x LONG_OTHER for the rest.
LONG_FARM, LONG_OTHER = 1.5, 0.75
# EA015, read: community marriage organization; clans + exogamous + segmented with exogamy = 362 of 1102 societies are exogamous
EXOGAMY_P = 362 / 1102

# the rules: (id, kind, rule, who, needs (all), boost (tag -> weight x), source)
RULES = [
    # totemic and clan
    ("totem_kin", "totemic", "a clan does not kill or eat its totem kind", "a lineage", (), {"hunt": 2.0}, "wp_totem"),
    ("totem_marry", "totemic", "members of one totem do not marry", "everyone", (), {}, "wp_totem"),
    # ritual purity and the dead
    ("corpse_unclean", "purity", "whoever touches a corpse or enters a house of the dead is unclean until cleansed", "everyone", ("burial",), {}, "wp_dead"),
    ("priests_no_dead", "purity", "priests may not touch the dead or walk near graves, save for their nearest kin", "priests", ("temples",), {"g:death": 1.5}, "wp_dead"),
    ("unclean_from_shrine", "purity", "the unclean keep away from shrines and sacred things until purified", "everyone", ("temples",), {}, "wp_dead"),
    ("mourners_silent", "purity", "the closest mourners do not speak until the dead are laid to rest", "kin of the dead", ("burial",), {}, "wp_tapu"),
    ("grave_night", "purity", "nobody goes among the graves between sunset and sunrise", "everyone", ("burial",), {"g:ancestors": 1.5}, "wp_dead"),
    # speech and names
    ("dead_name", "speech", "the name of the dead is not spoken while the mourning lasts", "everyone", ("burial",), {"g:ancestors": 1.5}, "wp_dead"),
    ("dead_soundalike", "speech", "words that sound like a dead person's name are replaced by others", "everyone", ("burial",), {}, "wp_dead"),
    ("ruler_name", "speech", "the ruler's name is not spoken or written in full; like-sounding words are changed", "everyone", ("kingship",), {"writing": 1.5}, "wp_naming"),
    ("ancestor_names", "speech", "the names of the clan's ancestors are not used for the living", "a lineage", ("burial",), {}, "wp_naming"),
    ("inlaw_words", "speech", "a wife avoids words that share a syllable with her parents-in-law's names", "women", (), {}, "wp_avoid"),
    # kinship and marriage
    ("incest_core", "kinship", "no marriage or lying together of parent and child or of brother and sister", "everyone", (), {}, "wp_incest"),
    ("clan_exogamy", "kinship", "nobody marries within their own clan, kin or not", "everyone", (), {}, "ea015"),
    ("cousin_one_side", "kinship", "one kind of cousin may not be married; the other kind is the preferred match", "everyone", (), {}, "wp_incest"),
    ("royal_sibling", "kinship", "only the ruling house may marry brother to sister", "the rulers", ("kingship",), {}, "wp_incest"),
    ("rank_endogamy", "kinship", "nobody marries below their rank", "everyone", ("kingship",), {}, "wp_incest"),
    ("motherinlaw", "kinship", "a man may not look at or speak to his mother-in-law; they speak through a third person", "men", (), {}, "wp_avoid"),
    ("fatherinlaw", "kinship", "a woman avoids her father-in-law", "women", (), {}, "wp_avoid"),
    # birth (post-partum: the length is drawn from EA036 in taboos.py)
    ("postpartum", "postpartum", "a nursing mother and her husband do not lie together for {span}", "parents", (), {}, "ea036"),
    # women, blood and birth
    ("menses_hut", "women", "a menstruating woman stays apart, in a hut of her own, for some nights", "women", (), {"forage": 1.3}, "wp_menses"),
    ("menses_kitchen", "women", "a menstruating woman does not cook or enter the kitchen", "women", (), {"farm": 1.3}, "wp_menses"),
    ("menses_shrine", "women", "a menstruating woman does not enter the temple or touch the gods' images", "women", ("temples",), {}, "wp_menses"),
    ("women_peak", "women", "women do not climb the sacred mountain or enter certain shrines", "women", (), {"g:mountain": 2.0}, "wp_menses"),
    ("birth_apart", "women", "a woman about to give birth goes to a shelter apart", "women", (), {}, "wp_tapu"),
    ("menses_silence", "women", "menstruation is not spoken of before men", "women", (), {}, "wp_menses"),
    # sacred places
    ("grove_fell", "place", "no tree is felled in the sacred grove", "everyone", ("g:forest",), {}, "wp_grove"),
    ("grove_hunt", "place", "no animal is hunted or plant uprooted in the sacred grove", "everyone", ("g:forest",), {"hunt": 1.5}, "wp_grove"),
    ("grove_inner", "place", "nobody but the priest enters the inner grove", "everyone", ("g:forest", "temples"), {}, "wp_grove"),
    ("spring_outsider", "place", "outsiders do not draw from the sacred spring or enter its ground", "outsiders", ("g:river",), {}, "wp_grove"),
    ("gateway_tree", "place", "the old trees that are doors to the spirit world are never cut", "everyone", (), {"g:forest": 2.0, "g:ancestors": 1.5}, "wp_grove"),
    ("burial_ground", "place", "the burial ground is fenced and nobody crosses it", "everyone", ("burial",), {}, "wp_tapu"),
    # sacred times
    ("mourning_span", "time", "for the span of the mourning (months, years for a great one) the dead person's kin stay under its bans", "kin of the dead", ("burial",), {}, "wp_dead"),
    ("closed_season", "time", "a priest's word closes the fishing ground or the hunt for a season", "everyone", (), {"sea": 1.5, "hunt": 1.3}, "wp_tapu"),
    ("royal_hunt", "time", "the ruler's forest is closed to hunting and cutting save for one hunt a year", "everyone", ("kingship",), {"g:forest": 1.5}, "wp_grove"),
    ("goddess_days", "time", "the temple shuts on the goddess's own days", "everyone", ("temples",), {"g:fertility": 1.5}, "wp_menses"),
    ("tapu_span", "time", "a person under a rite (a tattooing, an initiation) is set apart until it ends", "the initiated", (), {}, "wp_tapu"),
    # hunting and harvest
    ("restraint", "resource", "the hunter takes no more than the household needs, or the forest turns against the whole kin", "hunters", (), {"hunt": 1.5}, "mishmi"),
    ("rahui", "resource", "a closed shore or reef is not fished until the priest lifts the ban", "everyone", ("sea",), {}, "wp_tapu"),
    ("kin_liability", "resource", "one hunter's breach falls on all his kin", "hunters", (), {"forage": 1.5}, "mishmi"),
    ("sacred_kind", "resource", "the kind sacred to the hunt god is neither hunted nor eaten", "everyone", ("g:hunt",), {}, "wp_food"),
    # chiefly and royal
    ("chief_house", "rank", "the ruler's house is tapu: nobody else eats in it", "everyone", (), {}, "wp_tapu"),
    ("chief_food", "rank", "food made for the ruler may not be eaten by the lowly", "the lowly", (), {}, "wp_tapu"),
    ("chief_things", "rank", "the ruler's clothes and things are not to be touched", "everyone", (), {}, "wp_tapu"),
    ("chief_feeds", "rank", "the highest ruler does not feed himself and is fed by others", "the ruler", ("high_god",), {}, "wp_tapu"),
    # sumptuary
    ("dye_rank", "sumptuary", "the rare dye is worn only by the rulers and their officers", "everyone", (), {}, "wp_sumpt"),
    ("feathers_ruler", "sumptuary", "the rare plumes are for the ruler's head alone", "everyone", (), {"hunt": 1.3}, "wp_sumpt"),
    ("fur_rank", "sumptuary", "fine furs are for the high-born", "everyone", (), {"herd": 1.3}, "wp_sumpt"),
    ("grave_rank", "sumptuary", "the size of a grave marker is fixed by rank", "everyone", ("burial",), {}, "wp_sumpt"),
    ("commoner_white", "sumptuary", "commoners wear only undyed cloth", "commoners", (), {"farm": 1.3}, "wp_sumpt"),
    ("weapon_rank", "sumptuary", "only the warrior rank may bear the long blade", "everyone", ("metal",), {}, "wp_sumpt"),
    # contact and caste
    ("caste_eat", "caste", "the lowest rank may not eat with others", "everyone", (), {}, "wp_untouch"),
    ("caste_water", "caste", "the lowest rank may not draw from the common well or pond", "the lowest rank", (), {}, "wp_untouch"),
    ("caste_temple", "caste", "the lowest rank may not enter the temples or the others' houses", "the lowest rank", ("temples",), {}, "wp_untouch"),
    ("caste_work", "caste", "the work with the dead, hides and filth is kept to the lowest rank", "the lowest rank", (), {"herd": 1.3}, "wp_untouch"),
    ("caste_burial", "caste", "the lowest rank is buried apart", "the lowest rank", ("burial",), {}, "wp_untouch"),
    ("smith_endogamy", "caste", "smiths marry only within the smiths", "smiths", ("metal",), {"g:smithing": 2.0}, "wp_smith"),
]
RULE = {r[0]: r for r in RULES}
assert all(r[1] in KINDS and r[6] in SOURCES for r in RULES)
