#!/usr/bin/env bash
set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repos=()
explicit_mode=0

usage() {
	cat <<'USAGE'
Usage: install-main-guard-hooks.sh [--repo PATH]...

Without arguments, install hooks for zWorkspaces and discovered projects/* Git
repositories. With --repo, install only in each explicit repository, including
private clones that intentionally live outside the public workspace tree.
USAGE
}

while [ "$#" -gt 0 ]; do
	case "$1" in
	--repo)
		[ "$#" -ge 2 ] || { usage >&2; exit 2; }
		repos+=("$2")
		explicit_mode=1
		shift 2
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		usage >&2
		exit 2
		;;
	esac
done

if [ "${#repos[@]}" -eq 0 ]; then
	repos=("$workspace_root")
	for project_repo in "$workspace_root"/projects/*; do
		if [ -e "$project_repo/.git" ]; then
			repos+=("$project_repo")
		fi
	done
fi

for repo in "${repos[@]}"; do
	repo_root="$(git -C "$repo" rev-parse --show-toplevel)"
	repo_root="$(cd "$repo_root" && pwd -P)"
	git -C "$repo_root" config core.hooksPath "$workspace_root/.githooks"
	if [ "$explicit_mode" -eq 1 ]; then
		printf 'main-guard hooks installed for explicit repository\n'
	else
		printf 'main-guard hooks installed for %s\n' "$repo_root"
	fi
done

cat <<'MSG'

main-guard is active through core.hooksPath.
Root zWorkspaces may commit/push directly on main.
Project repositories, including explicitly supplied external clones, remain
protected.

To override a protected project repo after explicit user approval only:
  MAIN_GUARD_APPROVED=1 git commit ...
  MAIN_GUARD_APPROVED=1 git push ...

PR merge guard is procedural, because GitHub/GitLab PR merges do not run local
Git hooks. Use runbooks/guarded-pr-merge.sh with --workflow-evidence and never call
gh pr merge directly. A guarded merge records closeout debt; root pre-push blocks
until docs/kb, work evidence, and ticket completion are committed.
MSG
