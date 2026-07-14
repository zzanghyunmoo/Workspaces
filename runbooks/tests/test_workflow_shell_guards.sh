#!/usr/bin/env bash
set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT
mkdir -p "$test_dir/bin"

cat >"$test_dir/bin/python3" <<'PYTHON'
#!/usr/bin/env bash
set -euo pipefail
command_name="${2:-}"
case "$command_name" in
pre-merge)
  cat <<'OUTPUT'
PASS: workflow evidence and latest-head reviews are complete
VERIFIED_HEAD_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
OUTPUT
  ;;
record-closeout)
  printf 'record\n' >>"$TEST_DIR/sequence"
  ;;
cancel-closeout)
  printf 'cancel\n' >>"$TEST_DIR/sequence"
  ;;
pending-closeouts)
  printf '%s\n' "$*" >"$TEST_DIR/pre-push-args"
  ;;
*)
  printf 'unexpected Python command: %s\n' "$command_name" >&2
  exit 1
  ;;
esac
PYTHON
chmod +x "$test_dir/bin/python3"

cat >"$test_dir/bin/gh" <<'GH'
#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "pr" ] && [ "${2:-}" = "view" ]; then
  cat <<'OUTPUT'
42
Guarded workflow
https://github.com/owner/repo/pull/42
feature
main
CLEAN
MERGEABLE
false
OPEN
OUTPUT
  exit 0
fi
if [ "${1:-}" = "pr" ] && [ "${2:-}" = "merge" ]; then
  printf 'merge\n' >>"$TEST_DIR/sequence"
  printf '%s\n' "$*" >"$TEST_DIR/merge-args"
  exit 0
fi
printf 'unexpected gh command: %s\n' "$*" >&2
exit 1
GH
chmod +x "$test_dir/bin/gh"

export TEST_DIR="$test_dir"
export PATH="$test_dir/bin:$PATH"

PR_MERGE_APPROVED=1 \
	PR_MERGE_APPROVED_REPO=owner/repo \
	PR_MERGE_APPROVED_PR=42 \
	"$workspace_root/runbooks/guarded-pr-merge.sh" \
	--repo owner/repo \
	--pr 42 \
	--workflow-evidence docs/works/work.md \
	--method squash >/dev/null

expected_sequence=$'record\nmerge'
actual_sequence="$(cat "$test_dir/sequence")"
if [ "$actual_sequence" != "$expected_sequence" ]; then
	printf 'expected closeout debt before merge, got:\n%s\n' "$actual_sequence" >&2
	exit 1
fi

grep -F -- '--match-head-commit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
	"$test_dir/merge-args" >/dev/null

local_sha=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
printf 'refs/heads/main %s refs/heads/main %s\n' \
	"$local_sha" cccccccccccccccccccccccccccccccccccccccc |
	"$workspace_root/.githooks/pre-push" origin https://github.com/owner/repo.git

grep -F -- "pending-closeouts --ref $local_sha" "$test_dir/pre-push-args" >/dev/null

printf 'PASS: guarded merge pins reviewed head and pre-push validates pushed SHA\n'
