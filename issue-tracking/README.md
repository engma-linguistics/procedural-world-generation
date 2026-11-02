# Issue tracking

One markdown file per ticket in `tickets/`, draft tickets from subagents in `inbox/`, and a small stdlib-only CLI, `board.py`. The coordinating Claude session creates and reads most tickets; Daniel reads the ones he's pointed at, mostly `needs-decision`.

## When to open a ticket

Open one for anything you saw and didn't finish, that someone should come back to:
- a bug or artifact in the model, the zoom or the viewer;
- a mismatch with Earth that is worth fixing (not every mismatch is: Earth is a test analogue, not a parity target);
- a follow-up, a missing piece, or a cleanup you deliberately skipped;
- a judgement call for Daniel (`status: needs-decision`).

Don't open one for work you finish in the same branch, for pure observations with no action, or for timings and numbers (those go in `docs/coordination.md` or the review docs). Before opening, check the board for an existing ticket: `board.py list --subsystem X`.

## Subagents: write inbox drafts, never IDs

Subagents in worktrees must not number tickets (parallel branches would collide). Report every remaining issue as a draft file `issue-tracking/inbox/draft-<slug>.md` and commit it on your branch. One issue per file. Don't report remaining issues as prose only. Copy this template:

```markdown
---
title: Zoom falls lose their step when the river leaves the region
type: task              # epic | story | task
status: todo            # todo, or needs-decision for a judgement call
parent: null            # an epic/story id, e.g. PW-012, or null
milestone: null         # v1, v2, v3, v4, later, or null (unscheduled); may be left out of a draft
subsystem: zoom         # tectonics surface climate ocean hydrology coast zoom timezoom highlights viewer store infra docs
effort: s               # xs <30 min, s <2 h, m ~half a day, l a day or more, xl multi-agent project
impact: med             # low | med | high (see below)
found_by: falls2        # your branch or agent name
blocked_by: []
relates: []             # existing ticket ids, e.g. [PW-031]
refs: [planet/zoom.py, "zoom 58ed13", docs/review/zoom/]
---

## Description
What is wrong or missing, where you saw it (run/world/zoom ids, numbers), why it
matters, and what you'd try. Self-contained: someone who never saw your branch
must be able to act on it.
- [ ] acceptance criteria as a checklist, when useful
```

**List everything in `refs`.** A draft's `refs` (and a ticket update's) lists everything you actually used and anything a fixer will need: code functions (`path.py::name`), notes and reports, harness scripts, the specific runs, worlds and places you looked at (prefer protected or durable ones; say in the Description when a scratch run is gone), and papers by key. Two refs is almost always too few. When you create a ticket, put in everything you think it will need ahead of time. When a lane works on an open ticket, it fills in that ticket's thin refs as it goes; that is the only backfill (no backfill lanes, none for closed tickets).

For a `needs-decision` draft, the Description lays out the options (A, B, C), the trade-offs, and your lean.

`board.py check` (and the hook) validates drafts too, so a bad field shows up while you're still on the branch.

## Coordinator: intake after each merge

```bash
uv run python issue-tracking/board.py intake --list                      # each draft, with any problems
uv run python issue-tracking/board.py intake --reject draft-x.md "duplicate of PW-031"   # delete it
uv run python issue-tracking/board.py intake --merge-into PW-031 draft-x.md               # append it to PW-031's Updates
uv run python issue-tracking/board.py intake                             # number the rest: PW-NNN, into tickets/
```

Triage duplicates with `--reject` or `--merge-into` first, then run plain `intake`. It gives each draft the next `PW-NNN` id (in filename order), adds `created`/`updated` and a "Created from inbox draft" update, moves it to `tickets/`, and validates it. A draft without a `milestone` line becomes unscheduled (`milestone: null`). Drafts that fail validation stay in the inbox with their errors. Commit the result. On main, the coordinator may also create tickets directly with `board.py new`.

## Ticket format

```markdown
---
id: PW-014
title: Rivers in the zoom run perched above the land beside them
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: falls2
blocked_by: []
relates: [PW-012]
refs: [planet/zoom.py, "zoom f99af0"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
What and why, with enough detail to act on. Edit in place as understanding changes.

## Updates
- 2026-10-15: Newest first. One dated line per entry; continuation lines indented.
- 2026-10-14: Created.
```

## Fields

The 15 fields above are the complete schema; `check` rejects unknown and missing ones. No assignees, priorities, labels or due dates. To add a field, add it to `FIELDS` in `board.py` and document it here first.

- `type`: epic → story → task. A parent must rank above its child (a task may sit directly under an epic). `parent` is optional: most tickets have none. Epics are for real multi-ticket projects, not for grouping a subsystem (that's what `subsystem` is for).
- `milestone`: `v1`, `v2`, `v3`, `v4`, `later`, or `null` (unscheduled, the default). It says which release a ticket is planned for. `v1` is the finished, plausible planet; `v2` is the next features and the physics lanes' known path; `v3` is deliberately far off: a system of its own (civilization, technology, weather, moons and weird worlds, L8/L9) that the owner wants eventually but only after v2; `v4` is further still: ground-level, asset-heavy work (a walkable setting) after v3; `later` is "maybe, unscheduled": polish, quality-pass items and ideas nobody has pulled for. Rule of thumb: v3 needs an owner who wants it and a reason it waits; `later` needs neither. Milestones are not inherited: each ticket carries its own value, whatever its parent says. Drafts may omit it (intake makes it null). Use `board.py milestones [v1]` for counts and open tickets.

PW-244 is v1's written definition: the epic describes what v1 has to deliver, and its children are the work that does it. `milestone` decides membership. A ticket under PW-244 can be set to `v2` (PW-247, the speed pass, is one), and a v1 ticket need not sit under PW-244. Read PW-244 for the meaning of v1; read `milestone` for what is in it.
- `status`: `todo`, `in-progress`, `blocked` (only with `blocked_by` filled in), `needs-decision`, `done`, `wontdo`. A `needs-decision` ticket's Description gives the options and the coordinator's lean; Daniel's answer goes in Updates, then the status moves on.
- `subsystem`: tectonics, surface (erosion, sediment, rock), climate, ocean, hydrology (rivers, lakes), coast (waves, tides, deltas), zoom, timezoom, highlights, viewer, store (run/world/zoom files, checkpoints), infra (server, API, tests, tools, performance), docs.
- `effort`, in agent time: **xs** under 30 min; **s** under 2 h; **m** about half a day; **l** about a day or more; **xl** a multi-agent project (usually an epic).
- `impact`: how much better the planets look, behave or match Earth, or how much other work it unblocks. **high**: visible on most worlds or a key Earth check, or it unblocks an epic. **med**: visible in some places or zooms, or a clear Earth miss in one region. **low**: cosmetic, rare, or internal tidiness.
- `found_by`: the branch, agent or user that found it (`falls2`, `coordinator`, `daniel`).
- `blocked_by`, `relates`: ticket ids, recorded on one side only; `show` computes "blocks" and "related by".
- `refs`: file paths, doc sections, run/world/zoom ids (`"run fe7144"`, `"zoom f81832"`). Quote anything with spaces or commas. See "References to runs, worlds and places" below.
- `created`, `updated`: `YYYY-MM-DD`; `update` bumps `updated`.

**Updates are append-only**, newest first, each `- YYYY-MM-DD: text`. Don't edit or delete old entries. Close with `done` or `wontdo` and a one-line reason. Delete a file only if the ticket was a mistake. Never rename a file, even if the title changes.

## References to runs, worlds and places

Point at a moment and a place with these forms (in `refs` or in prose):

| What | Form | Example |
|---|---|---|
| a run at a time, at a place | `run:<id>@<t>Myr(<lat>,<lon>)` | `run:428083@624Myr(7.80,156.60)` |
| a world, at a place | `world:<id>(<lat>,<lon>)` | `world:7c5adf(-30.08,119.50)` |
| a regional zoom | `zoom:<id>` | `zoom:f81832` |
| a paper | `paper:<AuthorYear>`, a key in `docs/references/bibliography.md` | `paper:Holman2011` |
| a doc section | `path.md#heading-anchor` | `issue-tracking/README.md#subagents-write-inbox-drafts-never-ids` |
| a function or class | `path.py::name` | `planet/tectonics/crust.py::birth_and_cratons` |
| a note, report, harness script | its plain path (encouraged) | `docs/review/tectonics/margin/tracediag.py` |

The plain `run fe7144` / `world 7c5adf` / `zoom f81832` still work for a whole run, world or zoom. Use lat/lon, not cell ids: cell ids differ by grid level. Clicking a cell in the viewer copies the reference, the cell's description and a deep link that reopens the viewer there (`viewer/?run=428083&t=624&lat=7.80&lon=156.60`, or `?world=7c5adf.json&lat=..&lon=..`); paste the reference into the ticket and the link too if it helps.

Cite every paper you relied on by key; if it is not in `docs/references/bibliography.md`, add a line there (key, full citation, what you read, where the repo uses it) from the paper itself, never from memory. `check` warns (never fails) when a `paper:` key is missing from the bibliography, a `path.py::name` is not defined in that file, a `#anchor` matches no heading, or a path does not exist.

Runs, worlds and zooms get deleted (`planet delete`). `check` warns when open tickets' `refs` name ids that no longer exist; `check --refs` lists every such ref in all tickets' `refs` and Descriptions. Replace a dangling ref with a current one or note in an update that it's gone.

## CLI

Run from the repo root:

```bash
uv run python issue-tracking/board.py next [--subsystem zoom] [--limit 15]   # todo/in-progress, unblocked, effort asc then impact desc
uv run python issue-tracking/board.py decisions [--brief]                     # needs-decision tickets with their options
uv run python issue-tracking/board.py morning [--hours 24]                    # markdown digest: decisions + recent updates by subsystem
uv run python issue-tracking/board.py list --open --subsystem climate         # filters: --status --type --parent --subsystem --effort --impact --milestone
uv run python issue-tracking/board.py next --milestone v1                     # the same filter works on next and tree
uv run python issue-tracking/board.py tree [PW-002] [--open] [--milestone v1] # epics with children, then parentless tickets by subsystem
uv run python issue-tracking/board.py milestones [v1]                         # open/done counts per milestone; with one, its open tickets
uv run python issue-tracking/board.py show PW-014                             # ticket + computed blocks/related-by/children
uv run python issue-tracking/board.py new --type task --title "..." --subsystem zoom --effort s --impact med \
    [--found-by coordinator] [--parent PW-002] [--milestone v2] [--status needs-decision] [--desc "..."] [--ref X] [--relates PW-1] [--blocked-by PW-2]
uv run python issue-tracking/board.py update PW-014 "Fixed in a1b2c3d." [--status done]
uv run python issue-tracking/board.py intake ...                              # see above
uv run python issue-tracking/board.py check [--refs]                          # validate tickets and inbox drafts (--refs: list dangling run/world/zoom refs)
uv run python issue-tracking/board.py review [--orphans]                      # each docs/review file with what keeps it (see "Lane evidence")
```

`morning` prints to stdout; paste it where needed, but never commit a generated digest file. Its "updated in the last N hours" is day-granular (tickets carry dates, not times). Other edits (title, description, refs, links) are made directly in the file.

## Lane evidence in docs/review

Evidence a lane leaves behind (reports, tables, images, probe scripts) goes under `docs/review/<topic>/` and is cited from its tickets by path. It stays only while something live names it: an open ticket (anywhere in its file, including a partial path like `laneA10/x.txt` that ends exactly one review file), a core doc (any `.md` under `docs/` outside `review/`, `README.md`, `CLAUDE.md`), tracked code (`planet/ tools/ tests/ viewer/`), or a kept review page or script that names it (a `docs/review/` path, a relative link, or its path or folder relative to the page). `docs/review/*` names a rule, not files, and keeps nothing. When its tickets close it is deleted; the history keeps it. `board.py review [--orphans]` lists each file with what keeps it and the closed tickets that cite it; `check` warns with the orphans. Delete them with `git rm` and note each closed ticket that cited one: `board.py update PW-n "Removed <path> in cleanup; last present at <sha>."` (the last commit that had it). Don't re-note a removal a ticket already records. Large screenshot bundles stay outside the repo.

## Validation

`check` also verifies that `docs/wiki/*.md` links and repo paths exist and its PW- ids are tickets, warns when `docs/wiki/state.md` is over 3 days old, and warns with the docs/review files nothing live names (above). It enforces the exact field set; valid type, status, subsystem, effort, impact and milestone values; non-empty `found_by`; real dates with `updated` ≥ `created`; list-typed links whose targets exist and aren't the ticket itself; parent rank and no parent loops; `blocked` only with `blocked_by`; `## Description` and `## Updates` sections with well-formed entries; filenames starting with the id. Drafts get the same checks, minus `id`/`created`/`updated` and the Updates section.

Frontmatter is a small YAML subset (one `key: value` per line, flow lists `[a, "b c"]`, `#` comments), parsed by `board.py` itself, so it needs no dependencies.

A Claude Code `PostToolUse` hook (`.claude/hooks/issue_tracking_check.sh`, wired in `.claude/settings.json`) runs `check` after any Edit/Write under `issue-tracking/`, or any Bash command mentioning it. It finds the repo from the edited file's path, so it checks the right worktree. If `check` fails, the errors go back to the agent to fix.
