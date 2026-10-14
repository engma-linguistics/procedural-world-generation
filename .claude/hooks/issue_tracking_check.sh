#!/usr/bin/env bash
# PostToolUse hook: after anything touches issue-tracking/, run `board.py check`
# in the repo (or worktree) that was touched. On failure, exit 2 so the errors
# are fed back to Claude to fix.
#
# The repo root comes from the edited file's path (everything before
# /issue-tracking/), so edits inside .claude/worktrees/<branch>/ are checked
# against that worktree's board, not main's. For Bash commands with a relative
# path, it walks up from the hook's cwd to the nearest issue-tracking/board.py.
input=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")

case "$tool" in
  Edit|Write|MultiEdit)
    target=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' <<<"$input")
    ;;
  Bash)
    target=$(jq -r '.tool_input.command // empty' <<<"$input")
    ;;
  *) exit 0 ;;
esac

[[ "$target" == *issue-tracking/* || "$target" == *issue-tracking\ * || "$target" == *issue-tracking ]] || exit 0

root=""
# an absolute path mentioning issue-tracking: take the part before it
abs=$(grep -oE '/[^ "'"'"'`;|&<>]*/issue-tracking' <<<"$target" | head -n1)
if [[ -n "$abs" && -f "${abs}/board.py" ]]; then
  root=${abs%/issue-tracking}
else
  dir=${cwd:-${CLAUDE_PROJECT_DIR:-$PWD}}
  while [[ -n "$dir" && "$dir" != "/" ]]; do
    if [[ -f "$dir/issue-tracking/board.py" ]]; then root=$dir; break; fi
    dir=$(dirname "$dir")
  done
fi
[[ -n "$root" ]] || exit 0

# board.py is standard-library only: --no-project skips syncing the repo's
# numba/numpy environment (slow in a fresh worktree).
if ! out=$(cd "$root" && uv run --quiet --no-project --python 3.12 python issue-tracking/board.py check 2>&1); then
  printf 'issue-tracking/board.py check failed in %s. Fix these before continuing:\n%s\n' "$root" "$out" >&2
  exit 2
fi
exit 0
