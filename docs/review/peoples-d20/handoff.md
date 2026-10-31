# Lane 83 handoff (peoples D20)

Branch `worktree-agent-a6d3459a485a8bc68`, worktree `.claude/worktrees/agent-a6d3459a485a8bc68`. All work is committed; nothing is pushed
or merged. The narrative and tables are in report.md, and the follow-ups are five drafts in issue-tracking/inbox/.

## Done
- Stage 1: rulings 1–3 (fit with a breadth cost and a contest field; one-spot founding; stem land lies empty; a split founds by its
  dead parent's last land). INVADE and DENSITY_PUSH are removed.
- Stage 2: rulings 4–5 in dnd.toml (sourced forager densities; elves 4, dwarves 7–8; denning kobolds and goblins; martial dwarves
  and hobgoblins).
- Stage 3, from lane 84: one capacity per people (PW-1205 A) and density by era (PW-1203 A). Suite: lane 84's bloc measures and
  per-world brittleness (PW-1207).

## Still running (scratch: /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l83)
- `suite-s3/`: the full stress suite on the stage-3 code (frozen copy `code/s3f`), runner 1616919. Afterwards run
  `uv run python tools/peoples_robust.py report --out <scratch>/l83/suite-s3` from the worktree, and save the tables as
  docs/review/peoples-d20/suite-s3.md.
- `suite-base/`: the same suite on main e03eb572 (frozen copy `scratchpad/base`, arm "range"), runner 1608057. Report it from that code
  dir (`cd <scratchpad>/base && python tools/peoples_robust.py report --out <scratch>/l83/suite-base`).
- `dnd/s3-s{7,10,13}.json`: the stage-3 dnd drives (as the CLI), PIDs 1616923-1616925. Afterwards: `python3 <scratch>/l83/dndtab.py base s1
  s3`, then `planet delete` their runs. Each json has a "run_id", and the names are l83-s3-s7/10/13.
- Compare stages: `python3 <scratch>/l83/cmp.py suite-base suite-s1 suite-s2 suite-s3` (run from l83/).

## Next (in order)
1. Kobold founding (draft-peoples-split-of-a-megafauna-stem-strands): lean A, draw a megafauna stem's split by the child's own country.
   Small trees are human-only without it.
2. Look at hobgoblins (2.6–19%) and elves (8–15%) after (1), against the owner's reference of elves at 7–8%.
3. Stage 6, soft share bands (PW-1189), only if the owner still wants humans near 24–28% once (1) and PW-1202 C (late boats) are in.
4. PW-1202 A (re-weight the split landmass draw) and B (needs the owner: draft-peoples-blocs-incumbency-vs-surge).
