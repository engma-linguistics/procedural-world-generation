---
id: PW-944
title: "Tech tree v0: pottery and kilns have no clay layer; the land check is a proxy"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: culture
effort: s
impact: low
found_by: fun39-techtree
blocked_by: []
relates: [PW-713]
refs: [planet/lineages/samples/techtree.toml, planet/lineages/land.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
`pottery` needs clay, but land.GOODS has no clay good. The tech tree therefore uses `env_any = ["fertile", "foraging", "building"]` as a stand-in, and nearly every people passes it. In the same way, `canoes` read timber or sea mammals, and `sledges` read frost. A clay good (river floodplains, lake beds, weathered shale; soils.py has the texture) would make pottery uneven by land, as it was in reality: early in the Jomon lands and the Sahara, never in much of Sahul.
- [ ] a clay good in land.goods (from soils texture or floodplains)
- [ ] pottery and kilns read it

## Updates
- 2026-10-28: Created from inbox draft draft-techtree-clay-layer.md (found by fun39-techtree).
