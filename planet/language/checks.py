"""The checks of the language pass (PW-986, architecture section 10): the six of the slice, then the living-lect realism
checks (inventory sizes and segment frequencies vs PHOIBLE, 2026-11-04). Each returns {"name", "value", "target", "pass",
"note", "kind"}; `run_all(result)` takes history.generate's result.

`kind` (PW-1737, assessment 11-11): "realism" checks measure something the engine was not told to produce (evidence the
output looks like real languages); "guard" checks confirm a mechanism is wired (its outcome is near-built-in: the proto draw
follows PHOIBLE, rates scale with generation, WOLD scores weight borrowing, elite contact multiplies prestige loans), so a
failure means something broke and a pass proves little; "invariant" checks must always hold. A lane is judged on the
multi-world matrix (tools/language/matrix.py), not on one draw."""
from __future__ import annotations

import functools
import math
import time

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
HORIZON_RANGE = (6.0, 10.0)   # the comparative method's horizon in the literature (shown; the check reads HORIZON_MIN)
# Owner 11-08 (decisions.md): a reading of about 11 kyr or more is close enough, so the check bars only the short side:
# the stable reading (families.logistic_horizon, else the smoothed window read) must be at least HORIZON_MIN. The two-window
# read swings 4.5-19 kyr between seeds of one world and is shown, not judged (PW-1737).
HORIZON_MIN = HORIZON_RANGE[0]
SIBLING_MIN, CROSS_MAX = 0.5, 0.15
LONG_GEN_YR = 100.0  # generation length above which a people counts as long-lived for check 5
TOP20_MIN = 10  # top-20 segment overlap with PHOIBLE
HUMAN_VOICED = frozenset({"human", "halfling", "dwarf", "orc", "goliath", "firbolg", "hill_giant", "cloud_giant", "storm_giant",
                          "frost_giant", "fire_giant", "archaic_human", "giantkin", "elemental_giant", "true_giant", "sky_giant",
                          "elf", "drow", "sea_elf", "gnome", "goblin", "hobgoblin", "bugbear", "greater_goblinoid"})


def _row(name, value, target, ok, note) -> dict:
    return {"name": name, "value": value, "target": target, "pass": bool(ok), "note": note}


GUARD, REALISM, INVARIANT = "guard", "realism", "invariant"


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
    hum = groups.get("human") or {}
    stable = _stable(hum) if hum else h
    stable_long = _stable(lg) if lg else lh
    long_ok = stable_long is not None and stable is not None and (stable_long > stable or bool(lg.get("censored")))
    ok = stable is not None and stable >= HORIZON_MIN and long_ok
    return _row("scholars' horizon (human lects)",
                {"human_judged": stable, "long_lived_judged": stable_long,
                 "human": h, "human_smoothed": hum.get("smoothed_kyr"), "human_single_window": hum.get("single_window_kyr"),
                 "human_logistic": hum.get("logistic_kyr"),
                 "long_lived": lh, "long_lived_censored": lg.get("censored"), "long_lived_smoothed": lg.get("smoothed_kyr"),
                 "all": (groups.get("all") or {}).get("horizon_kyr"), "by_group": groups,
                 "old_pair_measure": old, "old_all": fam.get("horizon_kyr"), "recovery_by_bin": rec, "strict_shares": strict},
                f"human stable reading (logistic, else smoothed) >= {HORIZON_MIN:.0f} kyr (literature {HORIZON_RANGE[0]:.0f}-"
                f"{HORIZON_RANGE[1]:.0f} kyr; owner 11-08: ~11 kyr and more close enough); long-lived peoples (generation >= "
                f"{LONG_LIVED_YR:.0f} yr) longer than the humans' (or still recovering where their splits end)", ok,
                "judged: the logistic fit of recovered on split age (families.logistic_horizon), the smoothed read where the fit "
                "fails; the scholars' UPGMA tree (strict cognates: aligned distance under the threshold and recurring correspondences) over "
                "each group's living lects; the horizon is the start of the first two consecutive 2-kyr windows (stepped by 1 kyr, "
                f"each with >= {_fm().MIN_SPLITS} splits) where fewer than half of the true splits are recovered, read from the "
                "present; smoothed: the first crossing of a split-weighted 3-window moving average; single_window: the former "
                "one-window rule; censored: never under half, the value is a lower bound; old_pair_measure: the former per-pair "
                "edit-distance measure")


def _stable(g: dict) -> float | None:
    """A horizon group's stable reading: the logistic fit, else the smoothed window read, else the two-window read."""
    for k in ("logistic_kyr", "smoothed_kyr", "horizon_kyr"):
        if g.get(k) is not None:
            return float(g[k])
    return None


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


ELITE_PRESTIGE_X = 1.5   # elite loans' prestige-field share over the neighbour loans' (PW-1636)
ELITE_RULE_KYR = 2.0   # lects under elite rule this long ...
ELITE_SPLIT_MIN = 0.5   # ... at least this share of them with a meat or product split (a guard: 0.2 sat far under
#                        the ~0.7 passes give; PW-1737 raised it near the output, so a broken doublet path fails it)


def _last_loan(w):
    last = next((s for s in reversed(w.etym) if not s.process.startswith(("sound_change:", "accent:", "koine:"))), None)
    return last if last is not None and last.process.startswith("borrow:") else None


def contact_profiles(result: dict) -> dict:
    """Loans follow the contact kind (PW-1636, contact.py): over the living lects' loans, the share in the prestige fields
    (law, social and political, religion, war) of the loans from ruling peoples, against the share of the loans from
    neighbours; the elite profile must lift it ELITE_PRESTIGE_X or more."""
    from . import contact as CT
    living = [l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)]
    n: dict = {}
    pr: dict = {}
    for l in living:
        for k, w in l.lexicon.words.items():
            st = _last_loan(w)
            if st is None:
                continue
            kd = CT.kind_of_note(st.note)
            if kd is None:
                continue
            n[kd] = n.get(kd, 0) + 1
            pr[kd] = pr.get(kd, 0) + (CT.field_group(k) in CT.PRESTIGE)
    share = {k: pr.get(k, 0) / n[k] for k in n if n[k]}
    x = share.get("elite", 0.0) / share["flat"] if share.get("flat") else float("nan")
    return _row("loans follow the contact kind", {"loans": n, "prestige_share": {k: round(v, 3) for k, v in share.items()},
                                                  "elite_over_neighbour": round(x, 2)},
                f"elite prestige share >= {ELITE_PRESTIGE_X} x the neighbours'", x == x and x >= ELITE_PRESTIGE_X,
                "prestige = law, social and political, religion, war (contact.field_group); a loan's kind is its "
                "etymology note (contact.channel)")


def _union_kyr(spans: list) -> float:
    """Total kyr covered by [from, to] spans (kyr ago, from >= to), overlaps counted once."""
    tot, hi = 0.0, None
    for lo, up in sorted((min(a, b), max(a, b)) for a, b in spans):
        if hi is None or lo > hi:
            tot += up - lo
            hi = up
        elif up > hi:
            tot += up - hi
            hi = up
    return tot


def doublets(result: dict) -> dict:
    """Doublets (PW-1636, contact.doublet): living lects that were under elite rule for ELITE_RULE_KYR or more (their own
    or inherited, systems.contact_layers) show some meat or product splits; counts of splits by kind and of high-register
    doublets over all living lects."""
    from . import contact as CT
    living = [l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)]
    kinds = {"meat": 0, "product": 0, "register": 0}
    ruled = with_split = 0
    lects_with = 0
    for l in living:
        sp = 0
        for k, w in l.lexicon.words.items():
            st = _last_loan(w)
            if st is None or "doublet" not in st.note:
                continue
            kd = "meat" if k.startswith("meat:") else "product"
            kinds[kd] += 1
            sp += 1
        kinds["register"] += len(((l.lexicon.systems.get("registers") or {}).get("high")) or {})
        lects_with += sp > 0
        layers = l.lexicon.systems.get("contact_layers") or {}
        if _union_kyr([(e[0], e[1]) for v in layers.values() for kd, e in v.items() if kd == "elite"]) >= ELITE_RULE_KYR:
            ruled += 1
            with_split += sp > 0
    share = with_split / ruled if ruled else float("nan")
    return _row("doublets under elite rule", {"splits": kinds, "lects_with_splits": lects_with,
                                              f"ruled_{ELITE_RULE_KYR:g}kyr": ruled, "ruled_with_split": with_split,
                                              "share": round(share, 3) if share == share else None},
                f"share of lects under elite rule >= {ELITE_RULE_KYR:g} kyr with a meat or product split >= "
                f"{ELITE_SPLIT_MIN}", share == share and share >= ELITE_SPLIT_MIN,
                "a split is a word for a meat or a product borrowed beside the native word for the animal or ingredient "
                f"(data/splits.tsv); register = high-register doublets (systems.registers.high); {CT.__name__}")


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
        return _row("areal signal (cross-family, near vs far)", None, f"typology near - far >= {AREAL_MIN}", False,
                    "too few lects: no areal signal can be shown")
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
        return _row("areal signal (cross-family, near vs far)", {"pairs_near": len(near_t), "pairs_far": len(far_t)},
                    f"typology near - far >= {AREAL_MIN}", False, "no near or no far cross-family pairs: no areal signal shown")
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


# Word starts (PW-1686). Real word lists begin with a labial a quarter of the time and with a liquid, h or i rarely;
# sound change on a24559 had piled word starts onto l, h and i (s > h, ʃ > x > h, then h > ∅ before i; n > l and r > l
# dissimilations run as laws), and no check measured it. Each START_GROUPS group's share of a living human-voiced
# lect's words that begin with it; the median lect must sit within the reference's p10-p90 over NorthEuraLex's 107
# languages (data/word_initial.tsv, tools/language/token_priors.py), and no more than START_I_TAIL of the lects may have
# over START_I_MAX of their words begin with i (Zulu's noun-class i- prefixes give 46%; nothing in NorthEuraLex passes
# 16%). Human-voiced only: a lipless people's words cannot start with a labial.
START_GROUPS = ("labial", "liquid", "h", "vowel", "i")
START_I_MAX, START_I_TAIL = 0.20, 0.03


def start_groups(s) -> list[str]:
    """The word-start groups a word's first sound belongs to: labial (any consonant at the lips), liquid (a lateral or
    rhotic: l r ɾ ɹ ʀ ʁ...), h (a glottal fricative), vowel, i (a high front unrounded vowel)."""
    if s.kind == "V":
        return ["vowel"] + (["i"] if s.height >= 5 and s.back <= 1 and not s.round else [])
    if s.kind != "C":
        return []
    out = []
    if s.place == 0:
        out.append("labial")
    if s.manner in (5, 6, 7) or (s.manner == 4 and (s.lateral or s.place in (1, 2, 3))) or \
            (s.manner == 2 and s.place == 6 and s.voice):   # (ʁ, the French and German r)
        out.append("liquid")
    if s.manner == 2 and s.place == 8:
        out.append("h")
    return out


@functools.cache
def start_reference() -> dict:
    """group -> {p5, p10, p25, p50, p75, p90, p95} (data/word_initial.tsv; empty without the file)."""
    from .inventory import DATA
    p = DATA / "word_initial.tsv"
    if not p.exists():
        return {}
    rows = [ln.split("\t") for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    head = rows[0][1:]
    return {r[0]: dict(zip(head, map(float, r[1:]))) for r in rows[1:]}


def lect_starts(forms) -> dict:
    """{group: share of the forms that begin with it} over non-empty forms."""
    n, c = 0, {g: 0 for g in START_GROUPS}
    for f in forms:
        segs = [x for x in f if x.kind in ("C", "V")]
        if not segs:
            continue
        n += 1
        for g in start_groups(segs[0]):
            c[g] += 1
    return {g: c[g] / n for g in START_GROUPS} if n else {}


def word_starts(result: dict) -> dict:
    """Living human-voiced lects' word starts vs NorthEuraLex: each group's median lect share within the reference's
    p10-p90, and few lects with START_I_MAX of their words i-initial (bars above)."""
    ref = start_reference()
    ls = _living_human(result)
    if not ref or len(ls) < 10:
        return _row("word starts vs NorthEuraLex", None, "", False,
                    "no data/word_initial.tsv" if not ref else f"only {len(ls)} living human-voiced lects")
    per = [lect_starts(w.form for w in l.lexicon.words.values()) for l in ls if l.lexicon is not None]
    per = [p for p in per if p]
    val, why = {"lects": len(per)}, []
    for g in START_GROUPS:
        med = float(np.median([p[g] for p in per]))
        lo, hi = ref[g]["p10"], ref[g]["p90"]
        val[g] = {"median": round(med, 3), "ref_p10_p50_p90": [round(lo, 3), round(ref[g]["p50"], 3), round(hi, 3)]}
        if not lo <= med <= hi:
            why.append(g)
    tail = float(np.mean([p["i"] > START_I_MAX for p in per]))
    val["i_over_20pct"] = round(tail, 3)
    if tail > START_I_TAIL:
        why.append("i tail")
    return _row("word starts vs NorthEuraLex", val,
                f"living human-voiced lects: the median lect's share of words starting with a labial, a liquid, h, a vowel "
                f"and i each within NorthEuraLex's p10-p90; at most {START_I_TAIL:.0%} of lects over {START_I_MAX:.0%} "
                f"i-initial", not why, "Eurasian reference (107 languages)" + (f"; off: {', '.join(why)}" if why else ""))


# --- borrowing in the right places (PW-1738, PW-1745: language lane 20) ------------------------------------------------
CORE_ITEMS = ("I", "WE", "ONE", "TWO", "THREE", "MOTHER", "FATHER")
CORE_ITEM_MAX = 0.05   # each: the share of living lects whose word is a loan (WOLD: pronouns, low numerals, parent terms
#                        are borrowed in a few percent of languages at most; a24559 had 10-22% before lane 20)
SW100_XFAM_MAX = 0.02   # Swadesh-100 words borrowed across families in the last 3 kyr, share of all (living lect, word)
XFAM_KYR = 3.0
LATE_KYR = 6.0   # a late concept: its word in the lect was first made (or taken) in the last LATE_KYR kyr
LATE_LOAN_MIN = 0.5   # of late words for new things (animals met, biome kinds, tech items, crops), loans + calques


def _making_steps(w):
    return [s for s in w.etym if not s.process.startswith(("sound_change:", "accent:", "koine:", "wear"))]


def core_loans(result: dict) -> dict:
    """Core words are almost never borrowed (PW-1738): per-item loan shares of the living lects for I, WE, ONE-THREE,
    MOTHER, FATHER; Swadesh-100 words borrowed from another family in the last XFAM_KYR kyr; and ping-pong loans (a
    word borrowed back into a lect it had passed through)."""
    from . import lexicon as LX
    living = [l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)]
    by_id = {l.id: l for l in result["lects"]}
    items = {}
    for k in CORE_ITEMS:
        ws = [l.lexicon.words[k] for l in living if k in l.lexicon.words]
        items[k] = round(float(np.mean([_is_loan(w) for w in ws])), 3) if ws else 0.0
    sw = [c.id for c in LX.concept_index().values() if "SW100" in c.lists]
    n = xf = pp = nw = 0
    for l in living:
        for k in sw:
            w = l.lexicon.words.get(k)
            if w is None:
                continue
            n += 1
            st = _last_loan(w) if _is_loan(w) else None
            if st is not None and float(st.kyr) <= XFAM_KYR:
                d = by_id.get(st.process.split(":", 1)[1])
                if d is not None and d.family_true != l.family_true:
                    xf += 1
        for w in l.lexicon.words.values():
            if w.pos == "NAME":
                continue
            nw += 1
            bs = [s for s in w.etym if s.process.startswith("borrow:")]
            if len(bs) >= 2:   # (A > B > A: a borrowing into a lect that an earlier borrowing took the word from)
                pp += any(s.lect in {x.process.split(":", 1)[1] for x in bs[:j]} for j, s in enumerate(bs))
    share = xf / max(n, 1)
    worst = max(items.values()) if items else 0.0
    return _row("core words rarely borrowed", {"items": items, "sw100_xfam_3kyr": round(share, 4),
                                               "pingpong": round(pp / max(nw, 1), 4)},
                f"each of {', '.join(CORE_ITEMS)} <= {CORE_ITEM_MAX}; Swadesh-100 cross-family loans in the last "
                f"{XFAM_KYR:g} kyr <= {SW100_XFAM_MAX}", worst <= CORE_ITEM_MAX and share <= SW100_XFAM_MAX,
                "loan = the word's latest word-making step is a borrowing; WOLD/Tadmor 2009 for the core's low borrowability")


def _origin(w, gloss: str) -> tuple[str, float, str | None]:
    """(native | loan | calque | coined, kyr, lect) of a word for the concept glossed `gloss`, read from the steps made
    for that concept (a compound's chain starts with its head's steps, a shift's with the source word's): loan or calque
    when one of them borrowed or translated it (kyr: the first such step, the arrival); else native when the first is a
    proto root, coined otherwise (kyr: that first step)."""
    ms = [s for s in _making_steps(w) if s.gloss == gloss]
    if not ms:
        return "coined", float(w.etym[-1].kyr) if w.etym else 99.0, None
    for s in ms:
        if s.process.startswith("calque:"):
            return "calque", float(s.kyr), str(s.lect)
        if s.process.startswith(("borrow:", "substrate:")):
            return "loan", float(s.kyr), str(s.lect)
    return ("native" if ms[0].process == "proto" else "coined"), float(ms[0].kyr), str(ms[0].lect)


def late_things(result: dict) -> dict:
    """Things a people met late arrive as loans (PW-1745): over the living lects' words for animals, biome fauna and
    flora, crops and tech items first made or taken in the last LATE_KYR kyr, the share that are loans or calques; the
    horse's words (native / loan / calque / coined and their median date); and no proto-language with a native word for
    an animal its people never met (history.proto_met)."""
    from . import lexicon as LX
    h = result.get("history")
    living = [l for l in result["lects"] if l.alive and l.deme is not None and not getattr(l, "minority", False)]
    gated = {c.id for c in (h.concepts if h is not None else LX.concepts()) if not c.proto}
    late = {"loan": 0, "calque": 0, "coined": 0, "native": 0}
    horse = {"native": 0, "loan": 0, "calque": 0, "coined": 0}
    hk: list = []
    bad = 0
    met = getattr(h, "proto_met", {}) if h is not None else {}
    for l in living:
        for k, w in l.lexicon.words.items():
            if k not in gated:
                continue
            o, kyr, p = _origin(w, LX.concept_info(k).gloss)
            if o != "native" and kyr <= LATE_KYR:
                late[o] += 1
            if o == "native" and (k.startswith(("animal:", "fauna:", "flora:")) or k.startswith(LX.MEAT_OF)):
                if p in met and k not in met[p]:
                    bad += 1
            if k == "animal:horse":
                horse[o] += 1
                if o != "native":
                    hk.append(kyr)
    nl = sum(late.values()) - late["native"]
    share = (late["loan"] + late["calque"]) / max(nl, 1)
    hv = {**horse, "lects_with_word": round(sum(horse.values()) / max(len(living), 1), 3),
          "median_arrival_kyr": round(float(np.median(hk)), 2) if hk else None}
    return _row("late things arrive as loans", {"late_words": nl, "loan_calque_share": round(share, 3), "by": late,
                                                 "horse": hv, "native_unmet": bad},
                f"loans + calques >= {LATE_LOAN_MIN:.0%} of late words; 0 native words for an animal never met",
                share >= LATE_LOAN_MIN and bad == 0,
                f"late = first made or taken in the last {LATE_KYR:g} kyr; Brown 1999 (lexical acculturation): new things "
                f"are mostly borrowed or calqued, some named by native compounds ('big dog')")


def run_all(result: dict) -> list[dict]:
    out = []
    for fn, arg in ((proto_inventories, result["lects"]), (sister_distant, result), (horizon, result), (shifts, result),
                    (long_generations, result), (complexity, result), (living_sizes, result), (living_segments, result),
                    (living_overuse, result), (typology_consistency, result), (borrowability, result), (areal, result),
                    (possible_segments, result), (second_voice, result), (contact_profiles, result), (doublets, result),
                    (word_starts, result), (core_loans, result), (late_things, result)):
        t = time.perf_counter()
        try:
            row = fn(arg)
        except Exception as e:  # (a check that cannot run says so; it never stops the pass)
            row = _row(fn.__name__, None, "", False, f"check failed: {type(e).__name__}: {e}")
        row["kind"] = KIND.get(fn.__name__, REALISM)
        out.append(row)
        if isinstance(result.get("timing"), dict):
            result["timing"]["check_" + fn.__name__ + "_s"] = round(time.perf_counter() - t, 1)
    return out


# what each check is evidence of (the module docstring; assessment 11-11, "Engineering slice")
KIND = {"proto_inventories": GUARD, "long_generations": GUARD, "complexity": GUARD, "borrowability": GUARD,
        "contact_profiles": GUARD, "doublets": GUARD, "shifts": GUARD, "late_things": GUARD,
        "typology_consistency": INVARIANT, "possible_segments": INVARIANT, "second_voice": INVARIANT,
        "sister_distant": REALISM, "horizon": REALISM, "living_sizes": REALISM, "living_segments": REALISM,
        "living_overuse": REALISM, "areal": REALISM, "word_starts": REALISM}
