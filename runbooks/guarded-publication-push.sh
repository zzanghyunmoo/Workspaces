#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat <<'USAGE'
Usage:
  guarded-publication-push.sh --repo PATH --candidate RELATIVE_PATH \
    --base-branch NAME --remote NAME --branch NAME \
    --expected-remote URL_OR_PATH

Required approval environment (must match the current immutable inputs):
  PUBLICATION_PUSH_APPROVED=1
  PUBLICATION_PUSH_APPROVED_REMOTE=<expected remote URL/path>
  PUBLICATION_PUSH_APPROVED_BRANCH=<remote branch>
  PUBLICATION_PUSH_APPROVED_BASE=<fetched 40-character base commit SHA>
  PUBLICATION_PUSH_APPROVED_HEAD=<40-character commit SHA>
  PUBLICATION_PUSH_APPROVED_CANDIDATE=<candidate repository path>

Set PUBLICATION_CANARY without printing it before invoking this wrapper.
USAGE
}

repo=""
candidate=""
base_branch=""
remote=""
branch=""
expected_remote=""

while [ "$#" -gt 0 ]; do
	case "$1" in
	--repo | --candidate | --base-branch | --remote | --branch | --expected-remote)
		[ "$#" -ge 2 ] || { usage >&2; exit 2; }
		case "$1" in
		--repo) repo="$2" ;;
		--candidate) candidate="$2" ;;
		--base-branch) base_branch="$2" ;;
		--remote) remote="$2" ;;
		--branch) branch="$2" ;;
		--expected-remote) expected_remote="$2" ;;
		esac
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

for value in "$repo" "$candidate" "$base_branch" "$remote" "$branch" "$expected_remote"; do
	[ -n "$value" ] || { usage >&2; exit 2; }
done

case "$remote" in
*[!A-Za-z0-9._-]* | "") printf 'FAIL: publication rejected (unsafe remote name)\n' >&2; exit 1 ;;
esac

repo_root="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || {
	printf 'FAIL: publication rejected (repository unavailable)\n' >&2
	exit 1
}
repo_root="$(cd "$repo_root" && pwd -P)"

current_branch="$(git -C "$repo_root" symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
git -C "$repo_root" check-ref-format --branch "$branch" >/dev/null 2>&1 || {
	printf 'FAIL: publication rejected (unsafe branch)\n' >&2
	exit 1
}
git -C "$repo_root" check-ref-format --branch "$base_branch" >/dev/null 2>&1 || {
	printf 'FAIL: publication rejected (unsafe base branch)\n' >&2
	exit 1
}
[ "$current_branch" = "$branch" ] || {
	printf 'FAIL: publication rejected (branch mismatch)\n' >&2
	exit 1
}

head_sha="$(git -C "$repo_root" rev-parse --verify HEAD 2>/dev/null)" || {
	printf 'FAIL: publication rejected (HEAD unavailable)\n' >&2
	exit 1
}
actual_remote="$(git -C "$repo_root" remote get-url "$remote" 2>/dev/null)" || {
	printf 'FAIL: publication rejected (remote unavailable)\n' >&2
	exit 1
}
[ "$actual_remote" = "$expected_remote" ] || {
	printf 'FAIL: publication rejected (remote mismatch)\n' >&2
	exit 1
}

base_ref="refs/remotes/$remote/$base_branch"
if ! git -C "$repo_root" fetch --quiet --no-tags "$remote" \
	"+refs/heads/$base_branch:$base_ref"; then
	printf 'FAIL: publication rejected (base branch unavailable)\n' >&2
	exit 1
fi
base_sha="$(git -C "$repo_root" rev-parse --verify "$base_ref^{commit}")"
[ "$base_sha" != "$head_sha" ] || {
	printf 'FAIL: publication rejected (publication history is empty)\n' >&2
	exit 1
}
changed_paths="$(git -C "$repo_root" diff --name-only --no-renames "$base_sha..$head_sha")"
if [ "$changed_paths" != "$candidate" ]; then
	printf 'FAIL: publication rejected (approved candidate must be the only changed path)\n' >&2
	exit 1
fi
if [ -n "$(git -C "$repo_root" rev-list --merges "$base_sha..$head_sha")" ]; then
	printf 'FAIL: publication rejected (publication history must not contain merge commits)\n' >&2
	exit 1
fi
historical_paths="$(
	git -C "$repo_root" log --format= --name-only --no-renames "$base_sha..$head_sha" |
		sed '/^$/d' | LC_ALL=C sort -u
)"
if [ "$historical_paths" != "$candidate" ]; then
	printf 'FAIL: publication rejected (publication history touched a non-candidate path)\n' >&2
	exit 1
fi

if [ "${PUBLICATION_PUSH_APPROVED:-}" != "1" ] ||
	[ "${PUBLICATION_PUSH_APPROVED_REMOTE:-}" != "$expected_remote" ] ||
	[ "${PUBLICATION_PUSH_APPROVED_BRANCH:-}" != "$branch" ] ||
	[ "${PUBLICATION_PUSH_APPROVED_BASE:-}" != "$base_sha" ] ||
	[ "${PUBLICATION_PUSH_APPROVED_HEAD:-}" != "$head_sha" ] ||
	[ "${PUBLICATION_PUSH_APPROVED_CANDIDATE:-}" != "$candidate" ]; then
	cat >&2 <<'MSG'
FAIL: publication rejected (exact user approval is missing or stale).
Confirm the remote, branch, fetched base, HEAD, and candidate in an approval packet, then set the six
PUBLICATION_PUSH_APPROVED* values for this command only.
MSG
	exit 1
fi

[ -n "${PUBLICATION_CANARY:-}" ] || {
	printf 'FAIL: publication rejected (canary not configured)\n' >&2
	exit 1
}

[ -z "$(git -C "$repo_root" status --porcelain --untracked-files=all)" ] || {
	printf 'FAIL: publication rejected (working tree is not clean)\n' >&2
	exit 1
}

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
checker="$workspace_root/runbooks/check_publication_candidate.py"

(
	cd "$repo_root"
	python3 "$checker" check \
		--blog-root "$repo_root" \
		--candidate "$candidate" \
		--base-ref "$base_sha"
)

build_runner="$workspace_root/runbooks/run_publication_build.py"
build_timeout="${PUBLICATION_BUILD_TIMEOUT_SEC:-300}"
if ! python3 "$build_runner" --repo "$repo_root" --timeout "$build_timeout"; then
	printf 'FAIL: publication rejected (public build failed or timed out; output suppressed)\n' >&2
	exit 1
fi

(
	cd "$repo_root"
	python3 "$checker" check \
		--blog-root "$repo_root" \
		--candidate "$candidate" \
		--base-ref "$base_sha" \
		--artifact-root dist
)

current_head="$(git -C "$repo_root" rev-parse --verify HEAD)"
current_branch="$(git -C "$repo_root" symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
current_remote="$(git -C "$repo_root" remote get-url "$remote")"
if [ "$current_head" != "$head_sha" ] || [ "$current_branch" != "$branch" ] ||
	[ "$current_remote" != "$expected_remote" ] ||
	[ -n "$(git -C "$repo_root" status --porcelain --untracked-files=all)" ]; then
	printf 'FAIL: publication rejected (approved state changed during verification)\n' >&2
	exit 1
fi

git -C "$repo_root" push "$remote" "$head_sha:refs/heads/$branch"
printf 'PASS: approved publication history was pushed after privacy verification\n'
