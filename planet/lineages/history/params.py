"""The tuning constants of the peoples history (each documented where it is set)."""

from __future__ import annotations

HOP_EVERY_KYR = 1.0  # long sea crossings are drawn about this often (with the time since)
PIONEER_P = 1.0  # pressure a people's frontier carries into empty country, at most (its habitat there); 0: only its presence
POLY_MKM2, POLY_MAX = 2.0, 4  # polycentric origins (owner 2026-10-27, origins._polycentric): a split founds in one patch per this many Mkm² of the parent's range, at most this many
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
# staying held by a thin remnant. Never below the refuge floor: the lapse takes cells only while the range exceeds REFUGE_MKM2 (displacement's own gate).
# The same line bounds a jump's landing (PW-929): a people under HOLD_MIN x K on a cell holds it too thinly to keep founders out
NEAR_KM, NEAR_RANGE = 300.0, 0.5  # a 'near' wish's pull on the habitat: x(1 + 0.5 w) at the other's border, e-folding 300 km
NEAR_TOLERANCE = 0.5  # ...and the two compete this much less with each other
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
PIONEER_KYR = 8.0  # a newcomer's founding window (PW-869): the competition it feels is cut by PIONEER_Q at first, ramping back over this, and its founders are not displaced
PIONEER_Q = 0.5  # (its founders take the room as a first settler does in empty country; the incumbents press back as the window closes)
EXPANSE_PRESS = 0.6  # an expansive people (explore from EXPANSE_FROM, in full at +EXPANSE_SPAN) that holds a small share of the country it could hold
EXPANSE_FROM, EXPANSE_SPAN = 0.4, 0.3  # ...presses into country others hold: the competition it feels falls by up to this x its expansiveness x the unfilled
EXPANSE_FILL = 0.5  # share (1 - its range / (this x the country with K >= 0.3)); alone the founding window left the elves at 2 of 8 tries with 500 cells
PARTNER_PULL = 4.0  # a sea landing of a people whose contact hybrid is wanted is this much likelier (x1 + this) on the partner's own coast (PW-861)
MEGAFAUNA_PUSH = 0.1  # the competition a megafauna line (a handful of dragons per country, spec megafauna) puts on others, against its niche overlap (PW-855)
HYBRID_REACH_KM = 600.0  # an arrival whose hybrid is wanted comes down within about this of the other parent's range (PW-852)
LINGER_MIN = 0.3  # ...but where they last met it lives on as a small people of its own (at least this share)
HYBRID_FROM_KYR = 12.0  # coordinator 2026-10-27: hybrid peoples (half-elves, half-orcs) appear no earlier than the farming onset (~12-10 kyr ago,
# the Natufian / early Neolithic): before it, contact between foragers leaves ancestry traces (contacts.py) but no people of mixed descent of its own
HOLOCENE_KYR = 10.0  # the land's living goods (farmland, pasture, forest, coasts) are today's from then on
INVADE, INVADE_FLOOR = 0.5, 0.3  # frontier invasion (PW-887): on the cells touching its range, a rival thinner than one weighs exp(-INVADE x ln(own density / its))
# (a small demographic edge at the front displaces a thinner people, the modern-human / Neanderthal mechanism: Banks 2008, Kolodny & Feldman 2017), at least INVADE_FLOOR
CROWD_HOP, CROWD_ENTER = 2.0, 0.5  # crowding drives exploration (PW-887): a people that loses share of its held country to rivals crosses water (the crossing rate x 1 + CROWD_HOP x crowd,
# within its craft: crossing.modes) and enters poor country (the entry pressure a0 -> a0 + (1 - a0) x CROWD_ENTER x crowd)
DENSITY_PUSH, DENSITY_CLIP = 0.1, (0.7, 1.4)  # competition felt from a rival x (its density / one's own)^0.1, within
# 0.7..1.4: numbers tell a little where peoples share land (farmers at 10 /km² press on foragers at 2 x1.17; giants
# at 0.005 dent others' room x0.7 and feel theirs x1.4). Mild: at 0.25, 0.5..2, the elves and orcs lost
# most of their land to the humans in single tries on 1df1c3
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
JUMP_KM, JUMP_SWIM_KM = 300.0, 1000.0
JUMP_MAX = 25.0  # (jump lengths searched: exp(-25^0.5) = 0.7% of a jump next door)
JUMP_HEMMED = 0.05  # 'no room next door': under this share of the cells next to its range are free good country (room and K >= 0.3)
# (PW-928: a judgement threshold, kept: at a few percent of free frontier the ordinary spread still has somewhere to go; jumps are
# the fallback of a people with essentially none, as long-distance dispersal is favoured when local competition is saturated,
# Hamilton & May 1977, "Dispersal in stable habitats")
EXPLORE_MARGIN = (0.25, 0.5)  # into marginal land (K < 0.3) the spread keeps a + (1 - a) K / 0.3, a = [0] + [1] x explore
MVP_TAU_KYR = 2.0  # a separate patch of a people with fewer than meta.viable_pop people fades with this e-folding time
MVP_EVERY_KYR = 1.0  # (looked at about this often; a people's largest patch is never faded: its refuges hold)
GROUP_KIN = 0.5  # a group, its people and its sister groups compete at this share of their niche overlap, with no
# closed-country exclusion (terr 0): one people, mixing freely where their ways of life overlap (PW-665)
GROUP_MARGIN = 0.15  # a group appears where its own habitat beats its people's by this share (its niche exists there)
COMPOSITION_TWO_PCT = 10  # a cell holds 2+ peoples when its second people has at least this share (percent)
PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c",
           "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
           "#000075", "#a9a9a9", "#ff7f50", "#7fffd4", "#dc143c", "#00bfff", "#adff2f", "#ff69b4", "#cd853f"]

CHAIN_CELLS = 4
PORTAL_SEP_KM = 1800.0  # portals are at least this far apart
PORTAL_KM = 700.0  # an arriving people founds at a portal if it can live within this of it...
PORTAL_FAR_KM = 2500.0  # ...else within this of it (the portal opens onto bad ground for it); else at its best habitat anywhere
