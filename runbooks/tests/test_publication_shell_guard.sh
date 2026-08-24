#!/usr/bin/env bash
set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT

remote_dir="$test_dir/public-blog.git"
blog_dir="$test_dir/public-blog"
git init -q --bare "$remote_dir"
git init -q -b v4 "$blog_dir"
git -C "$blog_dir" config user.name "Publication Test"
git -C "$blog_dir" config user.email "publication@example.test"
printf 'dist/\n' >"$blog_dir/.gitignore"
printf '# Blog\n' >"$blog_dir/README.md"
git -C "$blog_dir" add .gitignore README.md
git -C "$blog_dir" commit -q -m "initial"
base_sha="$(git -C "$blog_dir" rev-parse HEAD)"
git -C "$blog_dir" remote add origin "$remote_dir"
git -C "$blog_dir" push -q origin v4
git -C "$blog_dir" switch -q -c feat/wiki
mkdir -p "$blog_dir/src/data/blog"
printf '# Safe publication\n' >"$blog_dir/src/data/blog/public-note.md"
git -C "$blog_dir" add src/data/blog/public-note.md
git -C "$blog_dir" commit -q -m "publish safe note"
head_sha="$(git -C "$blog_dir" rev-parse HEAD)"

git -C "$blog_dir" switch -q -c feat/wiki-history
printf 'transient private material\n' >"$blog_dir/transient-private.txt"
git -C "$blog_dir" add transient-private.txt
git -C "$blog_dir" commit -q -m "add transient non-candidate"
git -C "$blog_dir" rm -q transient-private.txt
git -C "$blog_dir" commit -q -m "remove transient non-candidate"
history_head_sha="$(git -C "$blog_dir" rev-parse HEAD)"

if PUBLICATION_PUSH_APPROVED=1 \
  PUBLICATION_PUSH_APPROVED_REMOTE="$remote_dir" \
  PUBLICATION_PUSH_APPROVED_BRANCH=feat/wiki-history \
  PUBLICATION_PUSH_APPROVED_BASE="$base_sha" \
  PUBLICATION_PUSH_APPROVED_HEAD="$history_head_sha" \
  PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md \
  "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/wiki-history \
  --expected-remote "$remote_dir" >/dev/null 2>&1; then
  printf 'publication push accepted a reverted non-candidate history path\n' >&2
  exit 1
fi

git -C "$blog_dir" switch -q feat/wiki

mkdir -p "$test_dir/bin"
cat >"$test_dir/bin/npm" <<'NPM'
#!/usr/bin/env bash
set -euo pipefail
[ "${1:-}" = "run" ] && [ "${2:-}" = "build" ]
if [ "${PUBLICATION_TEST_HANG_BUILD:-}" = "1" ]; then
  sleep 30
fi
mkdir -p dist/pagefind
printf '<h1>Safe publication</h1>\n' >dist/index.html
printf 'safe index\n' >dist/pagefind/index.js
if [ "${PUBLICATION_TEST_MUTATE_HEAD:-}" = "1" ]; then
  printf 'unexpected build mutation\n' >>README.md
  git add README.md
  git commit -q -m 'unexpected build mutation'
fi
NPM
chmod +x "$test_dir/bin/npm"
export PATH="$test_dir/bin:$PATH"
export PUBLICATION_CANARY="PRIVATE-CANARY-shell-91f0c4"

if "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/wiki \
  --expected-remote "$remote_dir" >/dev/null 2>&1; then
  printf 'publication push unexpectedly bypassed approval\n' >&2
  exit 1
fi

PUBLICATION_PUSH_APPROVED=1 \
PUBLICATION_PUSH_APPROVED_REMOTE="$remote_dir" \
PUBLICATION_PUSH_APPROVED_BRANCH=feat/wiki \
PUBLICATION_PUSH_APPROVED_BASE="$base_sha" \
PUBLICATION_PUSH_APPROVED_HEAD="$head_sha" \
PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md \
  "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/wiki \
  --expected-remote "$remote_dir" >/dev/null

remote_head="$(git --git-dir="$remote_dir" rev-parse refs/heads/feat/wiki)"
if [ "$remote_head" != "$head_sha" ]; then
  printf 'guarded publication did not push the approved head\n' >&2
  exit 1
fi

if PUBLICATION_TEST_HANG_BUILD=1 \
  PUBLICATION_BUILD_TIMEOUT_SEC=1 \
  PUBLICATION_PUSH_APPROVED=1 \
  PUBLICATION_PUSH_APPROVED_REMOTE="$remote_dir" \
  PUBLICATION_PUSH_APPROVED_BRANCH=feat/wiki \
  PUBLICATION_PUSH_APPROVED_BASE="$base_sha" \
  PUBLICATION_PUSH_APPROVED_HEAD="$head_sha" \
  PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md \
  "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/wiki \
  --expected-remote "$remote_dir" >/dev/null 2>&1; then
  printf 'publication push accepted a hung public build\n' >&2
  exit 1
fi

if PUBLICATION_PUSH_APPROVED=1 \
  PUBLICATION_PUSH_APPROVED_REMOTE="$remote_dir" \
  PUBLICATION_PUSH_APPROVED_BRANCH=feat/wiki \
  PUBLICATION_PUSH_APPROVED_BASE="$head_sha" \
  PUBLICATION_PUSH_APPROVED_HEAD="$head_sha" \
  PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md \
  "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch feat/wiki \
  --remote origin \
  --branch feat/wiki \
  --expected-remote "$remote_dir" >/dev/null 2>&1; then
  printf 'publication push accepted an empty caller-selected history range\n' >&2
  exit 1
fi

if PUBLICATION_TEST_MUTATE_HEAD=1 \
  PUBLICATION_PUSH_APPROVED=1 \
  PUBLICATION_PUSH_APPROVED_REMOTE="$remote_dir" \
  PUBLICATION_PUSH_APPROVED_BRANCH=feat/wiki \
  PUBLICATION_PUSH_APPROVED_BASE="$base_sha" \
  PUBLICATION_PUSH_APPROVED_HEAD="$head_sha" \
  PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md \
  "$workspace_root/runbooks/guarded-publication-push.sh" \
  --repo "$blog_dir" \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/wiki \
  --expected-remote "$remote_dir" >/dev/null 2>&1; then
  printf 'publication push accepted a build-time HEAD mutation\n' >&2
  exit 1
fi

remote_head_after_rejection="$(git --git-dir="$remote_dir" rev-parse refs/heads/feat/wiki)"
if [ "$remote_head_after_rejection" != "$head_sha" ]; then
  printf 'rejected publication changed the remote branch\n' >&2
  exit 1
fi

private_clone="$test_dir/private clone"
git init -q -b main "$private_clone"
git -C "$private_clone" config user.name "Private Test"
git -C "$private_clone" config user.email "private@example.test"
"$workspace_root/runbooks/install-main-guard-hooks.sh" --repo "$private_clone" >/dev/null

expected_hooks="$workspace_root/.githooks"
actual_hooks="$(git -C "$private_clone" config --get core.hooksPath)"
if [ "$actual_hooks" != "$expected_hooks" ]; then
  printf 'external clone did not receive the workspace main guard\n' >&2
  exit 1
fi

if (cd "$private_clone" && "$workspace_root/.githooks/pre-commit") >/dev/null 2>&1; then
  printf 'external private clone main branch was not protected\n' >&2
  exit 1
fi

git -C "$private_clone" switch -q -c feat/notes
(cd "$private_clone" && "$workspace_root/.githooks/pre-commit")

printf 'PASS: guarded publication pins approval and external clone main is protected\n'
