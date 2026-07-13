#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat <<'MSG'
Usage:
  runbooks/guarded-pr-merge.sh --repo OWNER/REPO --pr NUMBER [options]

Options:
  --method squash|merge|rebase   Merge method. Default: squash
  --subject TEXT                 Commit subject passed to gh pr merge
  --body TEXT                    Commit body passed to gh pr merge
  --body-file PATH               Commit body file passed to gh pr merge
  --delete-branch                Delete the PR branch after merge

This script refuses to merge unless the current turn has explicit user approval
for the exact repo and PR. After that approval, rerun with:

  PR_MERGE_APPROVED=1 \
  PR_MERGE_APPROVED_REPO=OWNER/REPO \
  PR_MERGE_APPROVED_PR=NUMBER \
  runbooks/guarded-pr-merge.sh --repo OWNER/REPO --pr NUMBER ...
MSG
}

repo=""
pr=""
method="squash"
subject=""
body=""
body_file=""
delete_branch=0

while [ "$#" -gt 0 ]; do
	case "$1" in
		--repo)
			repo="${2:-}"
			shift 2
			;;
		--pr)
			pr="${2:-}"
			shift 2
			;;
		--method)
			method="${2:-}"
			shift 2
			;;
		--subject)
			subject="${2:-}"
			shift 2
			;;
		--body)
			body="${2:-}"
			shift 2
			;;
		--body-file)
			body_file="${2:-}"
			shift 2
			;;
		--delete-branch)
			delete_branch=1
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			printf 'Unknown argument: %s\n\n' "$1" >&2
			usage >&2
			exit 64
			;;
	esac
done

if [ -z "$repo" ] || [ -z "$pr" ]; then
	usage >&2
	exit 64
fi

case "$method" in
	squash) method_flag="--squash" ;;
	merge) method_flag="--merge" ;;
	rebase) method_flag="--rebase" ;;
	*)
		printf 'Invalid --method: %s\n' "$method" >&2
		exit 64
		;;
esac

mapfile -t pr_info < <(
	gh pr view "$pr" \
		--repo "$repo" \
		--json number,title,url,headRefName,baseRefName,mergeStateStatus,mergeable,isDraft,state \
		--template '{{.number}}{{"\n"}}{{.title}}{{"\n"}}{{.url}}{{"\n"}}{{.headRefName}}{{"\n"}}{{.baseRefName}}{{"\n"}}{{.mergeStateStatus}}{{"\n"}}{{.mergeable}}{{"\n"}}{{.isDraft}}{{"\n"}}{{.state}}{{"\n"}}'
)

pr_number="${pr_info[0]}"
pr_title="${pr_info[1]}"
pr_url="${pr_info[2]}"
head_ref="${pr_info[3]}"
base_ref="${pr_info[4]}"
merge_state="${pr_info[5]}"
mergeable="${pr_info[6]}"
is_draft="${pr_info[7]}"
state="${pr_info[8]}"

if [ "${PR_MERGE_APPROVED:-}" != "1" ] || \
	[ "${PR_MERGE_APPROVED_REPO:-}" != "$repo" ] || \
	[ "${PR_MERGE_APPROVED_PR:-}" != "$pr_number" ]; then
	cat >&2 <<MSG

⛔ pr-merge-guard: explicit approval required before merging a PR/MR.

Approval packet to show the user:
- Repo: $repo
- PR: #$pr_number $pr_title
- URL: $pr_url
- Branches: $head_ref -> $base_ref
- State: $state, draft: $is_draft
- Mergeability: $mergeable / $merge_state
- Merge method: $method
- Delete branch: $delete_branch
- Commit subject: ${subject:-<gh default>}
- Commit body/body-file: ${body:-${body_file:-<gh default>}}

Only after the user explicitly approves merging this exact PR in this turn,
rerun with:

  PR_MERGE_APPROVED=1 \
  PR_MERGE_APPROVED_REPO="$repo" \
  PR_MERGE_APPROVED_PR="$pr_number" \
  $0 --repo "$repo" --pr "$pr_number" --method "$method" ...

Do not treat PR creation, merge order, reviewer pass, or Linear Done as merge
approval.
MSG
	exit 1
fi

args=(pr merge "$pr_number" --repo "$repo" "$method_flag")
if [ "$delete_branch" -eq 1 ]; then
	args+=(--delete-branch)
fi
if [ -n "$subject" ]; then
	args+=(--subject "$subject")
fi
if [ -n "$body" ]; then
	args+=(--body "$body")
fi
if [ -n "$body_file" ]; then
	args+=(--body-file "$body_file")
fi

gh "${args[@]}"
