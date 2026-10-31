# Stress suite on lane 83b's final code (commit b52c368c, arm now, one try per variant)

Made with `tools/peoples_robust.py report`. Raw results were in the lane's scratch dir; the base suite is suite-base.md.

# Peoples robustness suite: 86 runs (suite-final)

## Invariants per run

| run | peoples | crash | lost (why) | top people | top share | mono | most cells led | wall s |
|---|---|---|---|---|---|---|---|---|
| all_at_once-s10@4360a3 | 22 | - | - | human | 56% | ok | human 48% | 448.1 |
| all_at_once-s10@af2677 | 22 | - | - | human | 44% | ok | human 29% | 465.6 |
| all_at_once-s7@4360a3 | 22 | - | - | human | 54% | ok | human 43% | 537.6 |
| all_at_once-s7@af2677 | 22 | - | - | human | 43% | ok | human 45% | 407.7 |
| even_six-s10@4360a3 | 5 | - | - | human | 61% | ok | human 51% | 94.5 |
| even_six-s10@af2677 | 5 | - | - | halfling | 49% | ok | halfling 39% | 72.1 |
| even_six-s7@4360a3 | 5 | - | - | human | 48% | ok | human 44% | 111.6 |
| even_six-s7@af2677 | 5 | - | - | human | 42% | ok | human 39% | 72.0 |
| five_peoples-s10@4360a3 | 5 | - | - | human | 53% | ok | aarakocra 32% | 87.6 |
| five_peoples-s10@af2677 | 5 | - | - | gnome | 76% | ok | aarakocra 36% | 77.9 |
| five_peoples-s7@4360a3 | 5 | - | - | human | 71% | ok | aarakocra 38% | 109.8 |
| five_peoples-s7@af2677 | 5 | - | - | human | 52% | ok | aarakocra 34% | 73.0 |
| goblin_world-s10@4360a3 | 22 | - | - | human | 63% | ok | human 44% | 696.5 |
| goblin_world-s10@af2677 | 22 | - | - | human | 31% | ok | human 33% | 676.0 |
| goblin_world-s7@4360a3 | 22 | - | - | human | 34% | ok | human 19% | 847.0 |
| goblin_world-s7@af2677 | 22 | - | - | human | 39% | ok | human 32% | 565.9 |
| late_humans-s10@4360a3 | 23 | - | - | human | 72% | ok | human 59% | 740.0 |
| late_humans-s10@af2677 | 23 | - | - | human | 33% | ok | human 31% | 725.1 |
| late_humans-s7@4360a3 | 23 | - | - | human | 79% | ok | human 63% | 882.3 |
| late_humans-s7@af2677 | 23 | - | - | human | 57% | ok | human 56% | 579.0 |
| menagerie-s7@4360a3 | 52 | - | - | human | 30% | ok | human 14% | 1618.2 |
| menagerie-s7@af2677 | 52 | - | - | harengon | 14% | ok | dragonborn 13% | 1361.3 |
| mountain_stem-s10@4360a3 | 23 | - | - | human | 55% | ok | human 37% | 721.5 |
| mountain_stem-s10@af2677 | 23 | - | - | human | 35% | ok | hobgoblin 32% | 728.7 |
| mountain_stem-s7@4360a3 | 23 | - | - | human | 50% | ok | human 28% | 867.0 |
| mountain_stem-s7@af2677 | 23 | - | - | hobgoblin | 25% | ok | hobgoblin 23% | 598.8 |
| native_fey-s10@4360a3 | 23 | - | - | human | 61% | ok | human 38% | 731.5 |
| native_fey-s10@af2677 | 23 | - | - | hobgoblin | 51% | ok | hobgoblin 41% | 734.1 |
| native_fey-s7@4360a3 | 23 | - | - | human | 69% | ok | human 33% | 814.6 |
| native_fey-s7@af2677 | 23 | - | - | human | 37% | ok | human 24% | 626.5 |
| dnd-s10@4360a3 | 23 | - | - | human | 64% | ok | human 41% | 1069.1 |
| dnd-s10@af2677 | 23 | - | - | hobgoblin | 29% | ok | hobgoblin 33% | 689.8 |
| dnd-s13@4360a3 | 23 | - | - | human | 56% | ok | human 45% | 1039.0 |
| dnd-s13@af2677 | 23 | - | - | human | 37% | ok | human 32% | 673.0 |
| dnd-s7@4360a3 | 23 | - | - | human | 61% | ok | human 32% | 1061.2 |
| dnd-s7@af2677 | 23 | - | - | hobgoblin | 26% | ok | hobgoblin 27% | 807.1 |
| sm-s10@4360a3 | 22 | - | - | human | 31% | ok | human 21% | 1135.7 |
| sm-s10@af2677 | 22 | - | - | half_orc | 23% | ok | half_orc 18% | 757.9 |
| sm-s13@4360a3 | 22 | - | - | half_orc | 24% | ok | cervid_folk 26% | 1123.8 |
| sm-s13@af2677 | 22 | - | half_orc (never founded) | cervid_folk | 21% | ok | cervid_folk 23% | 738.4 |
| sm-s7@4360a3 | 22 | - | - | half_orc | 29% | ok | half_orc 16% | 1143.7 |
| sm-s7@af2677 | 22 | - | - | human | 27% | ok | half_orc 17% | 893.5 |
| dnd-j1@4360a3 | 23 | - | - | human | 46% | ok | human 19% | 1064.8 |
| dnd-j1@af2677 | 23 | - | - | human | 46% | ok | human 41% | 704.6 |
| dnd-j2@4360a3 | 23 | - | - | human | 56% | ok | human 35% | 1049.1 |
| dnd-j2@af2677 | 23 | - | - | human | 40% | ok | human 32% | 653.7 |
| dnd-j3@4360a3 | 23 | - | - | human | 59% | ok | human 34% | 1103.6 |
| dnd-j3@af2677 | 23 | - | - | halfling | 31% | ok | dragonborn 30% | 672.9 |
| dnd-j4@4360a3 | 23 | - | - | human | 63% | ok | human 42% | 898.2 |
| dnd-j4@af2677 | 23 | - | - | human | 33% | ok | human 34% | 630.9 |
| sm-j1@4360a3 | 22 | - | - | half_orc | 38% | ok | half_orc 29% | 987.6 |
| sm-j1@af2677 | 22 | - | - | halfling | 31% | ok | halfling 15% | 685.6 |
| sm-j2@4360a3 | 22 | - | - | human | 37% | ok | human 28% | 988.0 |
| sm-j2@af2677 | 22 | - | - | human | 32% | ok | human 20% | 703.1 |
| dnd-bugbearx0.5-s7@4360a3 | 23 | - | - | human | 61% | ok | human 32% | 624.6 |
| dnd-bugbearx0.5-s7@af2677 | 23 | - | - | hobgoblin | 26% | ok | hobgoblin 27% | 745.9 |
| dnd-bugbearx2-s7@4360a3 | 23 | - | - | human | 61% | ok | human 32% | 662.5 |
| dnd-bugbearx2-s7@af2677 | 23 | - | - | hobgoblin | 26% | ok | hobgoblin 27% | 792.9 |
| dnd-dwarfx0.5-s7@4360a3 | 23 | - | - | human | 61% | ok | human 32% | 652.5 |
| dnd-dwarfx0.5-s7@af2677 | 23 | - | - | hobgoblin | 27% | ok | hobgoblin 27% | 707.3 |
| dnd-dwarfx2-s7@4360a3 | 23 | - | - | human | 61% | ok | human 32% | 669.8 |
| dnd-dwarfx2-s7@af2677 | 23 | - | - | hobgoblin | 26% | ok | hobgoblin 27% | 748.5 |
| dnd-gnomex0.5-s7@4360a3 | 23 | - | - | human | 60% | ok | human 31% | 666.1 |
| dnd-gnomex0.5-s7@af2677 | 23 | - | - | hobgoblin | 30% | ok | hobgoblin 27% | 771.9 |
| dnd-gnomex2-s7@4360a3 | 23 | - | - | human | 48% | ok | human 25% | 681.5 |
| dnd-gnomex2-s7@af2677 | 23 | - | - | hobgoblin | 24% | ok | hobgoblin 28% | 773.7 |
| dnd-sites1-s10@4360a3 | 23 | - | - | human | 66% | ok | human 38% | 691.1 |
| dnd-sites1-s10@af2677 | 23 | - | - | human | 30% | ok | hobgoblin 40% | 737.7 |
| dnd-sites1-s7@4360a3 | 23 | - | - | human | 42% | ok | hobgoblin 18% | 762.7 |
| dnd-sites1-s7@af2677 | 23 | - | - | hobgoblin | 29% | ok | human 25% | 623.2 |
| dnd-sites3-s10@4360a3 | 23 | - | - | human | 64% | ok | human 38% | 660.9 |
| dnd-sites3-s10@af2677 | 23 | - | - | hobgoblin | 30% | ok | hobgoblin 39% | 710.9 |
| dnd-sites3-s7@4360a3 | 23 | - | - | human | 59% | ok | human 29% | 731.4 |
| dnd-sites3-s7@af2677 | 23 | - | - | hobgoblin | 28% | ok | hobgoblin 23% | 659.3 |
| dnd+1-s10@4360a3 | 24 | - | - | human | 62% | ok | human 39% | 780.4 |
| dnd+1-s10@af2677 | 24 | - | - | hobgoblin | 37% | ok | hobgoblin 35% | 735.3 |
| dnd+1-s7@4360a3 | 24 | - | - | human | 66% | ok | human 40% | 901.4 |
| dnd+1-s7@af2677 | 24 | - | - | hobgoblin | 24% | ok | hobgoblin 21% | 607.5 |
| dnd3-s10@4360a3 | 3 | - | - | human | 98% | FAIL | human 97% | 95.0 |
| dnd3-s10@af2677 | 3 | - | - | human | 79% | ok | human 66% | 58.5 |
| dnd3-s7@4360a3 | 3 | - | - | human | 99% | FAIL | human 98% | 110.9 |
| dnd3-s7@af2677 | 3 | - | - | human | 98% | FAIL | human 98% | 73.7 |
| dnd5-s10@4360a3 | 5 | - | - | human | 72% | ok | human 60% | 101.3 |
| dnd5-s10@af2677 | 5 | - | - | human | 57% | ok | human 62% | 70.0 |
| dnd5-s7@4360a3 | 5 | - | - | human | 60% | ok | human 56% | 117.4 |
| dnd5-s7@af2677 | 5 | - | - | elf | 60% | ok | orc 50% | 82.6 |

| founding arm | runs counted | any fail | crash | a people extinct | one people over 85% |
|---|---|---|---|---|---|
| now | 82 | 4 | 0 | 1 | 3 |

(info-only trees, all_at_once, are not counted.)

## Continental blocs (landmasses of 1+ Mkm² with people)

| run | landmasses | led by a non-human people | non-human majority (>50%) | humans under 50% | distinct leaders | median peoples making 90% | mix distance from the world's (people-weighted) | leaders (share of the landmass's people, largest landmass first) |
|---|---|---|---|---|---|---|---|---|
| all_at_once-s10@4360a3 | 10 | 4 | 2 | 4 | 4 | 2.5 | 0.38 | gnome 53%, human 72%, hobgoblin 34%, dwarf 67%, hobgoblin 46%, human 86% |
| all_at_once-s10@af2677 | 6 | 3 | 1 | 3 | 3 | 3.5 | 0.36 | human 55%, gnome 37%, bugbear 66%, human 56%, gnome 43%, human 88% |
| all_at_once-s7@4360a3 | 10 | 2 | 2 | 3 | 3 | 3 | 0.36 | gnome 66%, human 66%, hobgoblin 68%, human 44%, human 70%, human 85% |
| all_at_once-s7@af2677 | 6 | 2 | 2 | 4 | 2 | 3 | 0.31 | human 40%, human 46%, gnome 51%, human 56%, gnome 54%, human 93% |
| even_six-s10@4360a3 | 10 | 3 | 2 | 3 | 4 | 1 | 0.38 | human 94%, dragonborn 40%, human 54%, elf 96%, human 100%, gnome 86% |
| even_six-s10@af2677 | 6 | 3 | 3 | 3 | 3 | 2 | 0.24 | halfling 61%, gnome 82%, human 100%, halfling 59%, human 51%, human 79% |
| even_six-s7@4360a3 | 10 | 3 | 3 | 3 | 3 | 2 | 0.40 | human 52%, gnome 71%, human 57%, elf 69%, human 100%, gnome 66% |
| even_six-s7@af2677 | 6 | 4 | 3 | 4 | 3 | 1.5 | 0.22 | halfling 42%, human 100%, gnome 93%, halfling 57%, gnome 60%, human 100% |
| five_peoples-s10@4360a3 | 9 | 6 | 4 | 6 | 4 | 2 | 0.26 | gnome 75%, human 55%, gnome 45%, human 97%, aarakocra 65%, gnome 48% |
| five_peoples-s10@af2677 | 6 | 4 | 4 | 4 | 3 | 1.5 | 0.24 | gnome 85%, gnome 61%, human 100%, aarakocra 53%, gnome 95%, human 97% |
| five_peoples-s7@4360a3 | 10 | 4 | 4 | 4 | 3 | 1.5 | 0.35 | gnome 50%, gnome 89%, human 96%, aarakocra 90%, human 100%, gnome 95% |
| five_peoples-s7@af2677 | 6 | 4 | 4 | 4 | 3 | 1 | 0.45 | gnome 84%, human 98%, gnome 97%, aarakocra 95%, gnome 76%, human 100% |
| goblin_world-s10@4360a3 | 9 | 2 | 0 | 2 | 3 | 2 | 0.37 | human 85%, dragonborn 47%, hobgoblin 50%, human 81%, human 89%, human 81% |
| goblin_world-s10@af2677 | 6 | 2 | 1 | 3 | 3 | 3 | 0.46 | hobgoblin 51%, human 64%, human 76%, dragonborn 45%, human 37%, human 91% |
| goblin_world-s7@4360a3 | 10 | 7 | 3 | 8 | 6 | 4 | 0.44 | human 39%, elf 35%, hobgoblin 48%, aarakocra 57%, human 64%, gnome 45% |
| goblin_world-s7@af2677 | 6 | 3 | 2 | 4 | 4 | 2.5 | 0.39 | human 36%, human 56%, bugbear 48%, human 85%, gnome 81%, aarakocra 73% |
| late_humans-s10@4360a3 | 10 | 1 | 0 | 2 | 2 | 1.5 | 0.31 | human 83%, human 64%, hobgoblin 39%, human 99%, human 94%, human 89% |
| late_humans-s10@af2677 | 6 | 5 | 3 | 5 | 5 | 3 | 0.40 | hobgoblin 51%, halfling 48%, orc 87%, hobgoblin 75%, human 61%, dragonborn 47% |
| late_humans-s7@4360a3 | 10 | 1 | 1 | 1 | 2 | 1 | 0.23 | human 91%, human 84%, hobgoblin 56%, human 96%, human 65%, human 90% |
| late_humans-s7@af2677 | 6 | 1 | 1 | 2 | 2 | 2 | 0.31 | human 40%, human 97%, gnome 73%, human 81%, human 73%, human 87% |
| menagerie-s7@4360a3 | 9 | 4 | 1 | 7 | 5 | 5 | 0.49 | human 26%, human 29%, hobgoblin 47%, githyanki 34%, human 80%, harengon 30% |
| menagerie-s7@af2677 | 6 | 6 | 1 | 6 | 5 | 5.5 | 0.46 | dragonborn 21%, owlin 31%, owlin 36%, hadozee 32%, harengon 28%, ogre 64% |
| mountain_stem-s10@4360a3 | 10 | 2 | 0 | 3 | 3 | 2.5 | 0.38 | human 58%, dragonborn 47%, hobgoblin 36%, human 48%, human 87%, human 73% |
| mountain_stem-s10@af2677 | 6 | 3 | 3 | 4 | 3 | 3 | 0.39 | hobgoblin 52%, human 39%, elf 58%, hobgoblin 65%, human 59%, human 56% |
| mountain_stem-s7@4360a3 | 10 | 3 | 1 | 4 | 4 | 2.5 | 0.42 | human 24%, elf 42%, hobgoblin 49%, kobold 65%, human 92%, human 59% |
| mountain_stem-s7@af2677 | 6 | 4 | 3 | 4 | 4 | 2 | 0.44 | hobgoblin 38%, human 88%, gnome 85%, kobold 78%, gnome 77%, human 76% |
| native_fey-s10@4360a3 | 9 | 3 | 1 | 3 | 4 | 2 | 0.40 | human 87%, dragonborn 70%, hobgoblin 31%, kobold 48%, human 77%, human 92% |
| native_fey-s10@af2677 | 6 | 5 | 5 | 5 | 5 | 2.5 | 0.51 | hobgoblin 83%, elf 53%, human 82%, hobgoblin 56%, dragonborn 93%, orc 65% |
| native_fey-s7@4360a3 | 10 | 3 | 2 | 3 | 4 | 1 | 0.37 | human 93%, kenku 49%, hobgoblin 55%, human 81%, dragonborn 94%, human 91% |
| native_fey-s7@af2677 | 6 | 3 | 2 | 3 | 4 | 2 | 0.32 | hobgoblin 33%, human 82%, human 93%, kobold 70%, aarakocra 73%, human 95% |
| dnd-s10@4360a3 | 9 | 2 | 0 | 2 | 3 | 2 | 0.39 | human 84%, dragonborn 46%, hobgoblin 35%, human 59%, human 94%, human 74% |
| dnd-s10@af2677 | 6 | 5 | 4 | 5 | 5 | 3 | 0.49 | hobgoblin 57%, halfling 54%, orc 97%, hobgoblin 95%, dragonborn 42%, human 54% |
| dnd-s13@4360a3 | 10 | 3 | 1 | 3 | 4 | 2 | 0.45 | human 88%, gnome 49%, hobgoblin 34%, kobold 81%, human 71%, human 63% |
| dnd-s13@af2677 | 6 | 5 | 1 | 5 | 5 | 3 | 0.42 | halfling 38%, dragonborn 47%, firbolg 41%, human 82%, gnome 91%, gnome 49% |
| dnd-s7@4360a3 | 10 | 2 | 2 | 4 | 3 | 1.5 | 0.40 | human 46%, human 38%, hobgoblin 54%, human 93%, dragonborn 95%, human 82% |
| dnd-s7@af2677 | 6 | 4 | 2 | 4 | 4 | 2.5 | 0.34 | hobgoblin 35%, human 84%, gnome 87%, kobold 38%, gnome 60%, human 79% |
| sm-s10@4360a3 | 9 | 5 | 3 | 7 | 3 | 3 | 0.39 | human 39%, half_orc 33%, human 54%, half_orc 54%, human 41%, lizardfolk 43% |
| sm-s10@af2677 | 6 | 5 | 3 | 6 | 5 | 3 | 0.28 | human 30%, hobgoblin 52%, gnome 43%, half_orc 32%, halfling 83%, half_orc 76% |
| sm-s13@4360a3 | 9 | 6 | 0 | 6 | 5 | 4 | 0.48 | halfling 38%, cervid_folk 32%, half_orc 35%, half_orc 30%, lizardfolk 48%, human 63% |
| sm-s13@af2677 | 6 | 6 | 4 | 6 | 4 | 2.5 | 0.32 | hobgoblin 23%, lizardfolk 40%, aarakocra 66%, cervid_folk 63%, lizardfolk 75%, aarakocra 66% |
| sm-s7@4360a3 | 10 | 7 | 4 | 8 | 4 | 3.5 | 0.57 | halfling 37%, human 30%, half_orc 39%, half_orc 58%, human 61%, lizardfolk 49% |
| sm-s7@af2677 | 6 | 5 | 3 | 6 | 4 | 3.5 | 0.22 | human 32%, lizardfolk 43%, half_orc 53%, half_orc 29%, half_orc 65%, aarakocra 52% |
| dnd-j1@4360a3 | 9 | 3 | 3 | 5 | 3 | 3 | 0.46 | human 24%, human 46%, hobgoblin 68%, kobold 58%, human 100%, human 61% |
| dnd-j1@af2677 | 6 | 2 | 2 | 3 | 2 | 2 | 0.36 | human 41%, human 86%, gnome 95%, human 90%, gnome 67%, human 88% |
| dnd-j2@4360a3 | 10 | 3 | 1 | 4 | 3 | 2 | 0.39 | human 45%, human 66%, hobgoblin 52%, human 83%, hobgoblin 48%, human 68% |
| dnd-j2@af2677 | 6 | 2 | 2 | 4 | 2 | 2 | 0.39 | human 39%, human 47%, gnome 87%, human 88%, gnome 91%, human 89% |
| dnd-j3@4360a3 | 10 | 2 | 2 | 2 | 3 | 2 | 0.40 | human 72%, elf 55%, hobgoblin 56%, human 83%, human 88%, human 58% |
| dnd-j3@af2677 | 6 | 4 | 2 | 5 | 4 | 3 | 0.42 | halfling 48%, dragonborn 92%, gnome 89%, human 47%, gnome 45%, human 63% |
| dnd-j4@4360a3 | 9 | 1 | 1 | 2 | 2 | 2 | 0.31 | human 60%, human 41%, hobgoblin 50%, human 97%, human 64%, human 85% |
| dnd-j4@af2677 | 6 | 2 | 2 | 4 | 2 | 3 | 0.47 | human 42%, human 50%, gnome 93%, human 77%, gnome 80%, human 76% |
| sm-j1@4360a3 | 10 | 5 | 2 | 7 | 2 | 3 | 0.31 | human 41%, half_orc 49%, human 50%, half_orc 36%, half_orc 34%, half_orc 72% |
| sm-j1@af2677 | 6 | 5 | 1 | 5 | 4 | 3.5 | 0.35 | halfling 45%, human 59%, half_orc 43%, kobold 30%, half_orc 42%, half_orc 56% |
| sm-j2@4360a3 | 9 | 2 | 1 | 4 | 3 | 4 | 0.37 | human 41%, kobold 31%, human 35%, human 57%, human 50%, half_orc 76% |
| sm-j2@af2677 | 6 | 2 | 1 | 3 | 3 | 3 | 0.20 | human 29%, human 64%, half_orc 57%, dragonborn 21%, human 62%, human 51% |
| dnd-bugbearx0.5-s7@4360a3 | 10 | 2 | 2 | 4 | 3 | 1.5 | 0.40 | human 46%, human 38%, hobgoblin 55%, human 93%, dragonborn 95%, human 82% |
| dnd-bugbearx0.5-s7@af2677 | 6 | 4 | 2 | 4 | 4 | 2.5 | 0.35 | hobgoblin 35%, human 84%, gnome 87%, kobold 38%, gnome 60%, human 79% |
| dnd-bugbearx2-s7@4360a3 | 10 | 2 | 2 | 4 | 3 | 1.5 | 0.40 | human 46%, human 38%, hobgoblin 54%, human 93%, dragonborn 95%, human 82% |
| dnd-bugbearx2-s7@af2677 | 6 | 4 | 2 | 4 | 4 | 2.5 | 0.34 | hobgoblin 34%, human 84%, gnome 87%, kobold 38%, gnome 60%, human 79% |
| dnd-dwarfx0.5-s7@4360a3 | 10 | 2 | 2 | 4 | 3 | 1.5 | 0.40 | human 46%, human 38%, hobgoblin 55%, human 93%, dragonborn 95%, human 82% |
| dnd-dwarfx0.5-s7@af2677 | 6 | 4 | 2 | 4 | 4 | 2.5 | 0.35 | hobgoblin 35%, human 84%, gnome 87%, kobold 38%, gnome 60%, human 79% |
| dnd-dwarfx2-s7@4360a3 | 10 | 2 | 2 | 4 | 3 | 1.5 | 0.41 | human 46%, human 38%, hobgoblin 53%, human 93%, dragonborn 95%, human 82% |
| dnd-dwarfx2-s7@af2677 | 6 | 4 | 2 | 4 | 4 | 2.5 | 0.34 | hobgoblin 34%, human 84%, gnome 87%, kobold 38%, gnome 60%, human 79% |
| dnd-gnomex0.5-s7@4360a3 | 10 | 2 | 1 | 2 | 3 | 2.5 | 0.35 | human 70%, elf 40%, hobgoblin 55%, human 77%, human 77%, human 79% |
| dnd-gnomex0.5-s7@af2677 | 6 | 4 | 1 | 4 | 4 | 3 | 0.28 | hobgoblin 36%, human 51%, gnome 79%, kobold 41%, gnome 38%, human 84% |
| dnd-gnomex2-s7@4360a3 | 10 | 2 | 1 | 3 | 3 | 2 | 0.47 | human 44%, elf 44%, hobgoblin 56%, human 78%, human 65%, human 63% |
| dnd-gnomex2-s7@af2677 | 6 | 5 | 2 | 5 | 5 | 3 | 0.40 | hobgoblin 35%, aarakocra 47%, gnome 92%, kobold 41%, gnome 73%, human 77% |
| dnd-sites1-s10@4360a3 | 9 | 2 | 1 | 2 | 3 | 2 | 0.40 | human 85%, dragonborn 77%, hobgoblin 37%, human 91%, human 94%, human 81% |
| dnd-sites1-s10@af2677 | 6 | 4 | 3 | 5 | 4 | 2.5 | 0.50 | hobgoblin 81%, halfling 49%, orc 76%, hobgoblin 72%, human 37%, human 56% |
| dnd-sites1-s7@4360a3 | 10 | 4 | 4 | 4 | 4 | 2 | 0.51 | hobgoblin 62%, elf 60%, hobgoblin 56%, human 75%, human 74%, lizardfolk 63% |
| dnd-sites1-s7@af2677 | 6 | 4 | 3 | 4 | 5 | 2 | 0.31 | hobgoblin 38%, human 96%, human 100%, kobold 62%, orc 70%, aarakocra 81% |
| dnd-sites3-s10@4360a3 | 9 | 2 | 1 | 3 | 3 | 2 | 0.40 | human 85%, dragonborn 70%, hobgoblin 34%, human 48%, human 93%, human 88% |
| dnd-sites3-s10@af2677 | 6 | 6 | 5 | 6 | 4 | 3 | 0.56 | hobgoblin 73%, halfling 61%, orc 91%, hobgoblin 96%, dragonborn 28%, dragonborn 56% |
| dnd-sites3-s7@4360a3 | 10 | 2 | 1 | 2 | 3 | 2 | 0.38 | human 70%, elf 43%, hobgoblin 58%, human 81%, human 64%, human 91% |
| dnd-sites3-s7@af2677 | 6 | 4 | 3 | 4 | 5 | 3 | 0.29 | hobgoblin 36%, aarakocra 75%, human 100%, kobold 61%, gnome 70%, human 83% |
| dnd+1-s10@4360a3 | 10 | 2 | 0 | 3 | 3 | 2 | 0.43 | human 88%, dragonborn 47%, hobgoblin 31%, human 48%, human 99%, human 78% |
| dnd+1-s10@af2677 | 6 | 4 | 3 | 4 | 4 | 3 | 0.43 | hobgoblin 60%, elf 36%, orc 82%, hobgoblin 77%, human 61%, human 69% |
| dnd+1-s7@4360a3 | 9 | 2 | 1 | 2 | 3 | 3 | 0.33 | human 90%, human 51%, hobgoblin 37%, kobold 55%, human 79%, human 80% |
| dnd+1-s7@af2677 | 6 | 5 | 3 | 5 | 5 | 3 | 0.37 | hobgoblin 36%, aarakocra 41%, gnome 86%, kobold 67%, gnome 68%, human 78% |
| dnd3-s10@4360a3 | 10 | 0 | 0 | 0 | 1 | 1 | 0.02 | human 93%, human 100%, human 98%, human 100%, human 100%, human 98% |
| dnd3-s10@af2677 | 5 | 0 | 0 | 0 | 1 | 1 | 0.17 | human 64%, human 100%, human 100%, human 100%, human 98% |
| dnd3-s7@4360a3 | 10 | 0 | 0 | 0 | 1 | 1 | 0.02 | human 100%, human 100%, human 95%, human 100%, human 100%, human 100% |
| dnd3-s7@af2677 | 6 | 0 | 0 | 0 | 1 | 1 | 0.03 | human 100%, human 100%, human 100%, human 91%, human 100%, human 100% |
| dnd5-s10@4360a3 | 10 | 3 | 3 | 3 | 2 | 1 | 0.29 | elf 82%, human 68%, elf 64%, human 100%, human 94%, human 99% |
| dnd5-s10@af2677 | 6 | 1 | 1 | 1 | 2 | 2 | 0.17 | human 53%, human 50%, elf 63%, human 76%, human 52%, human 69% |
| dnd5-s7@4360a3 | 10 | 3 | 3 | 3 | 2 | 1 | 0.33 | elf 82%, human 53%, elf 59%, human 66%, human 99%, human 91% |
| dnd5-s7@af2677 | 6 | 6 | 6 | 6 | 2 | 1 | 0.22 | elf 54%, elf 100%, elf 100%, orc 99%, elf 100%, elf 96% |

## Share spread, dnd, founding now (base + jitter: 14 runs)

(swing x pooled over both worlds; the worst swing within one world and one family, seeds or jitter, PW-1207, decides 'brittle': the pooled one also holds the two worlds' different geography)

| people | share min | median | max | swing x | worst x in one world and family | led min | led median | led max | dead in | brittle |
|---|---|---|---|---|---|---|---|---|---|---|
| human | 12% | 46% | 64% | 5.39 | 3.9 | 16% | 33% | 45% | 0/14 |  |
| hobgoblin | 0.13% | 9.1% | 29% | 223 | 209 | 0.081% | 8.8% | 33% | 0/14 | BRITTLE |
| elf | 5.1% | 8.6% | 12% | 2.39 | 2.39 | 3% | 8.7% | 12% | 0/14 |  |
| halfling | 0.042% | 8.5% | 31% | 742 | 742 | 0% | 2.2% | 15% | 0/14 | BRITTLE |
| gnome | 0.69% | 7.2% | 31% | 44.9 | 9.93 | 0.31% | 3.3% | 12% | 0/14 |  |
| dragonborn | 2% | 4.3% | 19% | 9.6 | 4.53 | 1.6% | 7.9% | 30% | 0/14 |  |
| kobold | 0.45% | 2.8% | 11% | 25.4 | 25.4 | 0.42% | 3.1% | 16% | 0/14 | BRITTLE |
| orc | 0.78% | 1.3% | 4.6% | 5.88 | 4.57 | 0.36% | 2.4% | 8.7% | 0/14 |  |
| dwarf | 0.3% | 0.93% | 4.7% | 15.6 | 15.6 | 0.23% | 0.71% | 3% | 0/14 | BRITTLE |
| kenku | 0.093% | 0.75% | 1.3% | 13.8 | 12.8 | 0.71% | 4.4% | 12% | 0/14 | BRITTLE |
| triton | 0.28% | 0.52% | 0.72% | 2.61 | 2.61 | 0.16% | 0.57% | 1.5% | 0/14 |  |
| leonin | 0.0072% | 0.41% | 1% | 103 | 69.6 | 0% | 0% | 3.4% | 0/14 | BRITTLE |
| aarakocra | 0.1% | 0.37% | 0.64% | 6.08 | 4.24 | 0.65% | 5.4% | 13% | 0/14 |  |
| lizardfolk | 0.097% | 0.35% | 1.2% | 11.9 | 8.98 | 0.0081% | 3% | 6.4% | 0/14 |  |
| tabaxi | 0.0049% | 0.3% | 1.1% | 108 | 1.76 | 0% | 0.35% | 3.4% | 0/14 |  |
| goblin | 0.0053% | 0.17% | 0.55% | 54.6 | 46 | 0% | 0.13% | 0.76% | 0/14 | BRITTLE |
| tortle | 0.033% | 0.14% | 0.18% | 5.38 | 5.31 | 0% | 0.16% | 1% | 0/14 |  |
| bugbear | 0.00032% | 0.095% | 1.1% | 107 | 32.5 | 0% | 0% | 0.89% | 0/14 | BRITTLE |
| sea_elf | 0.029% | 0.068% | 0.091% | 3.14 | 2.68 | 0.0081% | 0.075% | 0.23% | 0/14 |  |
| firbolg | 0.0012% | 0.022% | 0.31% | 31.1 | 31.1 | 0% | 0.086% | 4.6% | 0/14 | BRITTLE |
| goliath | 0.0059% | 0.019% | 0.22% | 22.1 | 22.1 | 0% | 0.22% | 4.1% | 0/14 | BRITTLE |
| drow | 0.0019% | 0.015% | 0.076% | 7.58 | 7.58 | 0% | 0.16% | 0.46% | 0/14 |  |

## Share spread, seven_meals, founding now (base + jitter: 10 runs)

(swing x pooled over both worlds; the worst swing within one world and one family, seeds or jitter, PW-1207, decides 'brittle': the pooled one also holds the two worlds' different geography)

| people | share min | median | max | swing x | worst x in one world and family | led min | led median | led max | dead in | brittle |
|---|---|---|---|---|---|---|---|---|---|---|
| human | 9.8% | 25% | 37% | 3.8 | 2.78 | 4.7% | 16% | 28% | 0/10 |  |
| half_orc | 0% | 24% | 38% | 3.84e+03 | 2.41e+03 | 0% | 16% | 29% | 1/10 | BRITTLE |
| halfling | 1.1% | 9.8% | 31% | 28.5 | 5.61 | 0.043% | 4.4% | 15% | 0/10 |  |
| hobgoblin | 3.4% | 5.8% | 16% | 4.63 | 2.47 | 0.8% | 2.4% | 11% | 0/10 |  |
| dragonborn | 3% | 5.2% | 9% | 3.02 | 1.41 | 1.4% | 4% | 6.3% | 0/10 |  |
| lizardfolk | 3.7% | 4.7% | 13% | 3.65 | 3.49 | 9.3% | 14% | 18% | 0/10 |  |
| cervid_folk | 2% | 3.8% | 21% | 11 | 6.79 | 4.7% | 7.2% | 26% | 0/10 |  |
| goblin | 0.49% | 3.1% | 6.1% | 12.5 | 6.32 | 0.51% | 2.5% | 5.4% | 0/10 |  |
| antelope_folk | 1.4% | 2.2% | 7.5% | 5.17 | 4.35 | 2.3% | 5.2% | 7.6% | 0/10 |  |
| kobold | 0.49% | 2.2% | 5.9% | 11.9 | 7.25 | 0.57% | 3.1% | 12% | 0/10 |  |
| aarakocra | 1.2% | 1.6% | 4.2% | 3.5 | 3.5 | 4.6% | 9.9% | 17% | 0/10 |  |
| tabaxi | 0.38% | 1.1% | 3% | 7.92 | 7.92 | 0% | 1.3% | 10% | 0/10 |  |
| orc | 0.27% | 0.73% | 2.6% | 9.49 | 3.52 | 0.13% | 0.54% | 3.4% | 0/10 |  |
| merfolk | 0.32% | 0.56% | 1.6% | 5.01 | 5.01 | 1.4% | 2.3% | 2.9% | 0/10 |  |
| gnome | 0.11% | 0.49% | 4.8% | 42.2 | 16.9 | 0.0087% | 1.1% | 3.7% | 0/10 | BRITTLE |
| elf | 0.14% | 0.4% | 0.69% | 4.79 | 2.87 | 0.0079% | 0.22% | 2.9% | 0/10 |  |
| tortle | 0.17% | 0.34% | 0.79% | 4.73 | 4.73 | 0% | 0.088% | 0.42% | 0/10 |  |
| bugbear | 0.018% | 0.33% | 0.73% | 40.3 | 18.2 | 0% | 0% | 0.12% | 0/10 | BRITTLE |
| deep_folk | 0.17% | 0.31% | 0.82% | 4.72 | 2.93 | 0.16% | 0.63% | 1.4% | 0/10 |  |
| leonin | 0.044% | 0.25% | 1.1% | 24.5 | 7.16 | 0% | 0% | 4% | 0/10 |  |
| dwarf | 0.06% | 0.19% | 1.1% | 18.1 | 10.1 | 0.079% | 0.38% | 1.5% | 0/10 | BRITTLE |
| goliath | 0.0022% | 0.018% | 0.17% | 17.4 | 17.4 | 0% | 0.93% | 4.7% | 0/10 | BRITTLE |

## Portals (dnd): arrivals' share, off vs sites

| world, seed | portals | elf | gnome | triton |
|---|---|---|---|---|
| 4360a3 s7 | off | 8.2% | 3.7% | 0.68% |
| 4360a3 s7 | 1 | 6.5% | 1.3% | 0.36% |
| 4360a3 s7 | 3 | 8.8% | 2.8% | 0.48% |
| 4360a3 s10 | off | 8% | 1.1% | 0.6% |
| 4360a3 s10 | 1 | 3.4% | 0.25% | 0.4% |
| 4360a3 s10 | 3 | 4.7% | 0.26% | 0.4% |
| 4360a3 s13 | off | 8% | 10% | 0.51% |
| af2677 s7 | off | 6% | 12% | 0.72% |
| af2677 s7 | 1 | 3.3% | 1.3% | 0.32% |
| af2677 s7 | 3 | 6.4% | 9.5% | 0.31% |
| af2677 s10 | off | 9.5% | 3% | 0.62% |
| af2677 s10 | 1 | 2.8% | 0.18% | 0.22% |
| af2677 s10 | 3 | 6.4% | 1.6% | 0.26% |
| af2677 s13 | off | 10% | 14% | 0.28% |

## Authored trees (median over worlds and seeds; per arm: top people and share, peoples under 0.1%, dead)

| tree | rationale | arm | runs | top | top share | median people >= 1% | under 0.1% | dead |
|---|---|---|---|---|---|---|---|---|
| all_at_once (info only) | All at once: every dnd people (and dragon and giant kind) is placed at the same moment, 60 | now | 4 | human | 49% | 7 | aarakocra, drow, firbolg, goblin, goliath, tortle | - |
| even_six | Six peoples only (humans, elves, gnomes, dragonborn, halflings, tieflings), no dragons, gi | now | 4 | human | 45% | 5 | - | - |
| five_peoples | Only five peoples from four roots: humans, lizardfolk, goblins, aarakocra and the gnomes ( | now | 4 | human | 53% | 4 | - | - |
| goblin_world | A goblinoid-heavy world: the goblinoids split early and widely (goblins, hobgoblins, bugbe | now | 4 | human | 36% | 9.5 | drow, firbolg, goliath, sea_elf | - |
| late_humans | The humans are latecomers: they arrive from outside the world 40 kyr ago into a world the  | now | 4 | human | 65% | 8 | drow, firbolg, goliath, sea_elf | - |
| menagerie | The menagerie: dnd plus 29 more D&D kinds on plausible stems (52 peoples): does the histor | now | 2 | human | 16% | 17.5 | drow, firbolg, loxodon, minotaur, quaggoth, sea_elf, shadar_kai | - |
| mountain_stem | Dwarves split early (1.2 Myr) from a mountain-folk stem that leaves the hominids at 1.5 My | now | 4 | human | 42% | 9 | drow, firbolg, goliath, sea_elf | - |
| native_fey | Elves and gnomes are native: elves split from the hominids early, gnomes from the archaic  | now | 4 | human | 49% | 10.5 | drow, firbolg, goliath, sea_elf | - |

### All at once (info only) beside dnd (median share, range arm)

| people | dnd | all at once |
|---|---|---|
| human | 46% | 49% |
| hobgoblin | 12% | 9.1% |
| halfling | 9.2% | 2.2% |
| elf | 8.1% | 8.4% |
| gnome | 7.1% | 16% |
| dragonborn | 4.7% | 1.7% |
| kobold | 2.8% | 1.5% |
| orc | 1.3% | 0.69% |
| dwarf | 1.2% | 4.5% |
| kenku | 0.74% | 0.29% |
| leonin | 0.67% | 0.53% |
| triton | 0.61% | 0.72% |
| lizardfolk | 0.33% | 0.14% |
| tabaxi | 0.3% | 0.44% |
| aarakocra | 0.29% | 0.099% |
| goblin | 0.2% | 0.049% |
| tortle | 0.14% | 0.047% |
| bugbear | 0.12% | 0.2% |
| firbolg | 0.08% | 0.0014% |
| sea_elf | 0.067% | 0.73% |
| goliath | 0.066% | 0.0089% |
| drow | 0.0086% | 0.025% |

## Knob response (density x0.5 / x1 / x2, same world and seed)

| people | world, seed | share x0.5 | x1 | x2 | led x0.5 | x1 | x2 | area x0.5 | x1 | x2 | monotone |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dwarf (mainline) | 4360a3 s7 | 0.77% | 1% | 1.5% | 0.66% | 0.68% | 0.7% | 1.12 | 1.12 | 1.12 | ok |
| dwarf (mainline) | af2677 s7 | 1.7% | 2.8% | 4.9% | 1.1% | 1.1% | 1.1% | 1.63 | 1.63 | 1.63 | ok |
| bugbear (minor) | 4360a3 s7 | 0.033% | 0.066% | 0.13% | 0% | 0% | 0% | 2.69 | 2.69 | 2.69 | ok |
| bugbear (minor) | af2677 s7 | 0.54% | 1.1% | 2.1% | 0% | 0.0081% | 0.17% | 21.1 | 21.1 | 21.1 | ok |
| gnome (late arrival) | 4360a3 s7 | 2.5% | 3.7% | 10% | 2.1% | 2.2% | 3.1% | 4.02 | 3.7 | 4.1 | ok |
| gnome (late arrival) | af2677 s7 | 6.3% | 12% | 22% | 3.3% | 4% | 4.2% | 5.99 | 6.34 | 6.41 | ok |

## Founding range and stem inheritance (median over runs, Mkm2: founded / inherited at the stem's end / present)

| people | now |
|---|---|
| aarakocra | 0.299 / 0 / 17.7 |
| antelope_folk | 0.442 / 0 / 36.4 |
| bugbear | 0.374 / 0 / 5.98 |
| bullywug | 0.368 / 0 / 3.65 |
| centaur | 0.217 / 0 / 12.8 |
| cervid_folk | 0.367 / 0 / 27.1 |
| deep_folk | 0.1 / 0 / 4.13 |
| dragonborn | 0.461 / 0 / 12.9 |
| drow | 0.149 / 0 / 0.324 |
| duergar | 0.461 / 0 / 0.516 |
| dwarf | 0.218 / 0 / 1.58 |
| eladrin | 0.455 / 0 / 8.21 |
| elf | 2.1 / 0 / 15.8 |
| firbolg | 0.162 / 0 / 1.33 |
| giff | 0.28 / 0 / 11.4 |
| githyanki | 2.78 / 0 / 29.4 |
| githzerai | 1.34 / 0 / 1.46 |
| gnoll | 0.237 / 0 / 2.39 |
| gnome | 0.859 / 0 / 3.7 |
| goblin | 0.125 / 0 / 0.897 |
| goliath | 0.249 / 0 / 3.83 |
| grimlock | 0.236 / 0 / 2.91 |
| grung | 0.442 / 0 / 3.52 |
| hadozee | 0.131 / 0 / 24.9 |
| half_orc | 0.174 / 0 / 39.2 |
| halfling | 0.429 / 0 / 5.27 |
| harengon | 2.65 / 0 / 19.9 |
| hobgoblin | 0.386 / 0 / 26.5 |
| human | 0.436 / 0 / 59 |
| kenku | 0.324 / 0 / 17.6 |
| kobold | 0.374 / 0 / 3.29 |
| kuo_toa | 0.0495 / 0 / 1.2 |
| leonin | 0.374 / 0 / 14.1 |
| lizardfolk | 0.318 / 0 / 13.4 |
| locathah | 0.0435 / 0 / 0.828 |
| loxodon | 0.155 / 0 / 0.268 |
| merfolk | 0.056 / 0 / 3.24 |
| minotaur | 0.292 / 0 / 2.32 |
| myconid | 0.436 / 0 / 1.99 |
| ogre | 0.237 / 0 / 13.4 |
| orc | 0.349 / 0 / 16.4 |
| owlin | 0.38 / 0 / 17.5 |
| pixie | 2.32 / 0 / 23.9 |
| plasmoid | 2.02 / 0 / 2.81 |
| quaggoth | 0.336 / 0 / 0.367 |
| sahuagin | 0.0495 / 0 / 4.26 |
| satyr | 3.07 / 0 / 7.99 |
| sea_elf | 0.087 / 0 / 0.99 |
| shadar_kai | 0.168 / 0 / 0.149 |
| shifter | 0.392 / 0 / 2.39 |
| svirfneblin | 0.423 / 0 / 0.442 |
| tabaxi | 0.374 / 0 / 9.13 |
| thri_kreen | 0.461 / 0 / 11.9 |
| tortle | 0.1 / 0 / 4.79 |
| triton | 0.336 / 0 / 3.87 |
| troglodyte | 0.461 / 0 / 0 |
| yuan_ti | 0.206 / 0 / 9.61 |
