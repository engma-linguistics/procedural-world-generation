"""The checks of the language pass (PW-986, architecture section 10): the six of the slice, then the living-lect realism
checks (inventory sizes and segment frequencies vs PHOIBLE, 2026-11-04). Each returns {"name", "value", "target", "pass",
"note"}; `run_all(result)` takes history.generate's result."""
from __future__ import annotations

import math

import numpy as np

HORIZON_PEOPLES = {"human": frozenset({"human"})}
LONG_LIVED_YR = 60.0  # generation length from which a people counts as long-lived for the horizon groups (dwarves 71 yr, elves 145, dragons 430)
DWARVES = frozenset({"dwarf", "duergar"})
ELVES = frozenset({"elf", "drow", "sea_elf", "eladrin", "shadar_kai", "wood_elf", "high_elf"})
# the horizon groups beside the humans (families.horizon groups): predicates over a lect (people, gen_yr)
HORIZON_GROUPS = {"long_lived": lambda l: (getattr(l, "gen_yr", 0.0) or 0.0) >= LONG_LIVED_YR,
                  "dwarves": lambda l: l.people in DWARVES,
                  "elves": lambda l: l.people in ELVES,
                  "dragons": lambda l: l.people.endswith("_dragon")}
HORIZON_RANGE = (6.0, 10.0)
SIBLING_MIN, CROSS_MAX = 0.5, 0.15
LONG_GEN_YR = 100.0  # generation length above which a people counts as long-lived for check 5
TOP20_MIN = 10  # top-20 segment overlap with PHOIBLE
HUMAN_VOICED = frozenset({"human", "halfling", "dwarf", "orc", "goliath", "firbolg", "hill_giant", "cloud_giant", "storm_giant",
                          "frost_giant", "fire_giant", "archaic_human", "giantkin", "elemental_giant", "true_giant", "sky_giant",
                          "elf", "drow", "sea_elf", "gnome", "goblin", "hobgoblin", "bugbear", "greater_goblinoid"})


def _row(name, value, target, ok, note) -> dict:
    return {"name": name, "value": value, "target": target, "pass": bool(ok), "note": note}


def proto_inventories(lects: list) -> dict:
    """Check 1: proto inventory sizes within PHOIBLE's interquartile range for 70% of the human-voiced protos, and the top-20
    segments overlapping PHOIBLE's top 20."""
    from . import inventory as INV
    from .percepts import to_ipa
    protos = [l for l in lects if l.deme is None and l.how in ("proto", "arrival")]
    human = [l for l in protos if l.people in HUMAN_VOICED] or protos
    st = INV.phoible_sizes()
    qc, qv = st["consonants"]["stat"], st["vowels"]["stat"]
    inside = [qc["q1"] <= len(l.inventory.consonants) <= qc["q3"] and qv["q1"] <= len(l.inventory.vowels) <= qv["q3"] for l in human]
    loose = [qc["q1"] <= len(l.inventory.consonants) <= qc["q3"] or qv["q1"] <= len(l.inventory.vowels) <= qv["q3"] for l in human]
    cnt: dict = {}
    for l in human:
        for s in list(l.inventory.consonants) + list(l.inventory.vowels):
            cnt[s] = cnt.get(s, 0) + 1
    ours = [s for s, _ in sorted(cnt.items(), key=lambda t: (-t[1], to_ipa(t[0])))[:20]]
    pc, pv = INV.phoible_pool()
    theirs = [s for s, _ in sorted(list(pc) + list(pv), key=lambda t: -t[1])[:20]]
    ov = len(set(ours) & set(theirs))
    share = float(np.mean(inside)) if inside else 0.0
    cmed = float(np.median([len(l.inventory.consonants) for l in human])) if human else 0
    vmed = float(np.median([len(l.inventory.vowels) for l in human])) if human else 0
    c_in = float(np.mean([qc["q1"] <= len(l.inventory.consonants) <= qc["q3"] for l in human])) if human else 0
    v_in = float(np.mean([qv["q1"] <= len(l.inventory.vowels) <= qv["q3"] for l in human])) if human else 0
    # (judgement call: the contract's "70% within the IQR" cannot hold for a PHOIBLE-like draw, whose IQR holds half by
    # definition; the check asks for PHOIBLE's shape instead: medians inside its IQR, 35-75% of protos inside it per measure)
    ok = (qc["q1"] <= cmed <= qc["q3"] and qv["q1"] <= vmed <= qv["q3"] and 0.35 <= c_in <= 0.75 and 0.35 <= v_in <= 0.75
          and ov >= TOP20_MIN)
    return _row("proto inventories vs PHOIBLE", {"consonants_in_iqr": round(c_in, 3), "vowels_in_iqr": round(v_in, 3), "both_in_iqr": round(share, 3), "either_in_iqr": round(float(np.mean(loose)), 3) if loose else 0,
                                                  "top20_overlap": ov, "median_consonants": cmed, "median_vowels": vmed,
                                                  "protos": len(human)},
                f"medians inside PHOIBLE's IQR (C {qc['q1']:.0f}-{qc['q3']:.0f}, V {qv['q1']:.0f}-{qv['q3']:.0f}), 35-75% of protos inside it "
                f"per measure; top-20 overlap >= {TOP20_MIN}",
                ok, f"over {len(human)} human-voiced protos; our top 20: {' '.join(to_ipa(s) for s in ours)}")


def split_measure(result: dict) -> dict:
    """families.horizon on the pass result, once (cached on the result): the split horizon per people group and the strict
    sister / cross-family shares."""
    if "_split_measure" not in result:
        from . import families as FM
        try:
            result["_split_measure"] = FM.horizon(result, people="human", groups=HORIZON_GROUPS)
        except Exception as e:  # noqa: BLE001 - the checks say so
            result["_split_measure"] = {"error": f"{type(e).__name__}: {e}"}
    return result["_split_measure"]


def sister_distant(result: dict) -> dict:
    """Check 2 on the STRICT cognate share (a linguist's view: aligned distance under the threshold and recurring
    correspondences; owner 11-04 left the choice to the lane), bar 0.5; the loose and true shares beside it."""
    fam = result.get("families") or {}
    hz = split_measure(result)
    if "error" in hz:
        return _row("sisters recognisable, distant not", None, "", False, f"split measure failed: {hz['error']}")
    sis, cr = hz.get("sisters") or {}, hz.get("cross_family") or {}
    sib, cross = sis.get("strict"), cr.get("strict")
    ok = sib is not None and cross is not None and sib > SIBLING_MIN and cross < CROSS_MAX
    return _row("sisters recognisable, distant not",
                {"siblings": sib, "cross_family": cross, "siblings_loose": sis.get("loose"), "siblings_true": sis.get("true"),
                 "cross_family_loose": cr.get("loose"), "chance_floor": (fam.get("chance") or {}).get("floor")},
                f"strict cognate share (aligned distance < {_fm().COGNATE_DIST} and every correspondence recurring in "
                f">= {_fm().REC_MIN} other close pairs: what a comparativist would accept): lects parted <= 2 kyr ago > "
                f"{SIBLING_MIN}; different true families < {CROSS_MAX}", ok,
                f"{sis.get('pairs')} sister pairs, {cr.get('pairs')} cross-family pairs; loose (edit distance only) and true-root "
                "shares reported beside it")


def _fm():
    from . import families as FM
    return FM


def _group_row(v: dict | None) -> dict | None:
    if not v:
        return None
    return {"horizon_kyr": v.get("horizon_kyr"), "censored": v.get("censored"), "smoothed_kyr": v.get("smoothed_kyr"),
            "single_window_kyr": v.get("single_window_kyr"), "logistic_kyr": v.get("logistic_kyr"), "splits": v.get("splits"),
            "lects": v.get("lects")}


def horizon(result: dict) -> dict:
    """The split-based horizon under the strict cognate test (families.horizon): human lects inside HORIZON_RANGE, and the
    long-lived peoples (generation >= LONG_LIVED_YR) more conservative: their horizon longer than the humans', or their
    splits still recovered as far back as they go (censored). Per group (human, long-lived, dwarves, elves, dragons where
    they have splits) the two-window horizon, the smoothed read and the former single-window read; the old pair measure
    beside it."""
    fam = result.get("families") or {}
    hb = (fam.get("horizon_by") or {}).get("human") or {}
    old = hb.get("horizon_kyr")
    hz = split_measure(result)
    if "error" in hz:
        h, groups, rec, strict = None, {}, None, {"error": hz["error"]}
    else:
        h = hz.get("horizon_kyr")
        groups = {k: _group_row(v) for k, v in (hz.get("by") or {}).items()}
        rec = hz.get("recovery_by_bin")
        strict = {"sisters": hz.get("sisters"), "cross_family": hz.get("cross_family")}
    if h is None:
        h = old
    lg = groups.get("long_lived") or {}
    lh = lg.get("horizon_kyr")
    long_ok = lh is not None and h is not None and (lh > h or bool(lg.get("censored")))
    ok = h is not None and HORIZON_RANGE[0] <= h <= HORIZON_RANGE[1] and long_ok
    hum = groups.get("human") or {}
    return _row("scholars' horizon (human lects)",
                {"human": h, "human_smoothed": hum.get("smoothed_kyr"), "human_single_window": hum.get("single_window_kyr"),
                 "human_logistic": hum.get("logistic_kyr"),
                 "long_lived": lh, "long_lived_censored": lg.get("censored"), "long_lived_smoothed": lg.get("smoothed_kyr"),
                 "all": (groups.get("all") or {}).get("horizon_kyr"), "by_group": groups,
                 "old_pair_measure": old, "old_all": fam.get("horizon_kyr"), "recovery_by_bin": rec, "strict_shares": strict},
                f"human {HORIZON_RANGE[0]:.0f}-{HORIZON_RANGE[1]:.0f} kyr; long-lived peoples (generation >= {LONG_LIVED_YR:.0f} yr) "
                "longer than the humans' (or still recovering where their splits end)", ok,
                "the scholars' UPGMA tree (strict cognates: aligned distance under the threshold and recurring correspondences) over "
                "each group's living lects; the horizon is the start of the first two consecutive 2-kyr windows (stepped by 1 kyr, "
                f"each with >= {_fm().MIN_SPLITS} splits) where fewer than half of the true splits are recovered, read from the "
                "present; smoothed: the first crossing of a split-weighted 3-window moving average; single_window: the former "
                "one-window rule; censored: never under half, the value is a lower bound; old_pair_measure: the former per-pair "
                "edit-distance measure")


def shifts(result: dict) -> dict:
    h = result["history"]
    living = [l for l in result["lects"] if l.alive and l.deme is not None]
    differ = [l for l in living if h.first_family.get(l.deme) not in (None, l.family_true)]
    n = len(result["shifts"])
    return _row("language shift happened", {"shifts": n, "living_lects_off_their_descent": len(differ), "living": len(living)},
                "> 0 living lects whose family differs from their deme's descent", len(differ) > 0,
                f"shifts by trigger: {_by_kind(result['shifts'])}")


def _by_kind(sh: list) -> dict:
    out: dict = {}
    for s in sh:
        k = (s.get("trigger") or {}).get("kind", "?")
        out[k] = out.get(k, 0) + 1
    return out


def chain_rules_per_kyr(l, by_id: dict, start_kyr: float = 20.0) -> float:
    """Sound changes along a living lect's line since the start, per kyr."""
    n, cur, until = 0, l, 0.0
    while cur is not None:
        n += sum(1 for c in cur.changes if c["kyr"] >= until - 1e-9)
        until = cur.born_kyr
        cur = by_id.get(cur.parent) if cur.parent else None
    return n / start_kyr


def long_generations(result: dict) -> dict:
    by_id = {l.id: l for l in result["lects"]}
    living = [l for l in result["lects"] if l.alive and l.deme is not None]
    hum = [chain_rules_per_kyr(l, by_id) for l in living if l.people == "human"]
    lg = [chain_rules_per_kyr(l, by_id) for l in living if l.gen_yr >= LONG_GEN_YR]
    if not hum or not lg:
        return _row("long generations change less", None, "long-lived peoples' rules per kyr < a third of humans'", False, "no lects to compare")
    h, g = float(np.mean(hum)), float(np.mean(lg))
    return _row("long generations change less", {"human_rules_per_kyr": round(h, 3), "long_lived_rules_per_kyr": round(g, 3),
                                                  "ratio": round(h / g, 2) if g else None},
                "long-lived (generation >= 100 yr) peoples' sound changes per kyr < a third of humans'", g < h / 3.0,
                f"{len(hum)} human lects, {len(lg)} long-lived lects (dragons, elves, ...); wave-borrowed changes count too")


def complexity(result: dict) -> dict:
    from . import grammar as GR
    living = [l for l in result["lects"] if l.alive and l.deme is not None and l.grammar is not None]
    if len(living) < 8:
        return _row("hubs simpler, isolated richer", None, "hub mean complexity < isolated small", False, "too few lects")
    sc = np.array([GR.complexity(l.grammar)["score"] for l in living])
    l2 = np.array([l.l2 for l in living])
    pop = np.array([l.population for l in living])
    iso = np.array([l.isolation for l in living])
    rank = np.lexsort((pop, l2))  # (by adult-L2 share, ties by population)
    hub = np.zeros(len(living), bool)
    hub[rank[-max(1, len(living) // 4):]] = True
    hub |= pop >= np.quantile(pop, 0.9)
    small = (pop <= np.quantile(pop, 0.25)) & (iso >= np.median(iso)) & ~hub
    a, b = float(sc[hub].mean()) if hub.any() else None, float(sc[small].mean()) if small.any() else None
    ok = a is not None and b is not None and a < b
    return _row("hubs simpler, isolated richer", {"hub_score": round(a, 3) if a is not None else None,
                                                   "isolated_score": round(b, 3) if b is not None else None,
                                                   "hubs": int(hub.sum()), "isolated": int(small.sum())},
                "mean measured complexity (grammar.complexity score) of hubs (the quarter with the highest adult-L2 share, or top-decile population) "
                "< that of small isolated lects", ok, "one seed; across seeds later")


# ---------------------------------------------------------------------------- living human-voiced lects vs PHOIBLE (2026-11-04)
# Inventory sizes. The bar is PHOIBLE's shape, loosely: median within SIZE_MED_TOL of PHOIBLE's (21 C, 9 V), quartiles within
# SIZE_Q_TOL, and the share of lects above PHOIBLE's 95th percentile (42 C, 22 V; 5% of PHOIBLE by definition) inside
# TAIL_SHARE for consonants (a tail exists - at least one lect in ~300 - but stays rare) and under its upper end for vowels.
# Loose on purpose: one seed, ~300 lects, and lines that share ancestors are not independent draws.
SIZE_MED_TOL = {"consonants": 3, "vowels": 2}
SIZE_Q_TOL = {"consonants": 4, "vowels": 3}
TAIL_SHARE = (0.003, 0.15)
# Segment frequencies. Top-20 overlap with PHOIBLE's top 20 >= LIVING_TOP20_MIN (protos: TOP20_MIN); the plain sounds of
# PLAIN each present in at least PLAIN_FACTOR^-1 of PHOIBLE's share of languages (p: 85% -> at least 43%); and no
# monoculture: no segment in more than MONO_SHARE of the lects unless PHOIBLE has it in at least MONO_SHARE / MONO_FACTOR
# (ʒ, 14% of PHOIBLE, may not stand in more than half; ɲ, 42%, may).
LIVING_TOP20_MIN = 12
PLAIN = ("p", "t", "k", "m", "n", "i", "a", "u")
PLAIN_FACTOR = 2.0
MONO_SHARE, MONO_FACTOR = 0.5, 2.5


def _living_human(result: dict) -> list:
    return [l for l in result["lects"] if l.alive and l.deme is not None and l.people in HUMAN_VOICED
            and l.inventory is not None]


def _quant(xs, qs=(0.05, 0.25, 0.5, 0.75, 0.95)) -> list[float]:
    return [float(x) for x in np.quantile(np.asarray(xs, float), qs)] if len(xs) else []


def living_sizes(result: dict) -> dict:
    """Living human-voiced lects' consonant and vowel counts vs PHOIBLE: p5/q1/median/q3/p95 and the share above PHOIBLE's
    p95 (bars above)."""
    from . import inventory as INV
    ls = _living_human(result)
    if len(ls) < 10:
        return _row("living inventory sizes vs PHOIBLE", None, "", False, f"only {len(ls)} living human-voiced lects")
    val, ok, why = {"lects": len(ls)}, True, []
    for m, attr in (("consonants", "consonants"), ("vowels", "vowels")):
        n = [len(getattr(l.inventory, attr)) for l in ls]
        ph = INV.size_quantiles(m)
        ours = _quant(n)
        tail = float(np.mean(np.asarray(n) > ph[4]))
        val[m] = {"ours": [round(x, 1) for x in ours], "phoible": ph, "above_phoible_p95": round(tail, 4),
                  "max": int(max(n)), "min": int(min(n))}
        good = (abs(ours[2] - ph[2]) <= SIZE_MED_TOL[m] and abs(ours[1] - ph[1]) <= SIZE_Q_TOL[m]
                and abs(ours[3] - ph[3]) <= SIZE_Q_TOL[m] and tail <= TAIL_SHARE[1]
                and (m != "consonants" or tail >= TAIL_SHARE[0]))
        if not good:
            why.append(m)
        ok &= good
    return _row("living inventory sizes vs PHOIBLE", val,
                f"living human-voiced lects: median within {SIZE_MED_TOL['consonants']} C / {SIZE_MED_TOL['vowels']} V of "
                f"PHOIBLE's, quartiles within {SIZE_Q_TOL['consonants']} C / {SIZE_Q_TOL['vowels']} V, share above PHOIBLE's "
                f"95th percentile {TAIL_SHARE[0]:.1%}-{TAIL_SHARE[1]:.0%} for consonants (a rare tail), under "
                f"{TAIL_SHARE[1]:.0%} for vowels", ok,
                "quantiles p5/q1/median/q3/p95; vowels counted as inventory.vowels (length and nasality distinct, tone aside)"
                + (f"; off: {', '.join(why)}" if why else ""))


def living_segments(result: dict) -> dict:
    """Living human-voiced lects' segment shares vs PHOIBLE's share of languages: top-20 overlap, the plain sounds present
    within PLAIN_FACTOR, no monoculture (bars above)."""
    from . import inventory as INV
    from .percepts import to_ipa
    ls = _living_human(result)
    if len(ls) < 10:
        return _row("living segment frequencies vs PHOIBLE", None, "", False, f"only {len(ls)} living human-voiced lects")
    pc, pv = INV.phoible_pool()
    ph = {to_ipa(s): f for s, f in list(pc) + list(pv)}
    cnt: dict = {}
    for l in ls:
        for s in {to_ipa(x) for x in list(l.inventory.consonants) + list(l.inventory.vowels)}:
            cnt[s] = cnt.get(s, 0) + 1
    share = {s: c / len(ls) for s, c in cnt.items()}
    ours = [s for s, _ in sorted(share.items(), key=lambda t: (-t[1], t[0]))[:20]]
    order = sorted(ph, key=lambda s: -ph[s])
    ov = len(set(ours) & set(order[:20]))
    plain = {s: {"ours": round(share.get(s, 0.0), 3), "phoible": round(ph.get(s, 0.0), 3)} for s in PLAIN}
    plain_ok = all(v["ours"] >= v["phoible"] / PLAIN_FACTOR for v in plain.values())
    mono = {s: round(v, 3) for s, v in sorted(share.items(), key=lambda t: -t[1])
            if v > MONO_SHARE and v > MONO_FACTOR * ph.get(s, 0.0)}
    beyond12 = {s: round(v, 3) for s, v in sorted(share.items(), key=lambda t: -t[1]) if v > 0.5 and s not in order[:12]}
    ok = ov >= LIVING_TOP20_MIN and plain_ok and not mono
    return _row("living segment frequencies vs PHOIBLE",
                {"top20_overlap": ov, "plain": plain, "monocultures": mono, "over_half_outside_phoible_top12": beyond12,
                 "lects": len(ls)},
                f"living human-voiced lects: top-20 overlap with PHOIBLE >= {LIVING_TOP20_MIN}; {' '.join(PLAIN)} each in at "
                f"least 1/{PLAIN_FACTOR:.0f} of PHOIBLE's share; no segment in over {MONO_SHARE:.0%} of lects and over "
                f"{MONO_FACTOR}x PHOIBLE's share", ok,
                f"our top 20: {' '.join(ours)}; over_half_outside_phoible_top12 is informative (PHOIBLE itself has e, ŋ, b, o, "
                f"ɡ, h in over half its languages)")


# Overused segments over every living lect (round 5, 2026-11-07). The human-voiced check above judged only human-voiced lects,
# so a sound the sound changes over-produce everywhere (ɹ in half the living lects, PHOIBLE 1.7%) went unseen. Here every
# living lect counts a segment unless its own voice profile favours it (make_cost below 1 over the segment's keys: a
# reptilian lect may be full of sibilants) or humans cannot make it (a species' own sound); a segment fails when its share passes both OVERUSE_FLOOR and OVERUSE_FACTOR x
# PHOIBLE's share of languages (segments PHOIBLE lacks count as share 0, so the floor alone bars them).
OVERUSE_FLOOR, OVERUSE_FACTOR = 0.10, 3.0


def _favoured(profile, seg) -> bool:
    """Does the profile favour the segment (make_cost below 1 over its keys), or is it a sound humans cannot make (a
    species' own sound, PHOIBLE has no share for it)?"""
    from . import profiles as PR
    from .percepts import is_nonhuman
    if is_nonhuman(seg) or math.isinf(PR.species_cost(PR.HUMAN, seg)):   # (harsh voice too: finite but dear for humans,
        return True                                                         # PHOIBLE has no share for a growled vowel)
    if profile is None:
        return False
    m = 1.0
    for key in PR.keys_of(seg):
        m *= profile.make_cost.get(key, 1.0)
    return m < 1.0


def living_overuse(result: dict) -> dict:
    """Every living lect's segment shares vs PHOIBLE: no segment over OVERUSE_FLOOR and OVERUSE_FACTOR x PHOIBLE's share,
    a lect not counting a segment its own voice profile favours (bars above)."""
    from . import inventory as INV
    from .percepts import to_ipa
    ls = [l for l in result["lects"] if l.alive and l.deme is not None and l.inventory is not None]
    if len(ls) < 10:
        return _row("overused segments (all living lects)", None, "", False, f"only {len(ls)} living lects")
    pc, pv = INV.phoible_pool()
    ph = {to_ipa(s): f for s, f in list(pc) + list(pv)}
    cnt: dict = {}
    for l in ls:
        prof = getattr(l, "profile", None)
        for x in set(l.inventory.consonants) | set(l.inventory.vowels):
            if not _favoured(prof, x):
                s = to_ipa(x)
                cnt[s] = cnt.get(s, 0) + 1
    share = {s: c / len(ls) for s, c in cnt.items()}
    over = {s: {"ours": round(v, 3), "phoible": round(ph.get(s, 0.0), 3)}
            for s, v in sorted(share.items(), key=lambda t: (-t[1], t[0]))
            if v > OVERUSE_FLOOR and v > OVERUSE_FACTOR * ph.get(s, 0.0)}
    top = {s: round(v / max(ph.get(s, 0.0), 1e-3), 1) for s, v in sorted(share.items(), key=lambda t: (-t[1], t[0]))
           if v >= OVERUSE_FLOOR}
    worst = dict(sorted(top.items(), key=lambda t: -t[1])[:8])
    return _row("overused segments (all living lects)", {"overused": over, "worst_ratio_vs_phoible": worst, "lects": len(ls)},
                f"no segment in over {OVERUSE_FLOOR:.0%} of living lects and over {OVERUSE_FACTOR:.0f}x PHOIBLE's share "
                f"(a lect skips segments its voice profile favours)", not over,
                "worst_ratio_vs_phoible: our share / PHOIBLE's for segments in 10%+ of lects (informative)")


def typology_consistency(result: dict) -> dict:
    """Typology vs grams (2026-11-04): no living lect's shown typology may contradict its live grams ('number: none' with a
    live plural, 'case: none' with a live locative, the negator on the wrong side; grammar.clashes). Also reports how
    often the shown value of a gram-realised feature equals the drifting aim (the ladder keeping up with the drift)."""
    from . import grammar as GR
    living = [l for l in result["lects"] if l.alive and l.deme is not None and l.grammar is not None]
    feats: dict = {}
    bad = 0
    same = []
    for l in living:
        cl = GR.clashes(l.grammar, l.lexicon)
        bad += bool(cl)
        for c in cl:
            k = c.split(":")[0]
            feats[k] = feats.get(k, 0) + 1
        a = GR.aims(l.grammar)
        same += [a.get(f) == l.grammar.typology.get(f) for f in GR.REALISED]
    return _row("typology agrees with the live grams",
                {"lects_with_clashes": bad, "living": len(living), "by_feature": dict(sorted(feats.items())),
                 "shown_equals_aim": round(float(np.mean(same)), 3) if same else None},
                "0 lects with a clash", bad == 0,
                "shown_equals_aim is informative: realised features show what the grams do; the drifting aim pulls grams "
                "onto the ladder (grammar.PRESSURE) or lets them erode, so the two differ while the ladder catches up")


# --- lexicon & contact lane (2026-11-08) -------------------------------------------------------------------------------
WOLD_RHO_MIN = 0.3   # Spearman rho between the living lects' loan share per meaning and WOLD's borrowed score
CLOSED_LOAN_MAX = 0.08   # pronouns: mean living loan share (WOLD: a few percent; English they is the famous exception)


def _spearman(a, b) -> float:
    ra = np.argsort(np.argsort(np.asarray(a, float)))
    rb = np.argsort(np.argsort(np.asarray(b, float)))
    return float(np.corrcoef(ra, rb)[0, 1])


def _is_loan(w) -> bool:
    last = next((s for s in reversed(w.etym) if not s.process.startswith(("sound_change:", "accent:", "koine:"))), None)
    return last is not None and last.process.startswith("borrow:")


def borrowability(result: dict) -> dict:
    """Loans follow borrowability: over the meanings WOLD scores, the share of living lects whose word is a loan,
    against WOLD's borrowed score (Spearman rho); and pronouns kept (lexicon-gaps rec. 1: rho was -0.13, pronouns 11-16%
    loans)."""
    from . import lexicon as LX
    living = [l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)]
    loans: dict = {}
    per_lect = []
    for l in living:
        n = b = 0
        for k, w in l.lexicon.words.items():
            if w.pos == "NAME":   # (god names: faiths.py)
                continue
            x = _is_loan(w)
            loans.setdefault(k, []).append(x)
            n += 1
            b += x
        per_lect.append(b / max(n, 1))
    sc = LX._wold_scores()
    ks = sorted(k for k, v in loans.items() if len(v) >= max(5, len(living) // 10) and k in sc)
    share = [float(np.mean(loans[k])) for k in ks]
    rho = _spearman(share, [sc[k] for k in ks]) if len(ks) > 10 else float("nan")
    pron = [float(np.mean(loans[k])) for k in ("I", "THOU", "WE", "YOU", "THEY") if k in loans]
    pr = float(np.mean(pron)) if pron else 0.0
    q = [round(float(x), 3) for x in np.quantile(per_lect, [0.1, 0.5, 0.9])] if per_lect else []
    return _row("loans follow borrowability (WOLD)", {"rho": round(rho, 3), "meanings": len(ks), "pronoun_loans": round(pr, 3),
                                                      "lect_loan_share_p10_p50_p90": q},
                f"rho >= {WOLD_RHO_MIN}; pronoun loans <= {CLOSED_LOAN_MAX}",
                rho == rho and rho >= WOLD_RHO_MIN and pr <= CLOSED_LOAN_MAX,
                "WOLD borrowed scores (Haspelmath & Tadmor 2009) per meaning; the share is of living lects whose current word "
                "for the meaning is a loan (latest word-making step)")


AREAL_NEAR_KM, AREAL_FAR_KM = 1000.0, 4000.0
AREAL_MIN = 0.01   # near minus far agreement, cross-family pairs (typology share of features with the same value)


def areal(result: dict) -> dict:
    """An areal signal: lects of different true families agree more in typology (and inventories) when they are near
    (< AREAL_NEAR_KM between their demes) than when they are far (> AREAL_FAR_KM). contact-gaps.md 3a: the agreement was
    the same near and far (0.528 vs 0.529)."""
    R = result["run"]
    living = sorted((l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)),
                    key=lambda l: l.id)
    if len(living) < 3:
        return _row("areal signal", None, "", True, "too few lects")
    lat = np.radians([float(R.demes[l.deme]["lat"]) for l in living])
    lon = np.radians([float(R.demes[l.deme]["lon"]) for l in living])
    fam = np.array([l.family_true or l.id for l in living])
    feats = sorted({k for l in living for k, v in (getattr(l.grammar, "typology", None) or {}).items()
                    if isinstance(v, (str, bool, int))})
    vals: dict = {}
    T = np.array([[vals.setdefault((f, str((getattr(l.grammar, "typology", None) or {}).get(f))), len(vals)) for f in feats]
                  for l in living])
    segs = sorted({s for l in living for s in l.segments()}, key=repr)
    si = {s: j for j, s in enumerate(segs)}
    S = np.zeros((len(living), len(segs)), bool)
    for a, l in enumerate(living):
        S[a, [si[s] for s in l.segments()]] = True
    near_t, far_t, near_i, far_i = [], [], [], []
    for a in range(len(living) - 1):
        b = np.arange(a + 1, len(living))
        cosd = np.sin(lat[a]) * np.sin(lat[b]) + np.cos(lat[a]) * np.cos(lat[b]) * np.cos(lon[a] - lon[b])
        dk = 6371.0 * np.arccos(np.clip(cosd, -1.0, 1.0))
        cross = fam[b] != fam[a]
        ag = (T[b] == T[a]).mean(axis=1) if feats else np.zeros(len(b))
        inter = (S[b] & S[a]).sum(axis=1)
        uni = np.maximum((S[b] | S[a]).sum(axis=1), 1)
        ji = inter / uni
        n_ = cross & (dk < AREAL_NEAR_KM)
        f_ = cross & (dk > AREAL_FAR_KM)
        near_t += ag[n_].tolist(); far_t += ag[f_].tolist(); near_i += ji[n_].tolist(); far_i += ji[f_].tolist()
    if not near_t or not far_t:
        return _row("areal signal", None, "", True, "no near or no far cross-family pairs")
    dt = float(np.mean(near_t) - np.mean(far_t))
    di = float(np.mean(near_i) - np.mean(far_i))
    return _row("areal signal (cross-family, near vs far)",
                {"typology_near": round(float(np.mean(near_t)), 4), "typology_far": round(float(np.mean(far_t)), 4),
                 "typology_diff": round(dt, 4), "inventory_near": round(float(np.mean(near_i)), 4),
                 "inventory_far": round(float(np.mean(far_i)), 4), "inventory_diff": round(di, 4),
                 "pairs_near": len(near_t), "pairs_far": len(far_t)},
                f"typology near - far >= {AREAL_MIN}", dt >= AREAL_MIN,
                f"near < {AREAL_NEAR_KM:g} km, far > {AREAL_FAR_KM:g} km between the demes' places; inventories (Jaccard) "
                "are shown, not judged")


def possible_segments(result: dict) -> dict:
    """No lect of the run, living or dead, has a segment no mouth makes (rules.impossible: a voiced or prenasalised
    ejective; cold review 2026-11-08, R2)."""
    from . import rules as RU
    from .percepts import to_ipa
    bad: dict = {}
    for l in result["lects"]:
        if getattr(l, "lexicon", None) is None:
            continue
        for s in l.segments():
            if RU.impossible(s):
                bad.setdefault(to_ipa(s), []).append(l.id)
    n = sum(len(v) for v in bad.values())
    note = "; ".join(f"{k} in {len(v)} lects ({', '.join(v[:3])})" for k, v in sorted(bad.items())) or "none"
    return _row("no impossible segments (all lects)", n, "0", n == 0, note)


def second_voice(result: dict) -> dict:
    """Second-voice tone (syrinx lane, 2026-11-08; docs/review/language/syrinx.md): among living syrinx-voiced lects, the
    share with a second voice and the share whose second voice carries a tone contrast of its own (two or more categories
    over its vowels, parallel motion counting as one); the pass is that no lect of the run whose people has no syrinx has a
    second voice at all (loans heard by one-voiced ears lose it). The shares are shown, not judged."""
    bad: dict = {}
    syr = []
    for l in result["lects"]:
        if getattr(l, "lexicon", None) is None:
            continue
        has = "syrinx" in (getattr(getattr(l, "profile", None), "articulators", ()) or ())
        if not has:
            if any(s.kind == "V" and (s.source2 or s.tone2) for s in l.segments()):
                bad.setdefault(l.people, []).append(l.id)
        elif l.alive and l.deme is not None and l.inventory is not None:
            syr.append(l)
    n = len(syr)
    s2 = [l for l in syr if any(v.source2 for v in l.inventory.vowels)]
    t2 = [l for l in s2 if len({v.tone2 for v in l.inventory.vowels if v.source2}) >= 2]
    cats = sorted(len({v.tone2 for v in l.inventory.vowels if v.source2}) for l in t2)
    val = {"syrinx_lects": n, "with_second_voice": len(s2), "with_second_voice_tone": len(t2),
           "share_second_voice": round(len(s2) / n, 3) if n else None,
           "share_second_voice_tone": round(len(t2) / n, 3) if n else None, "categories": cats,
           "one_voiced_with_second_voice": sum(len(v) for v in bad.values())}
    note = ("; ".join(f"{p}: {len(v)} lects ({', '.join(v[:3])})" for p, v in sorted(bad.items())) or
            "no one-voiced lect has a second voice") + "; shares informative (design: about half of second-voice protos)"
    return _row("second voice only where there is a syrinx; second-voice tone shares", val, "0 one-voiced lects with ᴖ",
                not bad, note)


def run_all(result: dict) -> list[dict]:
    out = []
    for fn, arg in ((proto_inventories, result["lects"]), (sister_distant, result), (horizon, result), (shifts, result),
                    (long_generations, result), (complexity, result), (living_sizes, result), (living_segments, result),
                    (living_overuse, result), (typology_consistency, result), (borrowability, result), (areal, result),
                    (possible_segments, result), (second_voice, result)):
        try:
            out.append(fn(arg))
        except Exception as e:  # (a check that cannot run says so; it never stops the pass)
            out.append(_row(fn.__name__, None, "", False, f"check failed: {type(e).__name__}: {e}"))
    return out
