"""Food fit as a biology spectrum per people (PW-905; owner 10-26: "not just 'won't eat' but 'not an ideal fit'; some species love
what poisons others").

    fit(body)                 -> {food: {"level", "why", "basis", "src"}} for every food class in FOODS
    summary(body, grown=())   -> the four lists (thrives on, tolerates, poorly suited, harmful) plus the notable rows, for the
                                 cuisine sheet and the brief; `grown` (crop ids on the culture's land) marks a harmful or poorly
                                 suited food that its own fields grow
    line(body, grown=())      -> the one-line text ("Body and food: ...")

Read from the people's resolved body (spec.BODY_DEFAULT keys: milk, sweet, capsaicin, raw_meat, cellulose, toxic, diet, gut, grain,
bitter), so nothing new is authored per species: a body that already says "cats taste no sweet" or "birds feel no capsaicin" gets
its fit from the same keys. Levels, best to worst: thrives (its body is built for it), tolerates (fine in ordinary amounts),
poor (it can eat it, but it sits badly: discomfort, little gain, or a risk), harmful (poisons it, even in modest amounts).

Each row's `basis` is "sourced" (a real-biology finding for the nearest real body: humans for the human-like baseline, cats, dogs,
birds, deer for the rest; `src` names the entry in SOURCES, all fetched in lane 256, docs/review/food/lane256.md) or "judgement"
(a reading where no source was found, and every row for a fantasy body: lizardfolk, dragons, the saurian and bird stems are given the
nearest animal's biology, which is a call, not a measurement). The culinary side overrules any row.
"""

from __future__ import annotations

LEVELS = ("thrives", "tolerates", "poor", "harmful")
LEVEL_TEXT = {"thrives": "thrives on", "tolerates": "tolerates", "poor": "poorly suited to", "harmful": "harmed by"}

FOODS = (  # (id, label, crop ids on the land that are this food)
    ("fresh_milk", "fresh milk", ()),
    ("soured_dairy", "soured milk, yogurt and cheese", ()),
    ("cooked_meat", "cooked meat and fish", ()),
    ("raw_meat", "raw meat and fish", ()),
    ("aged_meat", "high meat (long-hung, near carrion)", ()),
    ("grain", "grain and pulses", ("wheat", "rye", "foxtail_millet", "sorghum", "rice", "maize", "pulses", "soybean", "cowpea", "stonegrain")),
    ("browse", "leaves, stalks and fibrous plants", ("greens",)),
    ("tannin", "acorns, bark and astringent browse", ()),
    ("sweet", "honey, sweet fruit and sugar", ("cane", "sap_sugar", "tree_fruit", "vine", "date_palm", "banana")),
    ("chili", "chili heat", ("chili",)),
    ("alcohol", "beer, wine and spirits", ()),
    ("caffeine", "tea- and coffee-like infusions", ("tea",)),
    ("cacao", "cacao (chocolate)", ("cacao",)),
    ("alliums", "onion and garlic", ("alliums",)),
)
LABEL = {k: lab for k, lab, _ in FOODS}

SOURCES = {  # fetched in lane 256 (docs/review/food/lane256.md has the quotes)
    "lactase": "Wikipedia, Lactase persistence and Lactose intolerance: most adults worldwide lose lactase (~65% malabsorb); persistence "
               "high in northern Europe and pastoralists, <=5% in East Asians and Native Americans; other mammals lose it after weaning",
    "ferment": "Wikipedia, Lactose intolerance: yogurt bacteria use up lactose; cheddar holds <1.5% of the lactose of the same mass of milk",
    "stomach": "Beasley et al. 2015 PLoS ONE 10:e0134116: scavengers and carnivores have more acid stomachs than herbivores; humans "
               "are near the carrion feeders",
    "tas1r2": "Li et al. 2005 PLoS Genetics 1:e3 (cat Tas1r2 a pseudogene); Jiang et al. 2012 PNAS (PMC3324019): sweet lost in many "
              "exclusive meat eaters (sea lion, spotted hyena, otter)",
    "trpv1": "Jordt & Julius 2002 Cell 108:421 (Duke abstract): capsaicin deters mammals; bird TRPV1 does not respond to it (Wikipedia, Capsaicin)",
    "adh4": "Carrigan et al. 2015 PNAS 112:458 (phys.org summary): an ADH4 change ~10 Myr ago let hominid ancestors oxidise ethanol well",
    "aldh2": "Wikipedia, ALDH2: about half of East Asians carry ALDH2*2 (acetaldehyde build-up, the flush)",
    "ethanol_pets": "Merck Veterinary Manual, Alcohols (search summary): dogs and cats sicken on ethanol (vomiting, ataxia, CNS depression)",
    "methylxanthine": "Merck Veterinary Manual, Chocolate toxicosis: theobromine and caffeine half-lives in dogs 17.5 h and 4.5 h; signs from 20 mg/kg",
    "allium": "Merck Veterinary Manual, Allium toxicosis: cats most susceptible, then dogs; Heinz body haemolytic anaemia",
    "tannin": "PMC7548203 (2020): browsing cervids such as mule deer have proline-rich (tannin-binding) saliva; the same study finds no "
              "browser/grazer difference across 28 African species (disputed)",
    "deer_meat": "Field & Stream (magazine, weak): deer take birds now and then, maybe for missing nutrients",
}


def _share(v) -> float:
    return 1.0 if v is True else 0.0 if v in (False, None) else float(v)


def _row(level: str, why: str, src: str | None = None) -> dict:
    return {"level": level, "why": why, "basis": "sourced" if src else "judgement", "src": src}


def fit(body: dict) -> dict:
    """Every food class's fit for one resolved body (spec.BODY_DEFAULT keys; missing keys read as the baseline)."""
    diet = body.get("diet", "omnivore")
    meat_eater = diet in ("carnivore", "obligate_carnivore")
    plant_eater = diet == "herbivore" or body.get("gut") in ("foregut", "hindgut") or _share(body.get("cellulose")) >= 0.5
    toxic = set(body.get("toxic") or [])
    out = {}
    lac = _share(body.get("milk"))
    out["fresh_milk"] = (_row("thrives", "digests milk as adults", "lactase") if lac >= 0.6 else
                         _row("tolerates", f"{round(100 * lac)}% digest milk as adults; the rest sicken on more than a little", "lactase") if lac > 0 else
                         _row("poor", "loses lactase after weaning: fresh milk bloats and gripes", "lactase"))
    out["soured_dairy"] = (_row("thrives", "a dairy body, and the lactose is fermented away", "ferment") if lac > 0 else
                           _row("tolerates", "fermenting takes most of the lactose out", "ferment"))
    raw = _share(body.get("raw_meat"))
    out["cooked_meat"] = (_row("thrives", "a meat eater", "stomach") if meat_eater else
                          _row("poor", "a plant eater's gut: meat now and then, never a staple (deer have been seen taking birds)", "deer_meat")
                          if diet == "herbivore" else _row("thrives", "an omnivore", None))
    out["raw_meat"] = (_row("thrives", "eats raw meat safely (a strongly acid stomach, as carnivores and scavengers have)", "stomach") if raw >= 0.5 and meat_eater else
                       _row("tolerates", "eats raw meat safely" if raw >= 0.5 else "fresh and well handled; a human-like stomach is acid, near the carrion feeders'", "stomach")
                       if raw > 0 or diet == "omnivore" else _row("poor", "a plant eater's stomach is the least acid: raw flesh carries what it cannot kill", "stomach"))
    scavenger = raw >= 0.5 and body.get("bitter") == "low"
    out["aged_meat"] = (_row("thrives", "a scavenger's stomach: what is high for others is ripe for it", "stomach") if scavenger else
                        _row("tolerates", "a raw-meat stomach takes meat well hung", "stomach") if raw >= 0.5 else
                        _row("poor" if diet != "herbivore" else "harmful", "near-carrion meat is a gamble for this stomach", None))
    grain = body.get("grain", "normal")
    out["grain"] = (_row("harmful", "its gut takes no grain", None) if grain == "none" else
                    _row("tolerates", "grain only in moderation, the gut adapted gradually (acidosis comes from sudden high-grain feeding)", None)
                    if grain == "moderate" else _row("poor", "a strict meat eater: starch is little use to it", None) if diet == "obligate_carnivore" else
                    _row("thrives", "grain and pulses suit it", None))
    out["browse"] = (_row("thrives", "ferments leaves and stalks (it digests cellulose)", None) if plant_eater else
                     _row("poor", "a meat eater's short gut gets little from leaves", None) if meat_eater else
                     _row("tolerates", "leaves as greens, not as fodder: no cellulose digestion", None))
    out["tannin"] = (_row("tolerates", "a browser: tannin-binding saliva, as browsing deer have", "tannin") if body.get("gut") == "foregut" else
                     _row("tolerates", "bitterness hardly troubles it", None) if body.get("bitter") == "low" else
                     _row("poor", "astringent and binding: acorns only after leaching", None))
    sw = body.get("sweet", True)
    out["sweet"] = (_row("thrives", "tastes sweet: honey and ripe fruit are treats", None) if sw is True else
                    _row("tolerates", f"only {round(100 * _share(sw))}% taste sweet", "tas1r2") if _share(sw) > 0 else
                    _row("poor" if diet == "obligate_carnivore" else "tolerates", "tastes no sweet (as cats and many strict meat eaters): sugar is texture, not a treat", "tas1r2"))
    cap = body.get("capsaicin", True)
    out["chili"] = (_row("thrives", "feels no capsaicin burn (as birds): the hottest peppers are only flavour", "trpv1") if cap is False else
                    _row("tolerates", f"{round(100 * _share(cap))}% feel the burn", "trpv1") if cap is not True else
                    _row("tolerates", "feels the burn: a liking is learned, or not", "trpv1"))
    methyl = "theobromine" in toxic
    pet = methyl or "alliums" in toxic  # (the cat-, dog- and bird-like bodies: the toxicity marker the presets already carry)
    out["alcohol"] = (_row("poor", "a cat-, dog- or bird-like liver: ethanol sickens it at small doses", "ethanol_pets") if pet else
                      _row("tolerates", "a hominid-like liver oxidises ethanol well (some peoples carry the flush)", "adh4"))
    out["caffeine"] = (_row("poor", "clears caffeine slowly (as dogs); a strong cup is a dose", "methylxanthine") if methyl else
                       _row("tolerates", "a stimulant in ordinary amounts", None))
    out["cacao"] = (_row("harmful", "theobromine poisons it (as dogs and cats)", "methylxanthine") if methyl else
                    _row("tolerates", "bitter, rich and mildly stimulating", None))
    out["alliums"] = (_row("harmful", "onion and garlic poison its blood (as cats, then dogs)", "allium") if "alliums" in toxic else
                      _row("tolerates", "onion and garlic are seasoning", None))
    return out


def fantasy_body(body: dict) -> bool:
    """A body far from the human-like baseline (another diet, gut, taste or a cold blood): its rows read the nearest animal's
    biology, a JUDGEMENT for a fantasy people."""
    return (body.get("diet", "omnivore") != "omnivore" or body.get("gut", "simple") != "simple" or body.get("sweet", True) is not True
            or body.get("capsaicin", True) is not True or body.get("thermo", "endo") == "ecto" or bool(body.get("toxic")))


def summary(body: dict, grown=()) -> dict:
    f = fit(body)
    grown = set(grown or ())
    on_land = {k: sorted(set(crops) & grown) for k, _, crops in FOODS}
    out = {lv: [k for k, _, _ in FOODS if f[k]["level"] == lv] for lv in LEVELS}
    warn = [{"food": k, "level": f[k]["level"], "grown_here": on_land[k]} for k in out["harmful"] + out["poor"] if on_land[k]]
    return {"levels": out, "rows": f, "grown_but_unsuited": warn, "fantasy_body": fantasy_body(body),
            "basis": "food_fit.py (PW-905): from the people's body; 'sourced' rows cite real biology of the nearest real body"
                     + ("; a fantasy body: every row is the nearest animal's biology, a JUDGEMENT" if fantasy_body(body) else "")}


def line(body: dict, grown=()) -> str:
    """One line: what it thrives on beyond what a human-like body does (the baseline's own strengths, cooked meat, grain, sweet fruit,
    go unsaid), then everything it is poorly suited to or harmed by, a food its own fields grow marked."""
    s = summary(body, grown)
    base = fit({})
    parts = []
    for lv in ("thrives", "poor", "harmful"):
        ks = [k for k in s["levels"][lv] if lv != "thrives" or base[k]["level"] != "thrives"]
        if ks:
            parts.append(f"{LEVEL_TEXT[lv]} " + ", ".join(LABEL[k] + (" (grown here)" if lv != "thrives" and any(w["food"] == k for w in s["grown_but_unsuited"]) else "")
                                                         for k in ks))
    parts.append("tolerates the rest" if parts else "the human-like baseline: tolerates or thrives on all")
    return "; ".join(parts) + (" (a fantasy body: the nearest animal's biology, JUDGEMENT)" if s["fantasy_body"] else "")
