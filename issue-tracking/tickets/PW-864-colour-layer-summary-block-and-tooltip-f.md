---
id: PW-864
title: Colour-layer summary block and tooltip for the peoples, animal, crop, land use and resource layers
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: fun-lane-25
blocked_by: []
relates: [PW-840]
refs: [viewer/index.html]
created: 2026-10-25
updated: 2026-10-25
---

## Description
PW-840 (lane 25) added a per-layer summary at the top of the Summary panel (renderLayerSum) and a hover tooltip (tipHtml). They cover categorical layers (biome, climate, rock, vegetation, soils, landforms, fuels) and the ramp layers with one number per cell. Not covered yet, so they show only the old text: peoples / peoples mix / overlay / blend (share of land per people, mixing area), animal: and crop: layers (area known vs wild range), land use (cropland, pasture shares), resources, coasts, and the 64-bit crop masks. The tooltip for those layers falls back to height and position. The owner said the fuel, horse and salt views were hard to read: horse is an animal: layer and salt a resource layer, so those are the first to add.

## Updates
- 2026-10-25: Created from inbox draft draft-summary-blocks-for-peoples-animal-crop-layers.md (found by fun-lane-25).
- 2026-10-25: (fun-lane-27) Done in viewer/index.html (`layerSpecial`, cached per layer/frame; hooked into `renderLayerSum` and `tipHtml`). Summary blocks and tooltip values now exist for: peoples / peoples mix / overlay / blend (leading people's share of the land and Mkm², share peopled and share holding 2+ peoples; mix histogram), `animal:` and `crop:` (wild range, known range, share of the wild range known, area carried outside it), land use (cropland, pasture, burned, managed woods, densely settled; present only), resources (leading resource shares), single `resource` (likely 0.5+ / possible 0.15-0.5 area, mean; the tooltip gives the likelihood, so salt reads off), building stone, coasts (km by form) and the coast score layers. Checked with headless Chrome on port 8791 against run b69f51 (horse: wild 34.3 Mkm2, known 125.3 Mkm2 = 76% of the wild range, 99.3 Mkm2 carried outside it; peoples; land use) and world 2a7385 (salt: 0.31 Mkm2 likely, 1.37 possible). Also fixed: the culinary-brief overlay (`briefBox`, inline display:flex) overrode its `hidden` attribute and darkened the page from load; a `[hidden]{display:none !important}` rule now wins. Not done: a tooltip for the `body:` layers (still the old text).
