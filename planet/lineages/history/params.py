"""The tuning constants of the peoples history (each documented where it is set)."""

from __future__ import annotations

HOP_EVERY_KYR = 1.0  # long sea crossings are drawn about this often (with the time since)
PIONEER_P = 1.0  # pressure a people's frontier carries into empty country, at most (its habitat there); 0: only its presence
FOUNDER_KM = 400.0  # a split's founders hold the suitable country within this of the origin
CONVERGE = 400  # passes at a deep (Myr) step: ranges fill what is connected
FARM_KYR = 6.0  # agricultural lines speed up from then
MIX_DROP = 0.6  # competition falls by this share by the present (from mixing_start), in full corridors
ALPHA_CLOSED = 1.4  # competition in closed country (contact 0), whatever the niches: over 1, the larger excludes
TAU_KYR = 1.0  # a people held above its competitive room declines toward it with this e-folding time
REFUGE_MKM2 = 0.5  # ...more slowly as its range shrinks toward this (last refuges hold out: no line is pushed out)
HOLD_MIN = 0.25  # PW-920 (kept, PW-928: crude but sound): a people displaced below this share of its carrying density on a cell (p < HOLD_MIN x K) loses its hold there and
# leaves (the Allee threshold: under a critical density a local population declines to nothing, Courchamp, Berec & Gascoigne 2008, Allee Effects
# in Ecology and Conservation; critical densities of order a fifth to a quarter of K), so the rival moves in fully instead of the land
# staying held by a thin remnant. Never below the refuge floor: the lapse takes cells only while the range exceeds REFUGE_MKM2 (displacement's own gate)
NEAR_KM, NEAR_RANGE = 300.0, 0.5  # a 'near' wish's pull on the habitat: x(1 + 0.5 w) at the other's border, e-folding 300 km
NEAR_TOLERANCE = 0.5  # ...and the two compete this much less with each other
AMONG_TOLERANCE = 0.7  # PW-889: an 'among' wish (a lives readily inside b's country, bugbears among goblins) cuts the pair's competition by
# this x its weight, both ways, and b's frontier does not invade a's cells. A design judgement: more than a 'near' pair's border tolerance, so
# alike peoples in closed country (ALPHA_CLOSED 1.4) fall to ~0.4, well under the 1 at which the larger excludes the other: they share cells
INTEGRATE = 0.5  # PW-889 (owner 10-29): under pressure a people grows more willing to live among a neighbour, as a survival strategy. The
# competition a squeezed people feels from each rival falls by up to this x its squeeze x how readily the two live side by side (the
# cohabitation matrix, compose.cohabitation: openness, near/among/apart wishes), so it shares a friendly neighbour's land rather than lose it,
# and hardly an enemy's. Squeeze = its crowding (pressure.crowding, the last step's) x how little of the country it could hold it holds
# (1 - held / (SQUEEZE_FILL x potential), as EXPANSE_FILL). A design judgement: at most half, so a squeezed people persists thinly inside
# the friendly range rather than taking it over
SQUEEZE_FILL = 0.5
CITY_TOP, CITY_MIN_KM2 = 0.05, 5.0  # PW-889: a city-minority group lives in its hosts' town country: the cells among the densest CITY_TOP of the
# peopled land this step by the hosts' settlement (people per km2 of the host peoples there, presence x density), and settled at least
# CITY_MIN_KM2. A design judgement, relative because a world's peak settlement varies (on world af2677 the 20 /km2 first tried was reached
# by 0-200 cells, none near the goblins in most rolls): the densest twentieth of the peopled land is where the towns are; the floor keeps
# a world of foragers townless
CITY_REACH_KM = 1000.0  # ...within this, over land, of its own people's range: the city minority comes in from its people's country
NEAR_ORIGIN_KM, NEAR_ORIGIN = 1000.0, 2.0  # ...and on an origin's placement (up to x3 next to it, e-folding 1000 km)
LOST_PENALTY = 0.05  # best of N: score taken off a try per line lost that the tree says lives at the present
APART_CONTESTED = 0.1  # an 'apart' or 'near' wish counts when the two niches would put at least this share of a's habitat near b's
START_KM = 1500.0  # a start hint's reach (PW-763): 'far_from' ramps from x0.05 at the other's border to x1 over this, 'near' falls off with it
NEAR_SCORE_KM = 330.0  # a 'near' wish is met for the share of a's range within this of b's (3 cells at L6)
LINGER_KYR = 10.0  # a contact hybrid lingers where its parents no longer meet, fading with this e-folding time...
ARRIVAL_ROOM = (0.5, 0.2, 0.0)  # an arrival near its hybrid partner takes the free room (share of its best habitat) of the first tier that has some, PW-861
ARRIVAL_POCKET_RINGS = 3  # ...and the free room around a cell is averaged over this many rings (PW-861)
SPECIES_AREA_Z = 0.3  # PW-888: the share of origins a landmass draws goes as (its habitable area)^z, z ~ 0.25-0.35 (the species-area relationship, Rosenzweig 1995, Species Diversity in Space and Time); islands keep some, as isolation drives speciation
ORIGIN_MVP_MULT = 8.0  # PW-888: the census minimum viable population over the REFERENCE horizon, this many times tree.viable_pop (500 in the presets = Frankham 2014's 500 for lasting evolutionary potential): Traill et al. 2007's median MVP for vertebrates is ~4000 = 8 x 500, for about MVP_REF_GEN generations
MVP_REF_GEN = 40.0  # ...Traill et al. 2007 take persistence over ~40 generations
PERSIST_EXP = 1.0  # PW-888: a daughter must persist from its origin to the present, so the population it needs grows with the horizon. Lande 1993 (environmental stochasticity): mean persistence time T ~ K^c with c = 2r/sigma_e^2 - 1 (Foley 1994 for vertebrate data), so the K needed for T goes as T^(1/c). c = 1 is r = sigma_e^2, a population growing as fast as its environment fluctuates; the literature gives a spread of c, this is its middle, not a fit to any target. K_req = ORIGIN_MVP_MULT x viable_pop x (horizon in generations / MVP_REF_GEN)^(1/c)
SURGE_Q = 0.5  # owner 10-30 (lane 73; in place of PW-869's founding window): a people on the upswing feels the competition of the peoples
# whose land it contests up to this much less (x the era's dial, meta.surge_early / surge_late), by its momentum (pressure.surge). The
# window's half, kept: at 0.5 a surging people takes room where its rivals stand at under twice its own claim, and an expansion that is
# not followed by holding the land fades back (failed forays: the edge goes once growth stalls). A design judgement
SURGE_KYR = 4.0  # ...its momentum: the range mass against its own mass lagged by this e-folding time, ~160 generations; half the old
# 8 kyr window's length scale, so the edge of a newcomer lasts a few kyr (the window's span) and an expansion's for as long as it grows:
# the Bantu, Austronesian and steppe expansions ran for 1-4 kyr each (Phillipson 2005; Gray et al. 2009, Science 323; Haak et al. 2015,
# Nature 522). The momentum is full at SURGE_FULL x the lagged mass
SURGE_FULL = 2.0
SURGE_LATE_FROM_KYR = 12.0  # the early dial holds before this (the farming onset, as HYBRID_FROM_KYR), the late at the present, blended between
EXPANSE_PRESS = 0.6  # an expansive people (explore from EXPANSE_FROM, in full at +EXPANSE_SPAN) that holds a small share of the country it could hold
EXPANSE_FROM, EXPANSE_SPAN = 0.4, 0.3  # ...presses into country others hold: the competition it feels falls by up to this x its expansiveness x the unfilled
EXPANSE_FILL = 0.5  # share (1 - its range / (this x the country with K >= 0.3)); alone the founding window (PW-869, now the momentum edge) left the elves at 2 of 8 tries with 500 cells
PARTNER_PULL = 4.0  # a sea landing of a people whose contact hybrid is wanted is this much likelier (x1 + this) on the partner's own coast (PW-861)
MEGAFAUNA_OFF = 0.1  # PW-924: a megafauna line's habitat outside its own country (its prefers), against 0.4 for a people: dragons and giants
# lair in their kind's country (swamp for black dragons, volcanoes for red), not anywhere they could survive
TOLERATE_K = 0.5  # PW-1024 (owner 10-29, option A): a megafauna kind's habitat in the country it tolerates (spec `tolerates`: the edge fits, green
# dragons in forest-steppe, white on the harsh northern steppe), against 1 in its own country and MEGAFAUNA_OFF elsewhere. A design judgement,
# not a measured number: half, so the edge holds them at half their density and counts as reachable country (history.megafauna SUITABLE)
EDGE_C, EDGE_OCT, EDGE_ELEV_M = 5.0, 0.5, 1000.0  # PW-1024: in that tier (and in ecological release, megafauna.release) the kind's comfort range is
# widened by this much on each side: degrees C of the annual mean, octaves of the rain (x1.4), metres of its height band. A design judgement: "at
# the edges" means a few degrees and a wetter or drier margin past where it lairs (silver dragons ranging down from the peaks over high steppe)
MEGAFAUNA_PUSH = 0.1  # the competition a megafauna line (a handful of dragons per country, spec megafauna) puts on others, against its niche overlap (PW-855)
HYBRID_REACH_KM = 600.0  # an arrival whose hybrid is wanted comes down within about this of the other parent's range (PW-852)
LINGER_MIN = 0.3  # ...but where they last met it lives on as a small people of its own (at least this share)
HYBRID_FROM_KYR = 12.0  # coordinator 2026-10-27: hybrid peoples (half-elves, half-orcs) appear no earlier than the farming onset (~12-10 kyr ago,
# the Natufian / early Neolithic): before it, contact between foragers leaves ancestry traces (contacts.py) but no people of mixed descent of its own
HOLOCENE_KYR = 10.0  # the land's living goods (farmland, pasture, forest, coasts) are today's from then on
# (lane 83, owner D20: PW-887's frontier invasion by density, INVADE, and lane 63's DENSITY_PUSH, numbers in the competition, are gone:
# the contest is decided by fit, FIT_Q below, not by who is denser; density sets how many people a land holds, not who holds it)
CROWD_HOP, CROWD_ENTER = 2.0, 0.5  # crowding drives exploration (PW-887): a people that loses share of its held country to rivals crosses water (the crossing rate x 1 + CROWD_HOP x crowd,
# within its craft: crossing.modes) and enters poor country (the entry pressure a0 -> a0 + (1 - a0) x CROWD_ENTER x crowd)
# overland (and over-water) jump dispersal (PW-920, owner 2026-10-27): a crowded people with no free country next door founds,
# now and then, on free suitable land farther off. Long-distance dispersal is rare and its kernel fat-tailed (Clark et al. 1998,
# "Reid's paradox of rapid plant migration", BioScience 48; Nathan et al. 2012, "Dispersal kernels: review", in Dispersal Ecology
# and Evolution): the weight of a place D jump lengths away is exp(-D^c) with c ~ 0.5 (Clark 1998's fitted exponential-power shape;
# c = 1 is the thin-tailed exponential). The lengths go by mobility: a walking people JUMP_KM (ethnographic and prehistoric
# relocations of foragers over a few hundred km: the order of the largest mammal natal dispersal, Sutherland et al. 2000), fliers
# spec.HOPS['flies'] over land and sea alike (birds disperse several times farther than mammals of their size, Paradis et al. 1998),
# a land people over water its crossing craft's reach (crossing.modes, raft drift excepted: that is crossing.hop's), a sea people
# (marine realm) JUMP_SWIM_KM over water (marine dispersal runs orders of magnitude farther than terrestrial, Kinlan & Gaines 2003)
JUMP_RATE = 0.02  # jumps per kyr of a fully crowded, fully hemmed-in people (one in ~50 kyr: deep-time steps are kyr to Myr, rare jumps suffice).
# Crude but sound (PW-928, coordinator 2026-10-27): no study gives a founding rate per people; one long relocation per ~2000 generations of a
# boxed-in people keeps jumps the rare tail of dispersal (Nathan 2012: long-distance events are a small share of all moves) while a
# squeezed people still gets several chances over a glacial cycle (~100 kyr)
JUMP_SHAPE = 0.5  # c of the exponential-power kernel exp(-(d / L)^c)
JUMP_KM, JUMP_SWIM_KM = 800.0, 1000.0  # owner 2026-10-27: walkers ~800 km (was 300). Forager fronts advance ~0.5-1 km/yr (Ammerman &
# Cavalli-Sforza 1984 for the Neolithic wave of advance ~1 km/yr; Hamilton & Buchanan 2007 ~0.5-1 km/yr for the Clovis spread), so a
# kyr-long step spans 500-1000 km of advance. A long jump is a small scouting band seeking better country: the kernel exp(-D^0.5)
# keeps a far landing rarer than a near one (few make it), and the founding weight (room there) favours the shorter successful ones
JUMP_MAX = 25.0  # (jump lengths searched: exp(-25^0.5) = 0.7% of a jump next door)
JUMP_HEMMED = 0.05  # 'no room next door': under this share of the cells next to its range are free good country (room and K >= 0.3)
# (PW-928: a judgement threshold, kept: at a few percent of free frontier the ordinary spread still has somewhere to go; jumps are
# the fallback of a people with essentially none, as long-distance dispersal is favoured when local competition is saturated,
# Hamilton & May 1977, "Dispersal in stable habitats")
EXPLORE_MARGIN = (0.25, 0.5)  # into marginal land (K < 0.3) the spread keeps a + (1 - a) K / 0.3, a = [0] + [1] x explore
MVP_TAU_KYR = 2.0  # a separate patch of a people with fewer than meta.viable_pop people fades with this e-folding time
MVP_EVERY_KYR = 1.0  # (looked at about this often; a people's largest patch is never faded: its refuges hold)
# (a group, its people and its sister groups share one capacity: alpha 1 among them, no closed-country term, lane 83, PW-1205 A;
# PW-665's GROUP_KIN 0.5 let them stack to ~1.35 K a cell)
GROUP_MARGIN = 0.15  # a group appears where its own habitat beats its people's by this share (its niche exists there)
COMPOSITION_TWO_PCT = 10  # a cell holds 2+ peoples when its second people has at least this share (percent)
PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c",
           "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
           "#000075", "#a9a9a9", "#ff7f50", "#7fffd4", "#dc143c", "#00bfff", "#adff2f", "#ff69b4", "#cd853f"]

CHAIN_CELLS = 4
BREAKS_RISE = 2.0  # PW-1024: 'breaks' (badlands, buttes, river breaks) is open country rising at least this many m per km to a neighbour (~120 m
BREAKS_RAIN = 1100.0  # over an L7 cell) with under this much rain, below the mountains. Badlands are far finer than a cell, so this is a proxy:
# rugged open grassland, about a third of the open land under 1,100 mm on world 2a7385 (lane 50 probe). A design judgement
PORTAL_SEP_KM = 1800.0  # portals are at least this far apart
PORTAL_KM = 700.0  # an arriving people founds at a portal if it can live within this of it...
PORTAL_FAR_KM = 2500.0  # ...else within this of it (the portal opens onto bad ground for it); else at its best habitat anywhere
PORTAL_WAIT_KYR = 5.0  # lane 78: an arrival (or a later wave) waits up to this long for a wandering thinning over land it can live on; then
# the first wave comes at its best habitat (as without portals) and a later one does not come. A design judgement: about one opening
SCATTER_KM = 100.0  # lane 78: a wandering thinning is placed this far (rms) off its site, as volcanism.hotspots scatters a new plume by ~100 km

FIT_Q, BREADTH_Q, FIT_CLIP = 1.0, 0.5, 3.0  # lane 83 (owner D20, PW-1180 option A: "fit decides the contest"): where two peoples want the
# same cell, the competition line k feels from rival j there is weighted by how much better j suits the cell than k does: x clip(S_j / S_k,
# 1 / FIT_CLIP, FIT_CLIP), with a people's contest strength S = (fit here)^FIT_Q (the fit: how well the land suits its body and ways, its
# learned country in, before the land's goods, herds and crops, habitat._K) x (1 / its breadth)^BREADTH_Q (x its martial strength, spec
# `contest`). K saturates at 1 over a people's whole comfort range, so where a broad people and a specialist both reach K = 1 the tie used to
# go to the denser (the old DENSITY_PUSH, INVADE) or the first; the breadth (the sum of its fit at the step) is the specialist-generalist
# trade-off: a people that lives everywhere is not the best at any one country, and one adapted to a narrow country is better there (the
# orangutans keep the jungle). A design judgement, not a measured number: the square root, and the clip at x3 either way so a tiny niche is
# not invincible; FIT_Q 1 so a people at its margin (fit 0.4 off its preferred country) presses less there than one at home
PEOPLE_PROD = True  # PW-974: a people's density per cell is its way-of-life number x the land's productivity (lineages.prey.people_fields); off only to measure what it does
COEXIST = True  # lane 73 (coordinator 10-30): mutual invasibility. Where two peoples' competition is under 1 both ways (Lotka-Volterra
# coexistence), each feels the other at most at its coexistence share (spread.coexist_cap), whichever came first: before, an incumbent
# at its full habitat left a newcomer K(1 - alpha) of room, under the establishment threshold (EST) and the hold (HOLD_MIN) wherever
# alpha_eff > ~0.75, so whoever reached a niche first kept it (kobolds held the mountains 1.5 Myr before the dwarves split, and the
# dwarves never got in). Off only to measure what it does
LEARN = True  # off: every habitat as the tree gives it (L stays 0; bit-identical to before)
BODY_C, BODY_OCT, BODY_ELEV_M = 8.0, 1.0, 1000.0  # the body envelope around the comfort range: degrees C of the annual mean on each side,
# octaves of the annual rain (x2 / x0.5) and metres of a height band. A design judgement, not a measured number: humans' comfort 6-26 C
# then tolerates -2..34 C, from the boreal forest edge to hot desert margins, while the polar ice, the hottest deserts and the driest
# land stay out of reach of a people whose comfort is temperate; a cold people (goliaths, -6..12 C) likewise stays out of the tropics.
# Real peoples went further still with clothing, fire and herds (the Arctic, below), so the envelope is a floor on what culture can do
ECTO_COLD_C = 1.0  # an ectotherm kind's (spec limits.cold_c: the saurian kin, tortles, lizardfolk, troglodytes) margin below its comfort
# range, in place of BODY_C: a cold-blooded body cannot be clothed against the cold (owner 10-30: "tortles really don't like the frozen
# north"). A design judgement; the heat side keeps BODY_C
T_LEARN_KYR = 5.0  # learned acceptance grows as (1 - L) with this e-folding time, in full where the people lives on country its culture
# finds marginal, and x its pressure on the ring of cells next to its range. Grounded on the human peopling of high and cold country
# (sources read 2026-10-30): settlement at 4,355-4,480 m in the Peruvian Andes by 12.8-12.4 kyr ago, within ~2 kyr of the first entry
# into the Americas (Rademaker et al. 2014, Science, doi:10.1126/science.1258260, "Paleoindian settlement of the high-altitude Peruvian Andes"); the Tibetan
# Plateau at 4,600 m visited 40-30 kyr ago (Zhang et al. 2018, Science 362:1049, Nwya Devu) but lived on all year only after ~3.6 kyr ago,
# with barley farming and herds (Chen et al. 2015, Science 347:248); people near 72 N by ~45 kyr ago, when earlier finds stop at 57 N
# (Pitulko et al. 2016, Science 351:260). So a margin is first held within ~1-2 kyr (L ~0.3 at 5 kyr e-folding, under full pressure) and
# lived in densely after ~10 kyr or more (L ~0.86 at 10 kyr)
FORGET_X = 10.0  # ...and fades where the people no longer lives (nor presses), with T_LEARN_KYR x this: knowledge outlives a retreat
CARRY = 0.9  # a pressed people moving into country of the same biome class (biome_class) as land it has learned carries that knowledge:
# the frontier cell takes up to CARRY x the best learned acceptance of its held neighbours of that class, x its pressure. Once a people
# has learned the tundra it can sweep the connected tundra (the Thule expansion); the tundra's lessons do not open the desert
FULL_FROM = 0.5  # pressure (0..1): the larger of the people's crowding (pressure.crowding) and how full its own country is, counted from
# this share of its good country held (K0 >= 0.3) to all of it. An unpressed people at home learns next to nothing
HIGH_M = 2500.0  # biome_class: land above this is high mountain whatever its climate
LEARNED_MIN = 0.5  # (reporting: a cell counts as learned country where L >= this and the preference alone gives K0 < 0.3)
LEARN_GAIN = 0.6  # learned country holds a people at most this share of the way from its preference to its body limit (K = K0 + GAIN L
# (T - K0)): the home country, where its way of life grew, stays its best; a frontier group lives thinner on what it learned. A design
# judgement, measured (lane 79, world 4360a3, dnd seed 7, one try): at 1 the first people into an empty continent (kobolds, ~100 kyr before
# the humans) learned the temperate lowlands and kept them (6.5% -> 27% of people; the peoples' biome mixes converged, homogenisation
# 0.63 -> 0.73); at 0.6 kobolds 11%, humans 73% -> 67%, homogenisation 0.62 as without learning
# (lane 77's SPLIT_FOUNDING switch is gone: lane 83, owner D20, made one-spot founding the rule, with the stem's land left empty at its
# end, origins._origin_split and _end_parent; PW-1152, PW-1181)
