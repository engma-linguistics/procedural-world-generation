# Tech catalogue brief (shared by the seven catalogue agents)

Project: procgen_world (repo /home/daniel/personal/repos/procedural-world-generation, READ-ONLY for you). It simulates fantasy peoples
(D&D-like kinds: humans, elves, dwarves, gnomes, orcs, goblins, kobolds...) on generated planets and gives them a tech tree whose timing
leans on the real-world (Earth) archaeological record. The owner wants the tree fleshed out with "a shitton of important technologies",
one agent per tech type, each with the best-knowledge date it first appeared. A later agent will source-hunt, so your job is breadth
and honest dates, not citations you have verified.

Read first: planet/lineages/samples/techtree.toml (its header explains the fields; ~120 techs exist already, reuse their ids and
`needs` where your techs depend on them) and skim planet/lineages/techtree.py's docstring.

Scope: from the first stone tools (~3.3 Myr) up to about 1700 CE (pre-industrial). Mark anything after 1500 CE with late = true.
Real-world techs only (no magic). Aim for 40-80 techs in your group; include the ones that matter to everyday life, food and
cooking (the project's end goal is a culinary ethnography of each people: what they grow, herd, cook, preserve, eat), not only the
famous firsts. Include intermediate steps (e.g. not just "iron" but bloomery, quench-hardening, steel by carburising).

Write ONE file: /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/techcat/<GROUP>.toml
Each tech as a [[tech]] table:

  id = "snake_case"            # reuse an existing techtree.toml id if it is the same tech (then add exists = true)
  name = "Plain name"
  group = "<GROUP>"
  track = "..."                # one of the existing tracks: communication fire tools food shelter travel social
  domains = ["..."]            # one or more of: war food craft build move know ritual trade
  needs = ["id", ...]          # prerequisite techs (ids from any group or the existing file; best guess is fine)
  env = ["..."]                # land goods it needs, if obvious (e.g. ore, clay, salt, timber, grass, wetland); free text ok
  earliest_kyr = 0.0           # first known appearance anywhere, kyr before present (1 kyr = 1000 years; 1500 CE = 0.5)
  origins = [ {where = "Levant", kyr = 11.5}, ... ]   # independent inventions you know of, each with its date (this sets the
                               # "band" in which the tech tends to appear once possible); one entry if single-origin/diffused
  spread_note = "..."          # one line: how it spread (diffusion, independent reinvention, slow/fast)
  confidence = "high" | "medium" | "low"   # your confidence in earliest_kyr
  source = "Author Year, short title (best knowledge, unverified)"   # what you believe the standard reference is; ALWAYS append
                               # "(unverified)" — never invent a DOI, page number or journal you are not sure of; "none known" is fine
  late = true                  # only if after 1500 CE
  note = "..."                 # optional, one line

Rules: never present a remembered citation as verified; dates are best knowledge and should say "c." ranges in note if contested.
Don't edit the repo. Don't read the owner's personal files. No web access is needed (you may use it to sanity-check a date, but
don't spend long). When done, reply with: the file path, the number of techs, and the 5 dates you are least sure of.
