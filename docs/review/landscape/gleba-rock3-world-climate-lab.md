# Competitor scan: Gleba, Rock 3, World Climate Lab
Date 2026-10-29. Sources actually read: Gleba itch page + devlog index + devlog #3, #4; Rock 3 Steam page + Steam appdetails API; World Climate Lab Steam page + appdetails API; web searches (little extra). Items marked (inferred) are my reasoning, not the sources'. Steam descriptions were summarised by the fetch tool, not read raw.

## 1. Summary table
| | Gleba (v0.3.6) | Rock 3 | World Climate Lab |
|---|---|---|---|
| Developer | Calandiel (solo?, inferred); Rust + Godot | Insight Games (support email on page) | "World Climate Lab Dev"; no publisher, no website |
| Price | Free download (itch); no price shown | Free (Steam, is_free) | $15.99, Early Access, released 2026-08-07 |
| Platform | Windows, Linux (215-232 MB) | Windows (DX11/12 dGPU, 8 GB RAM); 200 MB; GPU-only generation | Windows only; Vulkan GPU, min 6 GB VRAM (GTX 1660), 16 GB RAM; rec. 12 GB GPU, 32 GB RAM |
| Activity | Very active: devlog #1 Nov 2025 to v0.3.6 Sep 2 2026; 15 ratings, 5.0 | Released 2022-11-13; 126 reviews, 88% positive; no news/updates visible to me | 17 reviews all positive; ~6 months EA planned |
| Public methods | Devlog prose only; no source found | None found | None found; claims "checked against observed 1991-2020 climate zones" |
| Resolution | Not stated anywhere | Exports up to 8K; "5.9m cells" only in owner's paste (not on page I read; search found no confirmation) | Exports up to 8192x4096; sim grid not stated |

## 2. What each simulates
**Gleba** (page + devlogs): plate tectonics producing orogens and ocean features, adjustable plate motion; "mantle superswells" (plumes raising land); large igneous provinces; magma-cooling model giving bedrock types, rock classes (clastic sedimentary rarity fixed v0.3.4); surface-water erosion with soil transport; glaciation and last-glacial-maximum remnants; lakes (sweet/salt), aquifers and coral reefs (v0.3.2); climate model rewritten in devlog #3: geostrophic-wind approximation (pressure systems: subtropical high, polar front, ITCZ), ocean currents, seasonal climate, sampled 12x/year since v0.3.0 (was 2); plant-based biome map (grass, shrub, conifer, broadleaf); accretion simulation "inspired by the Nice model" for whole solar systems with moons. Custom map outlines / 16-bit heightmaps can drive climate. Dozens of sliders. Time evolution: NOT documented; nothing says Myr-scale stepping. The devlog says the climate "runs extremely quickly" and calls it maybe "the best available climate model for its computational budget" (author's claim). Netcode to view planets, 1-32 players (page); end-goal is a fantasy 4X/story sim ("scientifically accurate", page wording). Devlog #4 default start ~2000 BCE.

**Rock 3** (Steam): "simulates tectonics, erosion, and climate" for Earth-like planets, biomes over continents and islands, customization controls. Everything on GPU, real-time. Exports equirectangular biomes, elevation, heightmap, heat, water, landmasses. The page gives no mechanism, no timescale, no cell count. A Reddit comment found by search (anecdote) says its tectonics yield too much land for how long it was simulated, which hints at some time-stepped process (inferred, weak). Whether tectonics is a real plate simulation or noise/field synthesis: unknown.

**World Climate Lab** (Steam): climate only, no tectonics/erosion. "Real-time physics-based climate models on your GPU", "Every climate is calculated, not painted." Inputs: your own heightmaps, sea masks, depression masks, bathymetry, or a Topography Creator. Planet knobs: stars (binaries), orbit, axial tilt, day length, moons, atmosphere. 22 map views (surface, climate, atmosphere, ocean); Koppen classes for Earth-likes, custom classes for odd worlds; exports maps, posters, animations, climate data; Earth preset validated vs 1991-2020 zones; experimental deep-ocean model (beta). Page does not say which equations (could be energy-balance, could be primitive-equation; unknown).

## 3. Scale comparison (Earth area 510.1 M km^2; cell spacing = sqrt(area/N), equal-area, inferred)
| Grid | Cells | Spacing |
|---|---|---|
| procgen L6 | 40,962 | ~112 km |
| procgen L7 | 163,842 | ~56 km |
| procgen L8 | 655k | ~28 km |
| procgen L9 | 2.6M | ~14 km |
| **Rock 3 "5.9M"** | 5.9M | **~9.3 km** (hex-centre spacing ~10 km) |
| procgen L10 | 10.5M | ~7 km |
| procgen zoom 2 km/px, 2000 km | ~1M px | 2 km |
| Rock 3 8K export (8192x4096 = 33.5M px) | 33.5M | ~4.5 km at equator, coarser in cell terms |

So 5.9M is ~36x L7 and sits between L9 and L10 (about "L9.6"), about 5-6x finer linear than L7, but still 4-5x coarser than a procgen 2 km zoom. Single-pass or over time? Not stated on the page. Inferred: "real-time on the GPU" with 5.9M cells means each step is cheap, so it is either a single-pass synthesis of terrain plus a short iterative erosion/climate relaxation, or a coarse tectonic/erosion loop whose duration is not Myr-calibrated. A true 0.5-2 Gyr simulation at 9 km would be many orders of magnitude costlier than real-time (procgen: ~6 min/Gyr at L6, 30-40 min/Gyr at L7, per CLAUDE.md). Treat as "snapshot generator with simulation-flavoured passes" unless the developer says otherwise. Caveat: "cells" may be vertices of a rendered sphere mesh rather than simulation cells (inferred).

## 4. Subsystem comparison vs procgen_world
| Subsystem | procgen_world | Gleba | Rock 3 | WCL |
|---|---|---|---|---|
| Tectonics | Plates over 0.5-2 Gyr, run keyframes | Plates, orogens, superswells, LIPs; time model unknown | Claimed, GPU, unclear | none |
| Erosion/rivers | Iterative, drainage, deltas, glaciers | Water+soil erosion, lakes, aquifers, glacial | Claimed erosion, no rivers mentioned | none |
| Climate | Own climate pipeline, ice ages (time zoom 1 Myr) | Geostrophic winds, currents, 12 steps/yr, new biome class | Heat/water maps; method unknown | Core product; physics-based, 22 views, exotic stars/orbits/atmospheres |
| Biomes/vegetation | Biomes, vegetation groups | Plant-growth biomes | Biomes | Koppen + custom |
| Geology/resources | ~22 resource deposit models from history | Magma-cooling rock classes, igneous provinces | -- | -- |
| Zoom | 0.5-4 km/px regional + glacial time zoom | Tile/subtile map export (forum) | Export only | Export only |
| Life/people | Lineages, peoples, tech tree, languages | Fantasy 4X intent, not shown | none | none |
| Output | Viewer (three.js), text world format | Godot 3D, real-scale planets | Equirect maps to 8K | Maps, posters, animations, data |

## 5. Positioning
- Gleba sells "scientifically accurate" fantasy worlds, free, as a game/worldbuilding base with a Discord/Reddit community; closest rival in intent (Earth-like geology + fantasy). Open question: its tectonic time evolution.
- Rock 3 sells speed and exports: free, real-time, 8K maps for game devs/mapmakers/designers (Steam tags: Utilities, Game Development, Design & Illustration).
- WCL sells the "what if" climate sandbox: weird stars/atmospheres, validated Earth, polished UI, paid $15.99, 8 languages. Aimed at hobbyists/educators (inferred).
- procgen_world has what none show: deep-time tectonic history with keyframes, rivers/erosion/ice ages coupled, regional zooms consistent with parents, resource deposits from history, lineages/peoples/techs/language, and a viewer with time slicing. None of the three publishes anything past the world's physical state.

## 6. Ideas worth borrowing (ranked)
1. **Custom-input import** (WCL, Gleba): load a 16-bit heightmap / sea mask / outline and run climate, rivers, biomes on it. Cheap if `world` accepts a heightfield; huge for users; also a good test harness against Earth.
2. **Exotic-planet knobs in the viewer** (WCL): star/binary, tilt, day length, moons, atmosphere. Aligns with PW-443 planet-relative thresholds, but v1 is Earth-likes only (memory), so post-v1.
3. **Standard export bundle** (Rock 3, WCL): equirect PNG/EXR up to 8K for heights, biome, heat, water, landmasses, plus posters and animations. Makes the product usable without our viewer; owner needs viewer controls for it.
4. **Animated wind and ocean-current map modes** (Gleba) and 12 samples/yr seasonality: viewer layers for existing fields.
5. **Koppen-style legend and an explicit Earth validation panel** (WCL): advertise "checked vs 1991-2020" as a feature. We have earth_check; surface it.
6. **Quality slider / preview mode** (Rock 3: scale quality down for weak GPUs): L5-L7 presets in the UI.
7. **Devlog + Discord/Reddit cadence** (Gleba): visible changelog drives ratings; our wiki could feed it.
8. **Gleba features to compare against**: LIPs, superswells (mantle plumes; we have plume-hosted nickel), aquifers, reefs (we have reefs), accretion of whole systems (not ours).

## 7. Gaps and caveats
- Rock 3's 5.9M figure and tectonic time model are unverified; ask the owner for the paste's source or find the dev's docs/Discord.
- Gleba's source is not linked on the page I read; devlogs gave no resolution; one forum thread mentions "simulating plate movement with a height map" (title only, unread).
- WCL's Steam page was only read through summaries; Steam API description was paraphrased. The owner could paste the raw text.
- No videos, papers or talks were found or read.
