# Source-hunt brief: one agent per catalogue group

You are verifying a best-knowledge tech catalogue for procgen_world. The repo is read-only for you:
/home/daniel/personal/repos/procedural-world-generation/docs/references/tech-catalogue/<GROUP>.toml
Read its README.md and BRIEF.md first.

Goal: replace remembered dates and sources with ones you have actually read online. Use web search and open-access pages: journal pages, PMC, museum and university pages, and well-sourced reviews. Wikipedia is acceptable only to find the primary or review reference. Then cite that reference, and only if its page or abstract confirms the date.

## Priority order (you will not get through everything; work down this list)
1. Rows with confidence "low", plus the five rows the cataloguer flagged.
2. Rows marked `exists = true`. These are the tree's current anchors.
3. Food-, cooking- and herding-related rows in any group. The project's end goal is food.
4. Rows with several `origins`, for the band: confirm each origin's date.
5. Everything else.
Budget: about 80 searches or fetches. Stop then, and report what you covered.

## Output
Write /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/techcat/hunt/<GROUP>.toml as a copy of the group file. Change only the rows you checked, by adding:
  verified = true | false                  # false = you looked and could not confirm, or the evidence disagrees
  earliest_kyr_checked = <number>          # what the source supports, if different
  origins_checked = [ {where=..., kyr=...}, ... ]   # only if changed
  source_checked = "Authors Year. Title. Venue. DOI/URL. (what it says, e.g. 'abstract: 9.5-9 ka cal BP')"
  hunt_note = "one line: what changed and why, or why it is contested"
Keep the original fields untouched, so a diff shows the changes.

## Rules
- NEVER write a citation you did not see online in this session. If you can't confirm one, set verified = false and say so.
- Dates are kyr before present (1 kyr = 1000 years; 2000 CE = 0). Convert BCE/CE with care. Calibrated BP is close enough to kyr before present.
- Don't edit the repo. Don't read the owner's personal files. Don't download large files (keep each under 20 MB).
- When done, reply with:
  - the file path;
  - the rows checked, verified and refuted;
  - the 10 biggest date changes;
  - any tech you think is wrongly included or missing.
