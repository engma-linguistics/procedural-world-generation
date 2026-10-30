---
title: A city minority's share of the townsfolk is fixed; let it grow when its own people's country is squeezed
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-54
blocked_by: []
relates: [PW-889, PW-928]
refs: [planet/lineages/history/cities.py, planet/lineages/history/pressure.py]
---

## Description
In plain words. The city goblins and city kobolds (PW-889) are a fixed share of the townsfolk (3% and 2%) in the busiest towns near
their own people's country, whatever happens to that people. In the owner's picture, a people pushed out of its wild country would
drift into the towns. The model already measures how squeezed a people is (pressure.squeeze, used by the among/integration rule), so
the share could rise with that squeeze, for example share x (1 + squeeze), and fall back when the people's own country is roomy again.
- [ ] the city share follows its people's squeeze (owner to approve the form); show it in the Results tab's peoples table
