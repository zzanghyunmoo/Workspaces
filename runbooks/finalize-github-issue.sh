#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat <<'MSG'
Usage:
  runbooks/finalize-github-issue.sh --workflow-evidence docs/works/WORK.md [--execute]

Without --execute the finalizer performs a dry run. The execute path validates
the completed compound-work/v2 evidence on origin/main, reconciles a partial
prior attempt, removes the open lifecycle label, and closes the Issue with the
completed reason.
MSG
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workflow_gate="$script_dir/compound_workflow_gate.py"
workflow_evidence=""
execute=0

while [ "$#" -gt 0 ]; do
	case "$1" in
	--workflow-evidence)
		workflow_evidence="${2:-}"
		shift 2
		;;
	--execute)
		execute=1
		shift
		;;
	-h | --help)
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

if [ -z "$workflow_evidence" ]; then
	usage >&2
	exit 64
fi

python_command="${COMPOUND_PYTHON:-python3}"
if ! command -v "$python_command" >/dev/null 2>&1; then
	printf 'Python 3 is required to run the GitHub Issue finalizer.\n' >&2
	exit 1
fi

args=(finalize-issue --evidence "$workflow_evidence")
if [ "$execute" -eq 0 ]; then
	args+=(--dry-run)
fi

"$python_command" "$workflow_gate" "${args[@]}"
