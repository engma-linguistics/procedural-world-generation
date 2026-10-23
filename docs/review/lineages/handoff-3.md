# Lineages lane 3: handoff (2026-10-23)

Showcase and numbers: `showcase-3.md`. Design notes: `docs/proposals/lineages.md`, section "Lane 3 additions".

## Done
- **Speed.** L7 is ~4x faster (265 s -> 63 s a try, side by side). Outputs are identical: frames and events bitwise, the present presence within 2e-16. A test checks that the front-only spread equals the full sweep.
- **PW-604, near wishes.** The habitat pull is toward the other's border, the origin pull is wider and symmetric, the two tolerate each other, and the score distance is in km. A test covers it. Table in showcase-3.md.
- **PW-602.** Exposed shelf is a corridor in past epochs. The plains and river values are unchanged; that decision is still open.
- **Best of N** prefers tries that keep every living line.
- **Showcase.** New runs 3cf7fe, 2c70d9, 13cf30, 5cdd4a. Lane 2's 037790, 06a854, 2dcc80 and dfcbd2 were deleted.

## Next
- Inbox: `draft-lineages-goblin-orc-niches` (preset; lean: hobgoblin near orc) and `draft-lineages-contact-hybrids-lost`.
- Further speed: the remaining time is spread over habitat, frames, crossings, tags and per-line full-grid array work, ~10 s each. Compacting `History.p` to the land cells would be the next step. It would be a larger refactor (the spread crosses sea cells).
