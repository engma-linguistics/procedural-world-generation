# Civilization work that can start now: scout (2026-10-29)

## Short answer, with one correction
Yes. There is real culture work that will not collide with lane 45b. But the owner's "the last ~10 kyr is free" holds only for **passes that read a finished peoples run**. It does not hold for **anything that changes how the history steps through time**. Lane 45b is changing two things:
- how many people live in each cell (density from productivity, PW-974/PW-833);
- how the land's food surplus is split between dragons, hunters and herders today (PW-977 stage 2).

Both are exactly what the last 10 kyr runs on. So the history zoom (PW-908), ice-age ranges (PW-902) and cultures fracturing inside the simulation (PW-670) must wait for 45b. Output-only passes, the pattern of `contacts.py` and `brief.py`, can start today.

Facts that shape the candidates:
- A peoples run stores, for each frame, the people that leads each cell (`peoples_whole`) plus the top two by heads (`mix_lead`, `mix_second`). It does not store each people's full presence.
- Frames come every 0.5 kyr back to ~30 kyr ago: 41 frames in the last 20 kyr on run b69f51.
- A fresh L7 peoples run took 387 s on one core (b69f51).
- A 1.8 s read-only probe on b69f51 found humans in 6–12 separate patches of 300+ cells (20 kyr ago to now), orcs in 1–4: the raw material for "peoples splitting by area".
- No settlements exist at globe scale. `zoom_peoples.py` places villages only inside zooms. `humanuse.py` already gives harbours, navigable rivers, passes, fertile land and fresh water.
- culinary-dnd's roster is cultures tied to regions, not species:
  - humans-grain-belt, humans-jangwa and humans-forager;
  - the Anja and Arha orcs;
  - "tieflings-infernal: every metropolis" and "kenku: metropolitan docksides".
  The book ends in a city chapter of quarters and diaspora.

---

## 1. Demes v0: a people's range cut into regional populations, with a dated family tree (TOP PICK)
**In plain words:** today a people is one smear over its whole range, so humans on three continents count as a single community. This pass takes a finished peoples run and cuts each people's land into regional populations wherever sea, mountains, deserts or sheer distance separate them. It then follows each population through time: when it split off, when it merged with another, who it touched. Those regional populations are the natural seed of "different cultures arising in an area". The owner has already said cultures are probably these more than species.

- **Viewer:**
  - a globe layer, "regional populations", that changes as you scrub time: humans on the eastern landmass get one colour, those on the island chain another, and a long coast shades into a chain of neighbours;
  - in the workbench's Tree & timeline, a third view option beside "species + cultures" and "species only" that draws each people's population tree. (partly PW-841).
- **Tickets:** PW-981 (both acceptance items). It is the foundation of PW-856's culture unit and the demo PW-986. It gives PW-670 a light, output-only first form, and gives PW-906 (forgotten origins) arrival dates.
- **Files:**
  - new `planet/lineages/demes.py`;
  - reuses `crossing.sea_gap`, `spread.nearest_label`, `spread.graph_dist` and `grid.components`;
  - a `planet demes RUN` command;
  - sidecar `runs/<id>/demes.json` plus `layers/demes.bin`;
  - `viewer/index.html` (one layer) and `viewer/lineages.html` (tree view).
- **Collision with 45b:** none. It only reads stored layers. A later hook in `history/frame.py` (not a 45b file) could store full presence.
- **CPU:** seconds per run on existing runs (b69f51, 6b5d0e). Add 2–3 fresh peoples runs at ~6.5 min on one core each to check across worlds. No planet runs.
- **Effort:** m (the ticket's own estimate).
- **Caveat:** peoples that rarely lead a cell are hard to see (dwarves lead 57 cells on b69f51); v0 also counts the second people by heads.
- **Culinary payoff:** it turns "where humans are found" into "the grain-belt humans, the savanna humans". That is the book's unit, and the brief can key on it (PW-728 "per people" becomes per population). No linguistics: populations are only located and dated.

## 2. Settlements and cities v0: who lives in the towns, and minority quarters
**In plain words:** put market towns and a few big cities on the globe where people are dense and the site is good: a harbour, a navigable river, a pass, fertile land, fresh water. Then work out who lives in each one. Villages are mostly one species, 50–80% or more. Big cities are mixed, with quarters for minorities. That includes the goblins or kobolds who are both a distrusted minority in the cities and a wild people in the caves outside.

- **Viewer:**
  - town and city dots on the globe, sized by population;
  - hovering a city shows "dragonborn 62%, humans 21%, a kenku dockside quarter, an infernal-tiefling quarter";
- **Tickets:** PW-856 ("predominant species per settlement, mixing in cities"), PW-889 (the owner's 10-29 "two things at once", as an urban-minority group beside the wild range), PW-910 (realistic vs fantasy-neat mixing setting), PW-758 (culture-only groups).
- **Files:**
  - new `planet/lineages/settlements.py`, which reads the world's `humanuse` layers, the run's composition layers and `compose.cohabitation`;
  - a settlements block in `brief.py`;
  - globe markers in `viewer/index.html`;
  - a `[meta]` mixing-preset key in `spec.py`.
- **Collision with 45b:** no shared files. It does read people density, which 45b is redefining, so city sizes would move once 45b merges. Do the design and siting now, and calibrate sizes after the merge.
- **CPU:** seconds per run; the same few peoples runs.
- **Effort:** m–l.
- **Culinary payoff:** the biggest single one. It covers the metropolitan chapter, quarters, the kenku docksides and the infernal tieflings in every metropolis. 

## 3. Name stacks without a language: what each people calls itself and its neighbours, and why
**In plain words:** many peoples today just call the others "foreigners". This gives each people a self-name pattern, such as "the real people", "people of the river" or "the herders". It also gives each neighbour a name with its reason: "named after the first group they met", "the ones from the west", "the ones who conquered us". These are meanings only, in English. The actual words wait for the joint language project.

- **Viewer:** the workbench's Peoples tab and each brief show a small name table per people. Each row has the pattern, the English gloss and the reason ("met first on the eastern coast ~9 kyr ago").
- **Tickets:** PW-972 (owner-created; the acceptance bar is that under a third of rows read plain "foreigners"). It closes PW-856's "exonyms too narrow" note and uses the owner's ethnonym taxonomy doc.
- **Files:** `reputation.py` and `brief.py`. It reads the stored `meta.contacts` (pairs, first-meeting dates, incursions with direction) and the groups. Rivers and land names come from the world's hydrology and highlights.
- **Collision with 45b:** none.
- **CPU:** none beyond re-reading stored runs.
- **Effort:** m.
- **Language ruling:** respected; glosses only, no words, sapient peoples only. Better after #1 ("named after the population met first").
- **Culinary payoff:** the book names its peoples and its neighbours' slurs.

## 4. Folk memory and attitudes v0: "they have always lived here", grudges that fade
**In plain words:**
- **Forgotten origins:** after about 100 years nobody remembers a people arrived, and after about 300 years "they have always been here", while the true dates stay underneath.
- **Attitudes:** each people starts from a temperament (orcs aggressive, elves insular), and that is shifted by history. Conquest breeds grudges, and intermarriage and long contact soften them.

All of this is read from the contact and incursion record that already exists.

- **Viewer:** an attitude row per neighbour in the brief and Peoples tab; stories read "always here (truly ~415 yr)".
- **Tickets:** PW-906, PW-904 (light v0), and the leftover `resented` valence from PW-756.
- **Files:** `reputation.py`, `brief.py` and `spec.py`, where temperament fields go into the preset.
- **Collision with 45b:** none.
- **CPU:** none.
- **Effort:** s for PW-906, m for PW-904.
- **Judgement call:** starting temperaments go to the owner as a needs-decision ticket.
- **Culinary payoff:** who refuses whose food, and the class and grudge reactions the master reference is full of (the reception of chilies, the tieflings' split by class).

## 5. Polities v0: first states, drawn on top of 1 and 2 (start after them)
**In plain words:** a city's reach over the populations around it is the first, crude state. Where one population's cities dominate others, that is a ruled-by relationship. Enough for the owner's two empires (antelope-kin today, cervid-kin fallen) and a "ruled by" line in the brief.

- **Tickets:** PW-785, PW-756 (polity kind), and the first slice of PW-661/PW-676 (unifying pressure as a merge over states).
- **Files:** `settlements.py`, `reputation.py` and `brief.py`.
- **Collision with 45b:** none.
- **CPU:** none.
- **Effort:** l.
- **Ordering:** after #1 and #2, and probably after 45b merges, because polity size depends on density.

## Not now
- **PW-908 (history zoom at 25-year steps from each region's farming onset):** it needs new stepping code alongside `history/model.py`, a 45b file, and the density 45b is building. It is next after 45b, not beside it.
- **PW-902 (peoples ranges follow the ice-age climate):** it rewrites dispersal and habitat inputs inside the history.
- **PW-670 (fracture inside the simulation):** it changes `history/groups.py` and dispersal. #1 gives the output-only first version instead.

## Order
1, then 3 (the same lane, as follow-on), with 2 in a second lane or right after 1. Then 4, then 5 after 45b merges. None of 1–4 touches a 45b file; all need minutes of CPU, not sim hours.
