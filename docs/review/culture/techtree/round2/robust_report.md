# Peoples robustness suite: 8 runs (/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l200/robust)

## Invariants per run

| run | peoples | crash | lost (why) | top people | top share | mono | most cells led | wall s |
|---|---|---|---|---|---|---|---|---|
| humans_only-s10@4360a3 | 1 | - | - | human | 100% | ok | human 100% | 15.8 |
| humans_only-s10@af2677 | 1 | - | - | human | 100% | ok | human 100% | 14.6 |
| humans_only-s7@4360a3 | 1 | - | - | human | 100% | ok | human 100% | 78.1 |
| humans_only-s7@af2677 | 1 | - | - | human | 100% | ok | human 100% | 76.5 |
| no_dragons-s10@4360a3 | 23 | - | - | human | 27% | ok | human 19% | 163.5 |
| no_dragons-s10@af2677 | 23 | - | - | hobgoblin | 22% | ok | hobgoblin 21% | 154.4 |
| no_dragons-s7@4360a3 | 23 | - | - | human | 33% | ok | human 22% | 224.6 |
| no_dragons-s7@af2677 | 23 | - | - | hobgoblin | 32% | ok | hobgoblin 22% | 213.4 |

| founding arm | runs counted | any fail | crash | a people extinct | one people over 85% |
|---|---|---|---|---|---|
| now | 8 | 0 | 0 | 0 | 0 |

(info-only trees, all_at_once, are not counted.)

## Continental blocs (landmasses of 1+ Mkm² with people)

| run | landmasses | led by a non-human people | non-human majority (>50%) | humans under 50% | distinct leaders | median peoples making 90% | mix distance from the world's (people-weighted) | leaders (share of the landmass's people, largest landmass first) |
|---|---|---|---|---|---|---|---|---|
| humans_only-s10@4360a3 | 8 | 0 | 0 | 0 | 1 | 1 | 0.00 | human 100%, human 100%, human 100%, human 100%, human 100%, human 100% |
| humans_only-s10@af2677 | 6 | 0 | 0 | 0 | 1 | 1 | 0.00 | human 100%, human 100%, human 100%, human 100%, human 100%, human 100% |
| humans_only-s7@4360a3 | 9 | 0 | 0 | 0 | 1 | 1 | 0.00 | human 100%, human 100%, human 100%, human 100%, human 100%, human 100% |
| humans_only-s7@af2677 | 1 | 0 | 0 | 0 | 1 | 1 | 0.00 | human 100% |
| no_dragons-s10@4360a3 | 9 | 5 | 2 | 5 | 3 | 4 | 0.42 | hobgoblin 53%, elf 34%, hobgoblin 27%, elf 59%, human 60%, human 81% |
| no_dragons-s10@af2677 | 6 | 3 | 1 | 5 | 4 | 3.5 | 0.39 | hobgoblin 33%, human 35%, aarakocra 99%, leonin 45%, human 54%, human 37% |
| no_dragons-s7@4360a3 | 9 | 2 | 1 | 4 | 3 | 3 | 0.52 | hobgoblin 33%, kenku 59%, human 42%, human 48%, human 64%, human 89% |
| no_dragons-s7@af2677 | 6 | 6 | 4 | 6 | 3 | 2 | 0.14 | hobgoblin 32%, elf 52%, gnome 70%, hobgoblin 46%, gnome 65%, elf 93% |

## The commonest people's share (owner D31 A: reported, not a failure)

Usually under 50% of all people; never over 70% with 5+ peoples.

| tree | runs | median commonest share | runs under 50% | runs with 5+ peoples | of those, at or under 70% |
|---|---|---|---|---|---|
| humans_only | 4 | 100% | 0% | 0 | - |
| no_dragons | 4 | 29% | 100% | 4 | 100% |
| all tries | 8 | 67% | 50% | 4 | 100% |

## Authored trees (median over worlds and seeds; per arm: top people and share, peoples under 0.1%, dead)

| tree | rationale | arm | runs | top | top share | median people >= 1% | under 0.1% | dead |
|---|---|---|---|---|---|---|---|---|
| humans_only | Humans only: every other people, the dragons and the giants off; only the humans' stems ke | now | 4 | human | 100% | 1 | - | - |
| no_dragons | No dragons: dnd with the ten dragon kinds and their two great branches off. | now | 4 | hobgoblin | 24% | 9.5 | sea_elf, tortle | - |

## Founding range and stem inheritance (median over runs, Mkm2: founded / inherited at the stem's end / present)

| people | now |
|---|---|
| aarakocra | 0.423 / 0 / 18.6 |
| bugbear | 0.504 / 0 / 4.25 |
| dragonborn | 0.71 / 0 / 26.2 |
| drow | 0.367 / 0 / 0.623 |
| dwarf | 0.324 / 0 / 2.96 |
| elf | 6.41 / 0 / 19.2 |
| firbolg | 0.504 / 0 / 2.74 |
| gnome | 5.47 / 0 / 4.91 |
| goblin | 0.554 / 0 / 7.64 |
| goliath | 0.461 / 0 / 2.08 |
| halfling | 0.629 / 0 / 5.58 |
| hobgoblin | 0.666 / 0 / 37.8 |
| human | 0.48 / 0 / 50.3 |
| kenku | 0.567 / 0 / 20 |
| kobold | 0.623 / 0 / 11.2 |
| leonin | 0.604 / 0 / 20.8 |
| lizardfolk | 0.486 / 0 / 18.9 |
| orc | 0.597 / 0 / 17.9 |
| sea_elf | 0.156 / 0 / 1.16 |
| tabaxi | 0.405 / 0 / 13.4 |
| tortle | 0.199 / 0 / 5.45 |
| triton | 0.455 / 0 / 3.83 |
| troglodyte | 0.704 / 0 / 0 |
