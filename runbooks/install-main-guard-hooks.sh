#!/usr/bin/env bash
set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repos=("$workspace_root")

if [ -d "$workspace_root/projects/ReplaceMe/.git" ]; then
	repos+=("$workspace_root/projects/ReplaceMe")
fi

for repo in "${repos[@]}"; do
	git -C "$repo" rev-parse --git-dir >/dev/null
	git -C "$repo" config core.hooksPath "$workspace_root/.githooks"
	printf 'main-guard hooks installed for %s\n' "$repo"
done

cat <<'MSG'

main-guard is active through core.hooksPath.
Root zWorkspaces may commit/push directly on main.
Project repositories under projects/ remain protected.

To override a protected project repo after explicit user approval only:
  MAIN_GUARD_APPROVED=1 git commit ...
  MAIN_GUARD_APPROVED=1 git push ...

PR merge guard is procedural, because GitHub/GitLab PR merges do not run local
Git hooks. Use runbooks/guarded-pr-merge.sh and never call gh pr merge directly.
MSG
