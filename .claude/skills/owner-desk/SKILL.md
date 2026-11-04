---
name: owner-desk
description: Use when creating, refreshing or pruning the Owner's Desk (docs/review/owner-desk/index.html, the claude.ai artifact 5PJBUSAr7sia8gncwC4hRA), after a merge, a ruling or a lane report that Daniel should see, or when Daniel asks for the desk, a decision card, or the Friday week in review.
---

# Owner's Desk: generation and upkeep

The desk is the one surface for Daniel (the owner): every decision he must make and everything he should look at goes
there, nowhere else. It is **not** the wiki: it holds only what needs him now, plus what's running. Coordinator
memory lives in `docs/wiki/` (state.md, decisions.md); durable how-to in `docs/coordination.md`.

- File: `docs/review/owner-desk/index.html` (commit it after every publish).
- Artifact: https://claude.ai/artifact/5PJBUSAr7sia8gncwC4hRA. Republish the same file path with the Artifact tool
  (`edits` for small changes); never create a second desk.
- Daniel uses the viewer, not the CLI: links go to `http://localhost:8765/...` (world zoom form
  `?world=<id>.json&tab=zoom&zoom=<zoomid>`; peoples runs `viewer/?run=<id>&layer=peoples`). Check ids exist first.

## Sections, in order

1. **Header**: kicker with the date and time of day; a two-line lede; a nav of the sections present.
2. **Open, for you**: one card per decision (`D<n>`, ticket id in the card's id line). Each card: what was found, in
   plain words; the options as a numbered A/B/C list; *my lean* and why. When he asks a question about a card, answer it
   on the card (and in chat) and keep the card open until he picks.
3. **Running now**: a table of live lanes (number, what, in plain words), then one line on what's next.
4. **Things he asked to keep** (e.g. a feature he wants to look at): a card each, with viewer links and pictures.
5. **Settled today / since last refresh**: a short list of his rulings and merges since the last refresh. Prune it on the
   next refresh: settled items go to `docs/wiki/decisions.md`, not stay on the desk.
6. **The week in review**: Fridays only, at the bottom: what shipped, what moved, the plan for next week. Drop it the
   following Monday.

## Rules

- Every card starts "In plain words" or says it plainly: no shorthand, no internal lane jargon; ticket ids in brackets.
- Never cite from memory: every number and source on the desk comes from a lane report, a ticket or a file you read.
  An unsourced judgement is labelled as one.
- Leans are honest: push back on a weak idea of his, with reasons.
- **Run `uv run python tools/desk_check.py` before every publish and fix everything it lists** (ruled cards, dead viewer links,
  a stale kicker date, a settled list over 20 items, running rows for merged lanes). It can't see a card he answered in chat
  whose ticket is still open, so also: when he answers a card, remove it in that same turn; when a lane merges, move its row
  to settled in that same turn. Each refresh rewrites the kicker and lede for now, not appends.
- Prune on every refresh: remove settled cards, finished lanes, sections he has seen and acknowledged. Move anything
  durable (run costs, measured stats) to `docs/coordination.md` or the ticket before deleting it from the desk.
- Bump the footer's version (`Desk vN`) and publish with a short `label` (e.g. "v94: lane 132 merged").
- Record each of his answers on its ticket (`board.py update`) and a line in `docs/wiki/decisions.md` in the same turn.
- Daniel is he/him. Dragons are sapient (never "beasts").

## Style

Keep the existing look (the `<style>` block at the top: Source Serif 4 headings, IBM Plex body, the paper palette with
its dark-mode tokens, `.card`, `.id`, `.tbl`, `.done`). Don't restyle the page on a refresh; add classes only when a new
kind of content needs one.
