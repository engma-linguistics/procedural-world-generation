---
id: PW-1730
title: Decide where installer releases come from before curl | sh can work
type: task
status: needs-decision
parent: null
milestone: v1.0
subsystem: infra
effort: s
impact: high
found_by: lane304
blocked_by: []
relates: []
refs: [install.sh, docs/review/plan/installer.md, docs/review/plan/milestones-to-v1.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
`install.sh` works from a checkout, a tarball or a local git repo (`--source`), and was tested end to end that way.
The one-line `curl -LsSf <release>/install.sh | sh` needs a public place to fetch the script and the tags from. Its
default source is the GitHub repo (`DEFAULT_SOURCE` in install.sh); if that repo is private, a fresh user's install
fails at `git ls-remote` with an auth prompt, and the plan's headline "one command" does not hold. The plan's details
(desk card D80) are not confirmed yet either.

## Decide
- Where releases live: the GitHub repo made public, a public mirror, or release tarballs (then install.sh needs a
  tarball path for the remote case; today a remote source needs git).
- Whether release tags stay `v*` (update takes the newest `v*` tag by `sort -V`).
- Whether data, config and root paths in the plan (`~/procgen-world-data`, `~/.config/procgen-world`,
  `~/.local/share/procgen-world`) are the ones Daniel wants.

## Updates
- 2026-11-11: Created from inbox draft draft-installer-release-channel.md (found by lane304).
