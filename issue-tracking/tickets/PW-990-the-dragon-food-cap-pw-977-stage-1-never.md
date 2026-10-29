---
id: PW-990
title: "The dragon food cap (PW-977 stage 1) never binds at the default densities: what limits dragons is the pressed 1 per 5,000 km2 and the natural prey density, not food"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-43
blocked_by: []
relates: [PW-977, PW-957, PW-973]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/probe.py, docs/review/megafauna/age-of-dragons.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
**In plain words.** Stage 1 asks: does each place grow enough food for the dragons we put there? At default settings the answer is always yes, by about 10x, so the food check never changes anything.

Today the dragon count is set by two other rules:
1. A natural density from body size: big predators are rare, by a formula fitted to real carnivores.
2. Where peoples are strong, a fixed 1 dragon per 5,000 km2.

Both give far fewer dragons than the food could feed.

The question for the owner: should dragon numbers come *from* food, or from the body-size rule with food only as a ceiling?
- **A.** Keep the body-size rule and the 1 per 5,000; food stays a ceiling. It only bites on barren worlds or if dragons are set denser.
- **B.** Let food decide: dragons get what is left after peoples and other predators eat, and the body-size rule becomes a sanity check.
  - Catch: if dragons got all the leftovers, rich land would hold ~10x today's dragons. B only makes sense once the peoples' and other predators' share (stage 2) is in.
  - Real predator guilds take a small share: Farlow 1993 gives prey:predator ratios of 100-200:1.
- **C.** Tighten the food rules until the check bites. Not recommended; it's tuning without a reason.

Fun lane 43 built stage 1: per cell, all dragon kinds together are held to the food there (10%/yr of the wild herds plus 10%/yr of the herders' stock, both unverified), each dragon needing the younger schedule's 5.4 cattle (2.7 t) a year. On the 6 worlds x rolls 7000-7001 (and 7002-7003 for the default arm) it changes no count: present dragons per run are identical with the cap on and off on 4 of 4 checked runs, and the worst cell's need is 16% of its supply, the worst pocket's 8-16%. It bites only in cells whose food is exactly zero (barren desert, a few dozen cells), where the uncapped run had a handful of expected dragons.

Why: at 1 t/km2 of prey the food supports ~1 dragon per 27 km2 at 1 t/km2 of prey (2.7 t / 0.1 t/km2/yr), whereas the natural density (Carbone and Gittleman, ~1 per 270 km2 at 1 t/km2 at the younger eco mass) is ~10x below that and the pressed 1 per 5,000 km2 far below. The old section 5 ">100%" came from comparing an ancient's whole yearly kill with the stock in its range as if it ate only stock; with wild prey and stock eaten in proportion to what each supplies, the worst share of a pocket's stock taken is under 1%/yr.

Options:
- **A.** Leave stage 1 as a safeguard (it will bind in a hungrier setting: meta.dragon_km2 small, or the poor-prey worlds) and go on to stage 2 (peoples' and other predators' share), where the food will start to bind.
- **B.** Derive the natural density from the food too (dragons' share of the surplus / food per dragon) instead of Carbone, so food is the mechanism, not a check; Carbone then becomes a cross-check.
- **C.** Raise OFFTAKE-style shares, or lower the herders' tolerated loss, until the cap is a real limit (a tuning against nothing; not recommended).

Lean: A now, B with stage 2 (the budget is only a budget once hunters and herders draw on it too).

## Updates
- 2026-10-29: 2026-10-29: plain-language summary added at the top; to discuss with the owner.
- 2026-10-29: Papers read 10-29 bearing on option B (density from food): Farlow 1993 (pp. 171-174) builds predator density exactly that way, predator density x mass x intake = prey density x mass x turnover (eqs. 1-5), with intake 48.87 M^-0.30 kg/kg/yr for endotherms (eq. 7, p. 172) and 3.81 M^-0.16 for reptiles (eq. 8, p. 187). His reptile density fit, 66.07 M^-1.01 per km2 (M kg, p. 187), gives ~1 per 50 km2 at 3.2 t, close to Marshall's mesotherm line (~1 per 65, all ages). Jetz et al. 2004 (Table 1, p. 268) puts a 3.2 t mammal carnivore's home range at ~8,400 km2 (~52 km radius), near FORAGE_KM = 60. Nothing here favours A over B; it shows B has a standard form.
- 2026-10-29: Created from inbox draft draft-dragon-food-cap-does-not-bind.md (found by fun-lane-43).
