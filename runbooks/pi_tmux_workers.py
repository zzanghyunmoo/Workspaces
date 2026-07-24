#!/usr/bin/env python3
"""Launch and guard parallel Pi workers in tmux-backed Git worktrees."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterable, Iterator, Sequence
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path, PurePosixPath
from threading import Event
from typing import Any

READ_ONLY_TOOLS = "read,grep,find,ls"
DEFAULT_MAX_WORKERS = 4
NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,39}")
RESOURCE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}")


class WorkerError(RuntimeError):
    """A parallel worker guardrail was not satisfied."""


class PreserveWorkerError(WorkerError):
    """A startup failure whose worktree and metadata must be preserved."""


@dataclass(frozen=True)
class Runtime:
    state_root: Path
    worktree_root: Path
    tmux_bin: str
    pi_bin: str
    max_workers: int


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def run_process(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            input=input_text,
            check=False,
            text=True,
            capture_output=True,
        )
    except OSError as error:
        raise WorkerError(f"cannot run {shlex.join(command)}: {error}") from error
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise WorkerError(f"{shlex.join(command)}: {detail}")
    return result


def find_tool(command: str, *, label: str) -> str:
    if os.path.sep in command:
        path = Path(command).expanduser().resolve()
        try:
            available = path.is_file() and os.access(path, os.X_OK)
        except OSError as error:
            raise WorkerError(f"cannot inspect {label} executable: {path}") from error
        if not available:
            raise WorkerError(f"{label} executable is unavailable: {path}")
        return str(path)
    resolved = shutil.which(command)
    if not resolved:
        raise WorkerError(f"{label} executable is unavailable: {command}")
    return resolved


def runtime_from_environment() -> Runtime:
    state_root = Path(
        os.environ.get(
            "PI_TMUX_STATE_ROOT",
            Path.home() / ".local" / "state" / "pi-tmux-workers",
        )
    ).expanduser()
    worktree_root = Path(
        os.environ.get("PI_TMUX_WORKTREE_ROOT", Path.home() / ".pi" / "worktrees")
    ).expanduser()
    raw_max = os.environ.get("PI_TMUX_MAX_WORKERS", str(DEFAULT_MAX_WORKERS))
    try:
        max_workers = int(raw_max)
    except ValueError as error:
        raise WorkerError("PI_TMUX_MAX_WORKERS must be an integer") from error
    if max_workers < 1 or max_workers > 16:
        raise WorkerError("PI_TMUX_MAX_WORKERS must be between 1 and 16")
    return Runtime(
        state_root=state_root.resolve(),
        worktree_root=worktree_root.resolve(),
        tmux_bin=find_tool(os.environ.get("PI_TMUX_TMUX_BIN", "tmux"), label="tmux"),
        pi_bin=find_tool(os.environ.get("PI_TMUX_PI_BIN", "pi"), label="Pi"),
        max_workers=max_workers,
    )


def validate_name(value: str, *, label: str) -> str:
    if not NAME_PATTERN.fullmatch(value):
        raise WorkerError(
            f"{label} must match {NAME_PATTERN.pattern!r}; received {value!r}"
        )
    return value


def normalize_scope(raw: str) -> str:
    value = raw.strip().replace("\\", "/")
    if not value:
        raise WorkerError("scope cannot be empty")
    if any(character in value for character in ("\0", "\n", "\r", "\t")):
        raise WorkerError("scope cannot contain control characters")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise WorkerError(f"scope must be repo-relative without '..': {raw}")
    normalized = path.as_posix()
    if normalized == ".git" or normalized.startswith(".git/"):
        raise WorkerError("scope cannot include Git internals")
    return normalized


def normalize_resource(raw: str) -> str:
    value = raw.strip()
    if not RESOURCE_PATTERN.fullmatch(value):
        raise WorkerError(
            "resource must contain only letters, digits, '.', '_', ':', '/', or '-'"
        )
    return value


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def scopes_overlap(left: str, right: str) -> bool:
    normalized_left = left.casefold()
    normalized_right = right.casefold()
    if normalized_left == "." or normalized_right == ".":
        return True
    return (
        normalized_left == normalized_right
        or normalized_left.startswith(f"{normalized_right}/")
        or normalized_right.startswith(f"{normalized_left}/")
    )


def path_is_in_scope(path: str, scopes: Sequence[str]) -> bool:
    normalized_path = path.casefold()
    return any(
        scope == "."
        or normalized_path == scope.casefold()
        or normalized_path.startswith(f"{scope.casefold()}/")
        for scope in scopes
    )


def ensure_private_directory(path: Path, *, root: Path | None = None) -> None:
    resolved_path = path.resolve()
    if root is not None:
        resolved_root = root.resolve()
        if (
            resolved_path != resolved_root
            and resolved_root not in resolved_path.parents
        ):
            raise WorkerError(
                f"refusing to create directory outside managed root: {path}"
            )
    path.mkdir(parents=True, exist_ok=True)
    resolved_path.chmod(0o700)


@contextmanager
def state_lock(runtime: Runtime) -> Iterator[None]:
    ensure_private_directory(runtime.state_root)
    lock_path = runtime.state_root / ".lock"
    try:
        # pi-lens-ignore: python-path-traversal - fixed filename under managed state root
        lock_file = lock_path.open("a+", encoding="utf-8")
    except OSError as error:
        raise WorkerError(f"cannot open worker state lock: {lock_path}") from error
    with lock_file:
        try:
            lock_path.chmod(0o600)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        except OSError as error:
            raise WorkerError(
                f"cannot acquire worker state lock: {lock_path}"
            ) from error
        yield


def state_locked(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(args: argparse.Namespace, runtime: Runtime) -> Any:
        with state_lock(runtime):
            return function(args, runtime)

    return wrapper


def write_private_text(path: Path, text: str, *, root: Path) -> None:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise WorkerError(f"refusing to write outside managed state root: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    parent_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        parent_flags |= os.O_DIRECTORY
    temporary_name = f".{resolved_path.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    parent_descriptor: int | None = None
    file_descriptor: int | None = None
    temporary_created = False
    try:
        parent_descriptor = os.open(  # pi-lens-ignore: python-path-traversal
            resolved_path.parent,
            parent_flags,
        )
        file_descriptor = os.open(  # pi-lens-ignore: python-path-traversal
            temporary_name,
            flags,
            0o600,
            dir_fd=parent_descriptor,
        )
        temporary_created = True
        file = os.fdopen(file_descriptor, "w", encoding="utf-8")
        file_descriptor = None
        with file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
            os.fchmod(file.fileno(), 0o600)
        os.replace(
            temporary_name,
            resolved_path.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        temporary_created = False
        os.fsync(parent_descriptor)
    except OSError as error:
        raise WorkerError(
            f"cannot write managed state file: {resolved_path}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        if temporary_created and parent_descriptor is not None:
            with suppress(FileNotFoundError):
                os.unlink(  # pi-lens-ignore: python-path-traversal - constrained dirfd
                    # pi-lens-ignore: python-path-traversal - random basename
                    temporary_name,
                    dir_fd=parent_descriptor,
                )
        if parent_descriptor is not None:
            os.close(parent_descriptor)


def metadata_path(runtime: Runtime, run_name: str, worker_name: str) -> Path:
    return runtime.state_root / run_name / "workers" / worker_name / "metadata.json"


def worker_directory(runtime: Runtime, run_name: str, worker_name: str) -> Path:
    return metadata_path(runtime, run_name, worker_name).parent


def require_string_list(metadata: dict[str, Any], field: str) -> list[str]:
    value = metadata.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise WorkerError(f"worker metadata field must be a string list: {field}")
    return value


def validate_metadata(
    runtime: Runtime, path: Path, metadata: dict[str, Any]
) -> dict[str, Any]:
    lexical_root = Path(os.path.abspath(runtime.state_root))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
        path.resolve().relative_to(runtime.state_root.resolve())
    except ValueError as error:
        raise WorkerError(
            f"worker metadata is outside managed state root: {path}"
        ) from error
    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise WorkerError(f"worker metadata path cannot contain symlinks: {path}")
    if len(relative.parts) != 4 or relative.parts[1] != "workers":
        raise WorkerError(f"worker metadata path has an invalid shape: {path}")
    path_run, _, path_worker, filename = relative.parts
    if filename != "metadata.json":
        raise WorkerError(f"worker metadata filename is invalid: {path}")
    validate_name(path_run, label="metadata run")
    validate_name(path_worker, label="metadata worker")

    if metadata.get("schema") != "pi-tmux-worker/v1":
        raise WorkerError(f"unsupported worker metadata schema: {path}")
    if metadata.get("run") != path_run or metadata.get("worker") != path_worker:
        raise WorkerError(f"worker metadata identity does not match its path: {path}")
    mode = metadata.get("mode")
    if mode not in {"read", "write"}:
        raise WorkerError(f"worker metadata mode is invalid: {path}")
    expected_session = f"piw-{path_run}-{path_worker}"
    if metadata.get("session") != expected_session:
        raise WorkerError(f"worker metadata session is invalid: {path}")

    raw_repo = metadata.get("repo")
    raw_cwd = metadata.get("cwd")
    if not isinstance(raw_repo, str) or not Path(raw_repo).is_absolute():
        raise WorkerError(f"worker metadata repo must be an absolute path: {path}")
    if not isinstance(raw_cwd, str) or not Path(raw_cwd).is_absolute():
        raise WorkerError(f"worker metadata cwd must be an absolute path: {path}")
    repo = Path(raw_repo).resolve()
    cwd = Path(raw_cwd).resolve()
    raw_common_dir = metadata.get("repo_common_dir")
    if not isinstance(raw_common_dir, str) or not Path(raw_common_dir).is_absolute():
        raise WorkerError(
            f"worker metadata repo_common_dir must be an absolute path: {path}"
        )
    common_dir = Path(raw_common_dir).resolve()
    if not repo.is_dir() or common_dir != git_common_directory(repo):
        raise WorkerError(f"worker metadata repository identity is invalid: {path}")

    scopes = require_string_list(metadata, "scopes")
    resources = require_string_list(metadata, "resources")
    if scopes != unique(normalize_scope(scope) for scope in scopes):
        raise WorkerError(f"worker metadata scopes are invalid or duplicated: {path}")
    if resources != unique(normalize_resource(item) for item in resources):
        raise WorkerError(
            f"worker metadata resources are invalid or duplicated: {path}"
        )

    if mode == "write":
        expected_branch = f"pi-worker/{path_run}/{path_worker}"
        expected_cwd = (
            runtime.worktree_root / repo_identifier(repo) / path_run / path_worker
        ).resolve()
        base_commit = metadata.get("base_commit")
        if metadata.get("branch") != expected_branch or cwd != expected_cwd:
            raise WorkerError(f"worker metadata write identity is invalid: {path}")
        if not scopes:
            raise WorkerError(f"write worker metadata requires scopes: {path}")
        if not isinstance(base_commit, str) or not re.fullmatch(
            r"[0-9a-f]{40,64}", base_commit
        ):
            raise WorkerError(f"worker metadata base_commit is invalid: {path}")
    elif metadata.get("branch") is not None or cwd != repo or scopes:
        raise WorkerError(f"read worker metadata identity is invalid: {path}")
    return metadata


def load_metadata(runtime: Runtime, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WorkerError(f"invalid worker metadata: {path}: {error}") from error
    if not isinstance(value, dict):
        raise WorkerError(f"worker metadata must be a JSON object: {path}")
    return validate_metadata(runtime, path, value)


def save_metadata(runtime: Runtime, path: Path, metadata: dict[str, Any]) -> None:
    ensure_private_directory(path.parent, root=runtime.state_root)
    write_private_text(
        path,
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        root=runtime.state_root,
    )


def iter_metadata(
    runtime: Runtime, *, run_name: str | None = None
) -> Iterable[dict[str, Any]]:
    roots = (
        [runtime.state_root / run_name]
        if run_name
        else sorted(runtime.state_root.glob("*"))
    )
    for run_root in roots:
        workers_root = run_root / "workers"
        if not workers_root.is_dir():
            continue
        for path in sorted(workers_root.glob("*/metadata.json")):
            yield load_metadata(runtime, path)


def tmux_target(session: str) -> str:
    return f"={session}"


def tmux_pane_target(session: str) -> str:
    return f"={session}:"


def tmux_has_session(runtime: Runtime, session: str) -> bool:
    result = run_process(
        [runtime.tmux_bin, "has-session", "-t", tmux_target(session)],
        check=False,
    )
    if result.returncode == 0:
        return True
    detail = (result.stderr or result.stdout).strip().lower()
    absent = (
        detail == "no sessions"
        or (
            detail.startswith("can't find session: ")
            and len(detail) > len("can't find session: ")
        )
        or (
            detail.startswith("no server running on ")
            and len(detail) > len("no server running on ")
        )
        or (
            detail.startswith("error connecting to ")
            and detail.endswith(" (no such file or directory)")
        )
    )
    if absent:
        return False
    raise WorkerError(
        f"cannot determine tmux session state for {session}: "
        f"{detail or f'exit {result.returncode}'}"
    )


def active_worker_count(runtime: Runtime) -> int:
    return sum(
        1
        for metadata in iter_metadata(runtime)
        if tmux_has_session(runtime, str(metadata["session"]))
    )


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_process(["git", *args], cwd=repo, check=check)


def resolve_repo(raw_repo: str) -> Path:
    candidate = Path(raw_repo).expanduser().resolve()
    result = git(candidate, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def git_common_directory(repo: Path) -> Path:
    result = git(
        repo,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
    )
    return Path(result.stdout.strip()).resolve()


def index_visibility_paths(worktree: Path) -> list[str]:
    result = git(worktree, "ls-files", "-v", "-z")
    paths: list[str] = []
    for record in result.stdout.split("\0"):
        if len(record) < 3 or record[1] != " ":
            continue
        tag = record[0]
        if tag == "S" or tag.islower():
            paths.append(record[2:])
    return sorted(paths)


def require_clean_repo(repo: Path) -> None:
    result = git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignore-submodules=none",
    )
    hidden_paths = index_visibility_paths(repo)
    if result.stdout.strip() or hidden_paths:
        preview_lines = result.stdout.splitlines()[:12]
        preview_lines.extend(f"index-hidden: {path}" for path in hidden_paths[:12])
        preview = "\n".join(preview_lines)
        raise WorkerError(
            "write workers require a clean base checkout without hidden index flags; "
            f"preserve or finish existing changes first:\n{preview}"
        )


def initialized_submodule_paths(worktree: Path) -> list[Path]:
    result = git(worktree, "ls-files", "--stage", "-z")
    paths: list[Path] = []
    for record in result.stdout.split("\0"):
        if not record or "\t" not in record:
            continue
        metadata, relative_path = record.split("\t", 1)
        if metadata.split(" ", 1)[0] != "160000":
            continue
        candidate = worktree / relative_path
        if not candidate.is_dir():
            continue
        probe = git(candidate, "rev-parse", "--show-toplevel", check=False)
        if (
            probe.returncode == 0
            and Path(probe.stdout.strip()).resolve() == candidate.resolve()
        ):
            paths.append(Path(relative_path))
    return paths


def working_tree_paths(
    worktree: Path, *, seen_common_dirs: set[Path] | None = None
) -> list[str]:
    commands = (
        ("diff", "--no-renames", "--ignore-submodules=none", "--name-only", "-z"),
        (
            "diff",
            "--cached",
            "--no-renames",
            "--ignore-submodules=none",
            "--name-only",
            "-z",
        ),
        ("ls-files", "--others", "--exclude-standard", "-z"),
        ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
    )
    seen = seen_common_dirs if seen_common_dirs is not None else set()
    common_dir = git_common_directory(worktree)
    if common_dir in seen:
        return []
    seen.add(common_dir)

    paths: set[str] = set(index_visibility_paths(worktree))
    for command in commands:
        result = git(worktree, *command)
        paths.update(item for item in result.stdout.split("\0") if item)
    for submodule_path in initialized_submodule_paths(worktree):
        child = worktree / submodule_path
        for child_path in working_tree_paths(child, seen_common_dirs=seen):
            paths.add(f"{submodule_path.as_posix()}/{child_path}")
    return sorted(paths)


def guarded_changed_paths(metadata: dict[str, Any]) -> list[str]:
    worktree = Path(str(metadata["cwd"]))
    if not worktree.is_dir():
        return ["<missing-worktree>"]
    paths = set(working_tree_paths(worktree))
    base_commit = str(metadata["base_commit"])
    committed = git(
        worktree,
        "diff",
        "--no-renames",
        "--ignore-submodules=none",
        "--name-only",
        "-z",
        base_commit,
        "HEAD",
    )
    paths.update(item for item in committed.stdout.split("\0") if item)
    return sorted(paths)


def scope_violations(metadata: dict[str, Any]) -> list[str]:
    if metadata.get("mode") != "write":
        return []
    scopes = [str(value) for value in metadata["scopes"]]
    return [
        path
        for path in guarded_changed_paths(metadata)
        if not path_is_in_scope(path, scopes)
    ]


def repo_identifier(repo: Path) -> str:
    digest = hashlib.sha256(str(repo).encode("utf-8")).hexdigest()[:10]
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", repo.name).strip("-") or "repo"
    return f"{safe_name}-{digest}"


def check_contention(
    runtime: Runtime,
    *,
    repo: Path,
    scopes: Sequence[str],
    resources: Sequence[str],
) -> None:
    conflicts: list[str] = []
    for metadata in iter_metadata(runtime):
        if metadata.get("mode") != "write":
            continue
        other_name = f"{metadata.get('run')}/{metadata.get('worker')}"
        if Path(str(metadata["repo_common_dir"])) == git_common_directory(repo):
            for scope in scopes:
                for other_scope in metadata.get("scopes", []):
                    if scopes_overlap(scope, str(other_scope)):
                        conflicts.append(
                            f"scope {scope!r} overlaps {other_name}:{other_scope!r}"
                        )
        shared_resources = sorted(set(resources) & set(metadata.get("resources", [])))
        for resource in shared_resources:
            conflicts.append(f"resource {resource!r} is held by {other_name}")
    if conflicts:
        detail = "\n".join(f"- {conflict}" for conflict in conflicts)
        raise WorkerError(
            "parallel write contention detected; serialize or clean up the existing "
            f"worker:\n{detail}"
        )


def build_prompt(
    *,
    run_name: str,
    worker_name: str,
    mode: str,
    repo: Path,
    cwd: Path,
    branch: str | None,
    scopes: Sequence[str],
    resources: Sequence[str],
    task: str,
) -> str:
    lines = [
        "# Pi tmux worker contract",
        "",
        f"- Run: `{run_name}`",
        f"- Worker: `{worker_name}`",
        f"- Mode: `{mode}`",
        f"- Repository: `{repo}`",
        f"- Working directory: `{cwd}`",
    ]
    if branch:
        lines.append(f"- Worker branch: `{branch}`")
    if scopes:
        lines.append(
            f"- Allowed write scopes: {', '.join(f'`{scope}`' for scope in scopes)}"
        )
    if resources:
        lines.append(
            f"- Reserved resources: {', '.join(f'`{item}`' for item in resources)}"
        )

    lines.extend(
        [
            "",
            "## Mandatory guardrails",
            "",
            "1. Read and follow every applicable AGENTS.md/CLAUDE.md instruction.",
            "2. Do not create other agents, tmux sessions, worktrees, or background workers.",
            "3. Do not push, merge, rebase, delete branches/worktrees, or change remotes.",
            "4. Do not expose secrets, tokens, private hosts, or credential-bearing output.",
        ]
    )
    if mode == "write":
        lines.extend(
            [
                "5. Modify only the declared write scopes. Stop and report if another path is required.",
                "6. Do not run commands that contend for undeclared shared resources.",
                "7. Do not stage or commit. The coordinator owns review, integration, and commits.",
                "8. Run only focused verification that is safe for the reserved resources.",
            ]
        )
    else:
        lines.extend(
            [
                "5. This is a read-only investigation. Do not attempt to mutate files or external systems.",
                "6. Cite repository-relative paths and line numbers for important claims.",
            ]
        )

    lines.extend(
        [
            "",
            "## Final response contract",
            "",
            "Report: outcome, files inspected or changed, verification performed, blockers, and residual risks.",
            "",
            "## Assigned task",
            "",
            task.rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def write_launch_script(
    path: Path,
    *,
    runtime: Runtime,
    prompt_path: Path,
    run_name: str,
    worker_name: str,
    mode: str,
    model: str | None,
    thinking: str | None,
) -> None:
    command = [runtime.pi_bin, "--name", f"{run_name}/{worker_name}"]
    if mode == "read":
        command.extend(["--tools", READ_ONLY_TOOLS])
    if model:
        command.extend(["--model", model])
    if thinking:
        command.extend(["--thinking", thinking])
    command.append(f"@{prompt_path}")
    status_path = path.parent / "process.status"
    content = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -uo pipefail",
            f"printf 'starting\\n' > {shlex.quote(str(status_path))}",
            "set +e",
            shlex.join(command),
            "code=$?",
            f"printf 'exited:%s\\n' \"$code\" > {shlex.quote(str(status_path))}",
            'exit "$code"',
            "",
        ]
    )
    write_private_text(path, content, root=runtime.state_root)
    path.chmod(0o700)


def wait_for_startup_probe() -> None:
    Event().wait(0.2)


def start_tmux_session(
    runtime: Runtime, *, session: str, cwd: Path, launch_script: Path
) -> None:
    shell_command = f"exec {shlex.quote(str(launch_script))}"
    run_process(
        [
            runtime.tmux_bin,
            "new-session",
            "-d",
            "-s",
            session,
            "-c",
            str(cwd),
            shell_command,
        ]
    )
    wait_for_startup_probe()
    try:
        alive = tmux_has_session(runtime, session)
    except WorkerError as error:
        kill = run_process(
            [runtime.tmux_bin, "kill-session", "-t", tmux_target(session)],
            check=False,
        )
        if kill.returncode != 0:
            raise PreserveWorkerError(
                f"tmux state is uncertain; worker state was preserved: {session}"
            ) from error
        raise
    if alive:
        return
    status_path = launch_script.parent / "process.status"
    status = (
        status_path.read_text(encoding="utf-8").strip()
        if status_path.is_file()
        else "no process status"
    )
    raise WorkerError(f"Pi worker exited during startup: {session}: {status}")


def remove_failed_worktree(
    repo: Path, worktree: Path, branch: str, base_commit: str
) -> bool:
    if not worktree.is_dir() or working_tree_paths(worktree):
        return False
    head = git(worktree, "rev-parse", "HEAD", check=False)
    if head.returncode != 0 or head.stdout.strip() != base_commit:
        return False
    removed = git(repo, "worktree", "remove", str(worktree), check=False)
    if removed.returncode != 0:
        return False
    branch_head = git(repo, "rev-parse", branch, check=False)
    if branch_head.returncode == 0 and branch_head.stdout.strip() == base_commit:
        git(repo, "branch", "-D", branch, check=False)
    return True


@state_locked
def start_worker(args: argparse.Namespace, runtime: Runtime) -> None:
    run_name = validate_name(args.run, label="run")
    worker_name = validate_name(args.worker, label="worker")
    worker_dir = worker_directory(runtime, run_name, worker_name)
    metadata_file = worker_dir / "metadata.json"
    if metadata_file.exists():
        raise WorkerError(
            f"worker already exists: {run_name}/{worker_name}; clean it up before reuse"
        )
    if active_worker_count(runtime) >= runtime.max_workers:
        raise WorkerError(
            f"active worker limit reached ({runtime.max_workers}); stop a worker first"
        )

    repo = resolve_repo(args.repo)
    repo_common_dir = git_common_directory(repo)
    task_path = Path(args.task_file).expanduser().resolve()
    if not task_path.is_file():
        raise WorkerError(f"task file does not exist: {task_path}")
    task = task_path.read_text(encoding="utf-8")
    if not task.strip():
        raise WorkerError("task file cannot be empty")

    scopes = unique(normalize_scope(scope) for scope in args.scope)
    resources = unique(normalize_resource(resource) for resource in args.resource)
    if args.mode == "write" and not scopes:
        raise WorkerError("write workers require at least one --scope")
    if args.mode == "read" and scopes:
        raise WorkerError("read workers cannot declare write scopes")

    session = f"piw-{run_name}-{worker_name}"
    if tmux_has_session(runtime, session):
        raise WorkerError(f"tmux session already exists: {session}")

    branch: str | None = None
    base_commit: str | None = None
    cwd = repo
    worktree_created = False
    if args.mode == "write":
        require_clean_repo(repo)
        check_contention(runtime, repo=repo, scopes=scopes, resources=resources)
        base_commit = git(
            repo, "rev-parse", "--verify", f"{args.base}^{{commit}}"
        ).stdout.strip()
        branch = f"pi-worker/{run_name}/{worker_name}"
        git(repo, "check-ref-format", "--branch", branch)
        branch_exists = git(
            repo,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
            check=False,
        )
        if branch_exists.returncode == 0:
            raise WorkerError(f"worker branch already exists: {branch}")
        cwd = runtime.worktree_root / repo_identifier(repo) / run_name / worker_name
        if cwd.exists():
            raise WorkerError(f"worker path already exists: {cwd}")
        ensure_private_directory(cwd.parent, root=runtime.worktree_root)
        git(repo, "worktree", "add", "-b", branch, str(cwd), base_commit)
        worktree_created = True

    start_succeeded = False
    preserve_failed_state = False
    try:
        ensure_private_directory(worker_dir, root=runtime.state_root)
        prompt_path = worker_dir / "prompt.md"
        prompt = build_prompt(
            run_name=run_name,
            worker_name=worker_name,
            mode=args.mode,
            repo=repo,
            cwd=cwd,
            branch=branch,
            scopes=scopes,
            resources=resources,
            task=task,
        )
        write_private_text(prompt_path, prompt, root=runtime.state_root)
        launch_script = worker_dir / "launch.sh"
        write_launch_script(
            launch_script,
            runtime=runtime,
            prompt_path=prompt_path,
            run_name=run_name,
            worker_name=worker_name,
            mode=args.mode,
            model=args.model,
            thinking=args.thinking,
        )
        metadata: dict[str, Any] = {
            "schema": "pi-tmux-worker/v1",
            "run": run_name,
            "worker": worker_name,
            "mode": args.mode,
            "repo": str(repo),
            "repo_common_dir": str(repo_common_dir),
            "cwd": str(cwd),
            "session": session,
            "branch": branch,
            "base": args.base if args.mode == "write" else None,
            "base_commit": base_commit,
            "scopes": scopes,
            "resources": resources,
            "started_at": now_iso(),
        }
        save_metadata(runtime, metadata_file, metadata)
        start_tmux_session(
            runtime,
            session=session,
            cwd=cwd,
            launch_script=launch_script,
        )
        start_succeeded = True
    except PreserveWorkerError:
        preserve_failed_state = True
        raise
    finally:
        if not start_succeeded and not preserve_failed_state:
            safe_to_remove_state = True
            if worktree_created and branch and base_commit:
                safe_to_remove_state = remove_failed_worktree(
                    repo, cwd, branch, base_commit
                )
            if safe_to_remove_state:
                shutil.rmtree(worker_dir, ignore_errors=True)

    print(f"started {run_name}/{worker_name}")
    print(f"session: {session}")
    print(f"cwd: {cwd}")
    if branch:
        print(f"branch: {branch}")
    print(f"monitor: {Path(__file__).name} status --run {run_name}")


def selected_metadata(
    runtime: Runtime,
    *,
    run_name: str,
    worker_name: str | None,
) -> list[dict[str, Any]]:
    validate_name(run_name, label="run")
    if worker_name:
        validate_name(worker_name, label="worker")
        path = metadata_path(runtime, run_name, worker_name)
        if not path.is_file():
            raise WorkerError(f"unknown worker: {run_name}/{worker_name}")
        return [load_metadata(runtime, path)]
    values = list(iter_metadata(runtime, run_name=run_name))
    if not values:
        raise WorkerError(f"run has no workers: {run_name}")
    return values


def format_scope_state(metadata: dict[str, Any]) -> tuple[str, list[str]]:
    if metadata.get("mode") != "write":
        return "n/a", []
    violations = scope_violations(metadata)
    if violations:
        return "VIOLATION:" + ",".join(violations), violations
    changes = guarded_changed_paths(metadata)
    return ("ok" if changes else "clean"), []


@state_locked
def status_workers(args: argparse.Namespace, runtime: Runtime) -> int:
    if args.run:
        values = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)
    else:
        if args.worker:
            raise WorkerError("--worker requires --run")
        values = list(iter_metadata(runtime))
    if not values:
        print("no managed workers")
        return 0

    print("RUN\tWORKER\tMODE\tTMUX\tSCOPE\tBRANCH\tCWD")
    found_violation = False
    for metadata in values:
        tmux_state = (
            "running"
            if tmux_has_session(runtime, str(metadata["session"]))
            else "stopped"
        )
        scope_state, violations = format_scope_state(metadata)
        found_violation = found_violation or bool(violations)
        print(
            "\t".join(
                [
                    str(metadata["run"]),
                    str(metadata["worker"]),
                    str(metadata["mode"]),
                    tmux_state,
                    scope_state,
                    str(metadata.get("branch") or "-"),
                    str(metadata["cwd"]),
                ]
            )
        )
    return 2 if found_violation else 0


def capture_pane(runtime: Runtime, *, session: str, lines: int) -> str:
    result = run_process(
        [
            runtime.tmux_bin,
            "capture-pane",
            "-p",
            "-t",
            tmux_pane_target(session),
            "-S",
            f"-{lines}",
        ]
    )
    return result.stdout


@state_locked
def show_log(args: argparse.Namespace, runtime: Runtime) -> None:
    metadata = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)[0]
    session = str(metadata["session"])
    if tmux_has_session(runtime, session):
        print(capture_pane(runtime, session=session, lines=args.lines), end="")
        return
    artifact = runtime.state_root / args.run / "artifacts" / args.worker / "pane.log"
    if artifact.is_file():
        print(artifact.read_text(encoding="utf-8"), end="")
        return
    raise WorkerError(f"session is stopped and no collected log exists: {session}")


@state_locked
def send_message(args: argparse.Namespace, runtime: Runtime) -> None:
    metadata = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)[0]
    session = str(metadata["session"])
    if not tmux_has_session(runtime, session):
        raise WorkerError(f"worker session is not running: {session}")
    if args.message_file:
        message_path = Path(args.message_file).expanduser().resolve()
        if not message_path.is_file():
            raise WorkerError(f"message file does not exist: {message_path}")
        message = message_path.read_text(encoding="utf-8")
    else:
        message = args.message
    if not message or not message.strip():
        raise WorkerError("message cannot be empty")
    buffer_name = f"piw-{args.run}-{args.worker}-{secrets.token_hex(6)}"
    run_process(
        [runtime.tmux_bin, "load-buffer", "-b", buffer_name, "-"],
        input_text=message,
    )
    try:
        run_process(
            [
                runtime.tmux_bin,
                "paste-buffer",
                "-b",
                buffer_name,
                "-t",
                tmux_pane_target(session),
            ]
        )
        run_process(
            [runtime.tmux_bin, "send-keys", "-t", tmux_pane_target(session), "Enter"]
        )
    finally:
        run_process([runtime.tmux_bin, "delete-buffer", "-b", buffer_name], check=False)
    print(f"sent message to {args.run}/{args.worker}")


@state_locked
def stop_workers(args: argparse.Namespace, runtime: Runtime) -> None:
    values = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)
    for metadata in values:
        session = str(metadata["session"])
        if tmux_has_session(runtime, session):
            run_process([runtime.tmux_bin, "kill-session", "-t", tmux_target(session)])
            metadata["stopped_at"] = now_iso()
            save_metadata(
                runtime,
                metadata_path(runtime, str(metadata["run"]), str(metadata["worker"])),
                metadata,
            )
            print(f"stopped {metadata['run']}/{metadata['worker']}")
        else:
            print(f"already stopped {metadata['run']}/{metadata['worker']}")


@state_locked
def collect_workers(args: argparse.Namespace, runtime: Runtime) -> int:
    values = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)
    found_violation = False
    for metadata in values:
        worker_name = str(metadata["worker"])
        artifact_dir = runtime.state_root / args.run / "artifacts" / worker_name
        ensure_private_directory(artifact_dir, root=runtime.state_root)
        session = str(metadata["session"])
        pane_text = ""
        if tmux_has_session(runtime, session):
            pane_text = capture_pane(runtime, session=session, lines=args.lines)
        elif (artifact_dir / "pane.log").is_file():
            pane_text = (artifact_dir / "pane.log").read_text(encoding="utf-8")
        else:
            pane_text = f"session stopped before pane capture: {session}\n"
        write_private_text(
            artifact_dir / "pane.log", pane_text, root=runtime.state_root
        )
        write_private_text(
            artifact_dir / "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            root=runtime.state_root,
        )

        if metadata.get("mode") == "write":
            cwd = Path(str(metadata["cwd"]))
            paths = guarded_changed_paths(metadata)
            violations = scope_violations(metadata)
            found_violation = found_violation or bool(violations)
            write_private_text(
                artifact_dir / "changed-paths.txt",
                "".join(f"{path}\n" for path in paths),
                root=runtime.state_root,
            )
            if cwd.is_dir():
                committed = git(
                    cwd,
                    "diff",
                    "--no-renames",
                    "--ignore-submodules=none",
                    "--stat",
                    str(metadata["base_commit"]),
                    "HEAD",
                ).stdout
                unstaged = git(cwd, "diff", "--ignore-submodules=none", "--stat").stdout
                staged = git(
                    cwd,
                    "diff",
                    "--cached",
                    "--ignore-submodules=none",
                    "--stat",
                ).stdout
                diff_stat = (
                    "# committed\n"
                    + committed
                    + "\n# unstaged\n"
                    + unstaged
                    + "\n# staged\n"
                    + staged
                )
            else:
                diff_stat = "worktree is missing\n"
            write_private_text(
                artifact_dir / "diff-stat.txt", diff_stat, root=runtime.state_root
            )
            guard_text = (
                "scope_status: violation\nviolations:\n"
                + "".join(f"- {path}\n" for path in violations)
                if violations
                else "scope_status: pass\n"
            )
            write_private_text(
                artifact_dir / "guard.txt", guard_text, root=runtime.state_root
            )
        print(f"collected {metadata['run']}/{worker_name}: {artifact_dir}")
    return 2 if found_violation else 0


def worktree_is_registered(repo: Path, cwd: Path, branch: str) -> bool:
    result = git(repo, "worktree", "list", "--porcelain")
    expected_branch = f"refs/heads/{branch}"
    blocks = result.stdout.strip().split("\n\n")
    for block in blocks:
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        raw_path = fields.get("worktree")
        if (
            raw_path
            and Path(raw_path).resolve() == cwd.resolve()
            and fields.get("branch") == expected_branch
        ):
            return True
    return False


@state_locked
def cleanup_workers(args: argparse.Namespace, runtime: Runtime) -> None:
    values = selected_metadata(runtime, run_name=args.run, worker_name=args.worker)
    failures: list[str] = []
    for metadata in values:
        run_name = str(metadata["run"])
        worker_name = str(metadata["worker"])
        session = str(metadata["session"])
        if tmux_has_session(runtime, session):
            failures.append(f"{run_name}/{worker_name}: stop the tmux session first")
            continue
        if metadata.get("mode") == "write":
            cwd = Path(str(metadata["cwd"]))
            if not cwd.is_dir():
                failures.append(
                    f"{run_name}/{worker_name}: worktree is missing; repair Git registration manually"
                )
                continue
            violations = scope_violations(metadata)
            if violations:
                failures.append(
                    f"{run_name}/{worker_name}: scope violations remain: {', '.join(violations)}"
                )
                continue
            paths = working_tree_paths(cwd)
            if paths:
                failures.append(
                    f"{run_name}/{worker_name}: worktree still has changes: {', '.join(paths)}"
                )
                continue
            repo = Path(str(metadata["repo"]))
            branch = str(metadata["branch"])
            if not worktree_is_registered(repo, cwd, branch):
                failures.append(
                    f"{run_name}/{worker_name}: worktree registration does not match metadata"
                )
                continue
            result = git(repo, "worktree", "remove", str(cwd), check=False)
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip()
                failures.append(f"{run_name}/{worker_name}: {detail}")
                continue
        try:
            shutil.rmtree(worker_directory(runtime, run_name, worker_name))
        except OSError as error:
            failures.append(f"{run_name}/{worker_name}: {error}")
            continue
        print(
            f"cleaned {run_name}/{worker_name}; branch retained: "
            f"{metadata.get('branch') or '-'}"
        )
    if failures:
        raise WorkerError(
            "cleanup refused:\n" + "\n".join(f"- {item}" for item in failures)
        )


def parse_tmux_version(text: str) -> tuple[int, int] | None:
    match = re.search(r"tmux\s+(\d+)\.(\d+)", text)
    if not match:
        return None
    try:
        return int(match.group(1)), int(match.group(2))
    except ValueError:
        return None


def doctor(runtime: Runtime) -> None:
    tmux_version_text = run_process([runtime.tmux_bin, "-V"]).stdout.strip()
    pi_version_text = run_process([runtime.pi_bin, "--version"]).stdout.strip()
    git_version_text = run_process(["git", "--version"]).stdout.strip()
    print(f"Pi: {pi_version_text} ({runtime.pi_bin})")
    print(f"tmux: {tmux_version_text} ({runtime.tmux_bin})")
    print(f"Git: {git_version_text}")
    print(f"inside_tmux: {'yes' if os.environ.get('TMUX') else 'no'}")
    print(f"state_root: {runtime.state_root}")
    print(f"worktree_root: {runtime.worktree_root}")
    print(f"max_workers: {runtime.max_workers}")

    version = parse_tmux_version(tmux_version_text)
    config_path = Path.home() / ".tmux.conf"
    config = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
    if "extended-keys on" not in config:
        print("WARN: add `set -g extended-keys on` to ~/.tmux.conf for Pi key handling")
    if version and version >= (3, 5):
        if "extended-keys-format csi-u" not in config:
            print(
                "WARN: tmux >=3.5 should also use `set -g extended-keys-format csi-u`"
            )
    elif version:
        print(
            "INFO: tmux <3.5 must not set `extended-keys-format csi-u`; "
            "the default xterm format is supported"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Guarded parallel Pi workers using tmux and Git worktrees."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start one managed worker")
    start.add_argument("--run", required=True)
    start.add_argument("--worker", required=True)
    start.add_argument("--mode", choices=("read", "write"), required=True)
    start.add_argument("--repo", default=".")
    start.add_argument("--task-file", required=True)
    start.add_argument("--scope", action="append", default=[])
    start.add_argument("--resource", action="append", default=[])
    start.add_argument("--base", default="HEAD")
    start.add_argument("--model")
    start.add_argument("--thinking")
    start.set_defaults(handler=start_worker)

    status = subparsers.add_parser("status", help="show worker and scope status")
    status.add_argument("--run")
    status.add_argument("--worker")
    status.set_defaults(handler=status_workers)

    log = subparsers.add_parser("log", help="capture recent worker output")
    log.add_argument("--run", required=True)
    log.add_argument("--worker", required=True)
    log.add_argument("--lines", type=int, default=200)
    log.set_defaults(handler=show_log)

    send = subparsers.add_parser("send", help="queue a message in a worker's Pi editor")
    send.add_argument("--run", required=True)
    send.add_argument("--worker", required=True)
    message_group = send.add_mutually_exclusive_group(required=True)
    message_group.add_argument("--message")
    message_group.add_argument("--message-file")
    send.set_defaults(handler=send_message)

    stop = subparsers.add_parser("stop", help="stop one worker or an entire run")
    stop.add_argument("--run", required=True)
    stop.add_argument("--worker")
    stop.set_defaults(handler=stop_workers)

    collect = subparsers.add_parser(
        "collect", help="save logs and bounded Git summaries"
    )
    collect.add_argument("--run", required=True)
    collect.add_argument("--worker")
    collect.add_argument("--lines", type=int, default=500)
    collect.set_defaults(handler=collect_workers)

    cleanup = subparsers.add_parser("cleanup", help="remove stopped, clean worktrees")
    cleanup.add_argument("--run", required=True)
    cleanup.add_argument("--worker")
    cleanup.set_defaults(handler=cleanup_workers)

    doctor_parser = subparsers.add_parser("doctor", help="check Pi/tmux prerequisites")
    doctor_parser.set_defaults(handler=lambda args, runtime: doctor(runtime))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        runtime = runtime_from_environment()
        result = args.handler(args, runtime)
        return result if isinstance(result, int) else 0
    except WorkerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
