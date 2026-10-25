---
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
---

## Description
PW-840 (lane 25) added a per-layer summary at the top of the Summary panel (renderLayerSum) and a hover tooltip (tipHtml). They cover categorical layers (biome, climate, rock, vegetation, soils, landforms, fuels) and the ramp layers with one number per cell. Not covered yet, so they show only the old text: peoples / peoples mix / overlay / blend (share of land per people, mixing area), animal: and crop: layers (area known vs wild range), land use (cropland, pasture shares), resources, coasts, and the 64-bit crop masks. The tooltip for those layers falls back to height and position. The owner said the fuel, horse and salt views were hard to read: horse is an animal: layer and salt a resource layer, so those are the first to add.
