# Coordinator wiki

Lean map for the coordinating session. It points at things and does not restate them: follow the links. The full human wiki is parked (PW-792).

Read first, in order:
1. [state.md](state.md): what is true now (v1/v2 status, showcase ids, lanes). One overwritten page; check its "last updated".
2. [decisions.md](decisions.md): rulings still in force. Check before re-asking the owner anything.
3. [coordinator-playbook.md](coordinator-playbook.md): brief boilerplate for subagents, the merge procedure.

| Question | Page |
|---|---|
| What does "people / group / template / icehouse bar / lane" mean? | [glossary.md](glossary.md) (geology terms: [overview section 7](../overview.md)) |
| What did the owner rule on X? | [decisions.md](decisions.md) |
| What is running, what is v1/v2 status, which ids are the showcases? | [state.md](state.md) |
| Where is the run store, review folder, scorecard, presets, server? | [where-things-live.md](where-things-live.md) |
| What goes in a subagent prompt? How do I merge a lane? | [coordinator-playbook.md](coordinator-playbook.md) |
| How does subsystem X work? | [overview.md](../overview.md) |
| Open work, tickets, drafts | the board (`uv run python issue-tracking/board.py next`); rules in [issue-tracking/README.md](../../issue-tracking/README.md) |
| Worktrees, run costs, showcase recipes, server | [coordination.md](../coordination.md) |
| Roadmap by milestone | [plan_next.md](../plan_next.md) |

Conventions for this wiki:
- Link, don't copy. If a fact lives in a ticket or in overview.md, give the id or section.
- `state.md` is overwritten, never appended; history is in git.
- New rulings go in ticket Updates as `RULING (owner): ...` or `RULING (coordinator): ...`, plus one line in decisions.md.
- `board.py check` verifies this folder's file links and PW- ids, and warns when state.md is over 3 days old.
