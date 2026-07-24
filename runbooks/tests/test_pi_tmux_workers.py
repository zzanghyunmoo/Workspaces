from __future__ import annotations

import argparse
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from threading import Event
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "pi_tmux_workers.py"
SPEC = importlib.util.spec_from_file_location("pi_tmux_workers", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load worker module: {MODULE_PATH}")
WORKERS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WORKERS
SPEC.loader.exec_module(WORKERS)


class PiTmuxWorkersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Worker Test")
        self.git("config", "user.email", "worker@example.test")
        (self.repo / "src/api").mkdir(parents=True)
        (self.repo / "src/ui").mkdir(parents=True)
        (self.repo / "tests/api").mkdir(parents=True)
        (self.repo / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        (self.repo / "src/api/service.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "src/ui/view.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "tests/api/test_service.py").write_text(
            "def test_value():\n    assert True\n", encoding="utf-8"
        )
        self.git("add", ".")
        self.git("commit", "-m", "initial")
        self.task_file = self.root / "task.md"
        self.task_file.write_text("Implement the assigned slice.\n", encoding="utf-8")
        true_bin = "/usr/bin/true"
        self.runtime = WORKERS.Runtime(
            state_root=self.root / "state",
            worktree_root=self.root / "worktrees",
            tmux_bin=true_bin,
            pi_bin=true_bin,
            max_workers=4,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or self.repo,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout

    def start_args(
        self,
        *,
        worker: str,
        mode: str = "write",
        scopes: list[str] | None = None,
        resources: list[str] | None = None,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            run="demo",
            worker=worker,
            mode=mode,
            repo=str(self.repo),
            task_file=str(self.task_file),
            scope=scopes or [],
            resource=resources or [],
            base="HEAD",
            model=None,
            thinking=None,
        )

    def start_worker(self, args: argparse.Namespace) -> None:
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            mock.patch.object(WORKERS, "start_tmux_session") as launch,
        ):
            WORKERS.start_worker(args, self.runtime)
        launch.assert_called_once()

    def load_metadata(self, worker: str) -> dict[str, object]:
        return WORKERS.load_metadata(
            self.runtime,
            WORKERS.metadata_path(self.runtime, "demo", worker),
        )

    def test_write_worker_creates_isolated_worktree_and_contract(self) -> None:
        self.start_worker(
            self.start_args(
                worker="api",
                scopes=["src/api", "tests/api"],
                resources=["test-db"],
            )
        )

        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        self.assertTrue(cwd.is_dir())
        self.assertEqual(
            self.git("branch", "--show-current", cwd=cwd).strip(),
            "pi-worker/demo/api",
        )
        prompt = (
            WORKERS.worker_directory(self.runtime, "demo", "api") / "prompt.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Allowed write scopes: `src/api`, `tests/api`", prompt)
        self.assertIn("Do not stage or commit", prompt)
        self.assertIn("Reserved resources: `test-db`", prompt)

    def test_write_worker_requires_clean_base_checkout(self) -> None:
        (self.repo / "src/api/service.py").write_text("VALUE = 2\n", encoding="utf-8")
        with self.assertRaisesRegex(WORKERS.WorkerError, "clean base checkout"):
            self.start_worker(self.start_args(worker="api", scopes=["src/api"]))

    def test_overlapping_scope_is_blocked_until_existing_worker_is_cleaned(
        self,
    ) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        with self.assertRaisesRegex(WORKERS.WorkerError, "scope 'src' overlaps"):
            self.start_worker(
                self.start_args(worker="backend", scopes=["src"], resources=[])
            )

    def test_shared_resource_is_blocked_across_repositories(self) -> None:
        self.start_worker(
            self.start_args(
                worker="api",
                scopes=["src/api"],
                resources=["port:5000"],
            )
        )
        other_repo = self.root / "other"
        subprocess.run(
            ["git", "clone", "--quiet", str(self.repo), str(other_repo)],
            check=True,
        )
        args = self.start_args(
            worker="ui",
            scopes=["src/ui"],
            resources=["port:5000"],
        )
        args.repo = str(other_repo)
        with self.assertRaisesRegex(WORKERS.WorkerError, "resource 'port:5000'"):
            self.start_worker(args)

    def test_linked_checkout_uses_common_git_identity_for_scope_contention(
        self,
    ) -> None:
        linked = self.root / "linked-checkout"
        self.git("worktree", "add", "-b", "linked-base", str(linked), "HEAD")
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        args = self.start_args(worker="backend", scopes=["src/api"], resources=[])
        args.repo = str(linked)
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            mock.patch.object(WORKERS, "start_tmux_session"),
            self.assertRaisesRegex(WORKERS.WorkerError, "scope 'src/api' overlaps"),
        ):
            WORKERS.start_worker(args, self.runtime)

    def test_read_worker_uses_read_only_pi_tool_allowlist(self) -> None:
        self.start_worker(self.start_args(worker="review", mode="read"))
        metadata = self.load_metadata("review")
        self.assertEqual(metadata["cwd"], str(self.repo.resolve()))
        launch_script = (
            WORKERS.worker_directory(self.runtime, "demo", "review") / "launch.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("--tools read,grep,find,ls", launch_script)
        self.assertNotIn("pi-worker/demo/review", launch_script)

    def test_scope_violation_is_reported_by_status_and_collect(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        (cwd / "src/api/service.py").write_text("VALUE = 2\n", encoding="utf-8")
        (cwd / "src/ui/view.py").write_text("VALUE = 2\n", encoding="utf-8")

        output = io.StringIO()
        status_args = argparse.Namespace(run="demo", worker="api")
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            redirect_stdout(output),
        ):
            status = WORKERS.status_workers(status_args, self.runtime)
        self.assertEqual(status, 2)
        self.assertIn("VIOLATION:src/ui/view.py", output.getvalue())

        collect_args = argparse.Namespace(run="demo", worker="api", lines=100)
        with mock.patch.object(WORKERS, "tmux_has_session", return_value=False):
            collected = WORKERS.collect_workers(collect_args, self.runtime)
        self.assertEqual(collected, 2)
        guard = self.runtime.state_root / "demo/artifacts/api/guard.txt"
        self.assertIn("src/ui/view.py", guard.read_text(encoding="utf-8"))
        diff_stat = self.runtime.state_root / "demo/artifacts/api/diff-stat.txt"
        self.assertTrue(diff_stat.is_file())
        self.assertFalse((diff_stat.parent / "full.patch").exists())

    def test_index_visibility_flags_cannot_hide_changes_from_cleanup(self) -> None:
        flag_pairs = (
            ("--assume-unchanged", "--no-assume-unchanged"),
            ("--skip-worktree", "--no-skip-worktree"),
        )
        for index, (set_flag, clear_flag) in enumerate(flag_pairs, start=1):
            worker = f"hidden{index}"
            self.start_worker(
                self.start_args(worker=worker, scopes=["src/api"], resources=[])
            )
            metadata = self.load_metadata(worker)
            cwd = Path(str(metadata["cwd"]))
            self.git("update-index", set_flag, "src/api/service.py", cwd=cwd)
            (cwd / "src/api/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.assertIn("src/api/service.py", WORKERS.working_tree_paths(cwd))
            cleanup_args = argparse.Namespace(run="demo", worker=worker)
            with (
                mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
                self.assertRaisesRegex(
                    WORKERS.WorkerError, "worktree still has changes"
                ),
            ):
                WORKERS.cleanup_workers(cleanup_args, self.runtime)
            self.git("update-index", clear_flag, "src/api/service.py", cwd=cwd)
            self.git("reset", "--hard", "HEAD", cwd=cwd)
            with mock.patch.object(WORKERS, "tmux_has_session", return_value=False):
                WORKERS.cleanup_workers(cleanup_args, self.runtime)

    def test_ignored_file_inside_initialized_submodule_is_detected(self) -> None:
        submodule_repo = self.root / "submodule-source"
        submodule_repo.mkdir()
        self.git("init", "-b", "main", cwd=submodule_repo)
        self.git("config", "user.name", "Submodule Test", cwd=submodule_repo)
        self.git("config", "user.email", "submodule@example.test", cwd=submodule_repo)
        (submodule_repo / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        (submodule_repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        self.git("add", ".", cwd=submodule_repo)
        self.git("commit", "-m", "submodule initial", cwd=submodule_repo)

        self.git(
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(submodule_repo),
            "deps/sub",
        )
        self.git("commit", "-am", "add submodule")
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        self.git(
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "update",
            "--init",
            cwd=cwd,
        )
        ignored = cwd / "deps/sub/ignored/cache.txt"
        ignored.parent.mkdir()
        ignored.write_text("cache\n", encoding="utf-8")
        self.assertIn(
            "deps/sub/ignored/cache.txt",
            WORKERS.guarded_changed_paths(metadata),
        )

    def test_committed_scope_violation_is_detected_and_blocks_cleanup(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        (cwd / "src/ui/view.py").write_text("VALUE = 2\n", encoding="utf-8")
        self.git("add", "src/ui/view.py", cwd=cwd)
        self.git("commit", "-m", "out of scope", cwd=cwd)

        self.assertEqual(WORKERS.scope_violations(metadata), ["src/ui/view.py"])
        cleanup_args = argparse.Namespace(run="demo", worker="api")
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            self.assertRaisesRegex(WORKERS.WorkerError, "scope violations remain"),
        ):
            WORKERS.cleanup_workers(cleanup_args, self.runtime)

    def test_ignored_untracked_scope_violation_is_detected(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        (cwd / "ignored").mkdir()
        (cwd / "ignored/cache.txt").write_text("secret\n", encoding="utf-8")
        self.assertIn("ignored/cache.txt", WORKERS.guarded_changed_paths(metadata))
        self.assertEqual(WORKERS.scope_violations(metadata), ["ignored/cache.txt"])

    def test_metadata_identity_tampering_is_rejected_before_cleanup(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        path = WORKERS.metadata_path(self.runtime, "demo", "api")
        metadata = WORKERS.load_metadata(self.runtime, path)
        victim = self.root / "victim"
        victim.mkdir()
        (victim / "keep.txt").write_text("keep\n", encoding="utf-8")
        metadata["cwd"] = str(victim)
        WORKERS.write_private_text(
            path,
            WORKERS.json.dumps(metadata, ensure_ascii=False),
            root=self.runtime.state_root,
        )

        cleanup_args = argparse.Namespace(run="demo", worker="api")
        with self.assertRaisesRegex(WORKERS.WorkerError, "write identity is invalid"):
            WORKERS.cleanup_workers(cleanup_args, self.runtime)
        self.assertTrue((victim / "keep.txt").is_file())

    def test_tmux_state_errors_fail_closed_and_targets_exact_session(self) -> None:
        permission_error = subprocess.CompletedProcess(
            args=["tmux"], returncode=2, stdout="", stderr="permission denied"
        )
        with (
            mock.patch.object(WORKERS, "run_process", return_value=permission_error),
            self.assertRaisesRegex(WORKERS.WorkerError, "cannot determine"),
        ):
            WORKERS.tmux_has_session(self.runtime, "piw-demo-api")

        unrelated_missing_path = subprocess.CompletedProcess(
            args=["tmux"],
            returncode=2,
            stdout="",
            stderr="failed to inspect socket: No such file or directory",
        )
        with (
            mock.patch.object(
                WORKERS, "run_process", return_value=unrelated_missing_path
            ),
            self.assertRaisesRegex(WORKERS.WorkerError, "cannot determine"),
        ):
            WORKERS.tmux_has_session(self.runtime, "piw-demo-api")

        missing = subprocess.CompletedProcess(
            args=["tmux"],
            returncode=1,
            stdout="",
            stderr="can't find session: piw-demo-api",
        )
        with mock.patch.object(WORKERS, "run_process", return_value=missing) as run:
            self.assertFalse(WORKERS.tmux_has_session(self.runtime, "piw-demo-api"))
        self.assertIn("=piw-demo-api", run.call_args.args[0])

    def test_metadata_symlink_redirection_is_rejected(self) -> None:
        self.start_worker(self.start_args(worker="api", mode="read"))
        self.start_worker(self.start_args(worker="review", mode="read"))
        api_dir = WORKERS.worker_directory(self.runtime, "demo", "api")
        review_dir = WORKERS.worker_directory(self.runtime, "demo", "review")
        for child in api_dir.iterdir():
            child.unlink()
        api_dir.rmdir()
        api_dir.symlink_to(review_dir, target_is_directory=True)

        with self.assertRaisesRegex(WORKERS.WorkerError, "cannot contain symlinks"):
            WORKERS.selected_metadata(self.runtime, run_name="demo", worker_name="api")

    def test_atomic_state_write_preserves_previous_file_on_replace_failure(
        self,
    ) -> None:
        directory = self.runtime.state_root / "atomic"
        WORKERS.ensure_private_directory(directory, root=self.runtime.state_root)
        path = directory / "metadata.json"
        WORKERS.write_private_text(path, "old\n", root=self.runtime.state_root)
        with (
            mock.patch.object(WORKERS.os, "replace", side_effect=OSError("disk full")),
            self.assertRaisesRegex(WORKERS.WorkerError, "cannot write"),
        ):
            WORKERS.write_private_text(path, "new\n", root=self.runtime.state_root)
        self.assertEqual(path.read_text(encoding="utf-8"), "old\n")
        self.assertEqual(
            sorted(item.name for item in directory.iterdir()), ["metadata.json"]
        )

    def test_startup_failure_preserves_modified_worktree_and_metadata(self) -> None:
        args = self.start_args(worker="api", scopes=["src/api"], resources=[])

        def fail_after_write(
            runtime: object,
            *,
            session: str,
            cwd: Path,
            launch_script: Path,
        ) -> None:
            del runtime, session, launch_script
            (cwd / "src/api/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            raise WORKERS.WorkerError("startup failed")

        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            mock.patch.object(
                WORKERS, "start_tmux_session", side_effect=fail_after_write
            ),
            self.assertRaisesRegex(WORKERS.WorkerError, "startup failed"),
        ):
            WORKERS.start_worker(args, self.runtime)

        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        self.assertTrue(cwd.is_dir())
        self.assertTrue(WORKERS.metadata_path(self.runtime, "demo", "api").is_file())
        self.assertIn("src/api/service.py", WORKERS.guarded_changed_paths(metadata))

    def test_tmux_launch_quotes_state_paths_and_detects_early_exit(self) -> None:
        launch_script = self.root / "state with spaces" / "launch.sh"
        launch_script.parent.mkdir()
        launch_script.write_text("#!/bin/sh\nexit 2\n", encoding="utf-8")
        (launch_script.parent / "process.status").write_text(
            "exited:2\n", encoding="utf-8"
        )
        with (
            mock.patch.object(WORKERS, "run_process") as run,
            mock.patch.object(WORKERS, "wait_for_startup_probe"),
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            self.assertRaisesRegex(WORKERS.WorkerError, "exited:2"),
        ):
            WORKERS.start_tmux_session(
                self.runtime,
                session="piw-demo-api",
                cwd=self.repo,
                launch_script=launch_script,
            )
        shell_command = run.call_args_list[0].args[0][-1]
        self.assertEqual(
            shell_command,
            f"exec {WORKERS.shlex.quote(str(launch_script))}",
        )

    def test_cleanup_refuses_missing_worktree(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "remove", "--force", str(cwd)],
            check=True,
        )
        cleanup_args = argparse.Namespace(run="demo", worker="api")
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            self.assertRaisesRegex(WORKERS.WorkerError, "worktree is missing"),
        ):
            WORKERS.cleanup_workers(cleanup_args, self.runtime)

    def test_cleanup_refuses_dirty_worktree_and_retains_branch_when_clean(self) -> None:
        self.start_worker(
            self.start_args(worker="api", scopes=["src/api"], resources=[])
        )
        metadata = self.load_metadata("api")
        cwd = Path(str(metadata["cwd"]))
        (cwd / "src/api/service.py").write_text("VALUE = 2\n", encoding="utf-8")
        cleanup_args = argparse.Namespace(run="demo", worker="api")
        with (
            mock.patch.object(WORKERS, "tmux_has_session", return_value=False),
            self.assertRaisesRegex(WORKERS.WorkerError, "worktree still has changes"),
        ):
            WORKERS.cleanup_workers(cleanup_args, self.runtime)

        self.git("reset", "--hard", "HEAD", cwd=cwd)
        with mock.patch.object(WORKERS, "tmux_has_session", return_value=False):
            WORKERS.cleanup_workers(cleanup_args, self.runtime)
        self.assertFalse(cwd.exists())
        branches = self.git("branch", "--list", "pi-worker/demo/api")
        self.assertIn("pi-worker/demo/api", branches)

    def test_state_lock_serializes_separate_processes(self) -> None:
        ready = self.root / "child-ready"
        acquired = self.root / "child-acquired"
        script = f"""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('pi_tmux_workers_child', {str(MODULE_PATH)!r})
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)
runtime = module.Runtime(
    state_root=Path({str(self.runtime.state_root)!r}),
    worktree_root=Path({str(self.runtime.worktree_root)!r}),
    tmux_bin='/usr/bin/true',
    pi_bin='/usr/bin/true',
    max_workers=4,
)
Path({str(ready)!r}).write_text('ready', encoding='utf-8')
with module.state_lock(runtime):
    Path({str(acquired)!r}).write_text('acquired', encoding='utf-8')
"""
        with WORKERS.state_lock(self.runtime):
            child = subprocess.Popen([sys.executable, "-c", script])
            for _ in range(100):
                if ready.exists():
                    break
                Event().wait(0.01)
            self.assertTrue(ready.exists())
            self.assertFalse(acquired.exists())
        self.assertEqual(child.wait(timeout=5), 0)
        self.assertTrue(acquired.exists())

    def test_scope_normalization_and_overlap_rules(self) -> None:
        self.assertEqual(WORKERS.normalize_scope("src\\api"), "src/api")
        self.assertTrue(WORKERS.scopes_overlap("src", "src/api"))
        self.assertFalse(WORKERS.scopes_overlap("src/api", "src/ui"))
        self.assertTrue(WORKERS.path_is_in_scope("src/api/a.py", ["src/api"]))
        with self.assertRaisesRegex(WORKERS.WorkerError, "without '..'"):
            WORKERS.normalize_scope("../outside")
        with self.assertRaisesRegex(WORKERS.WorkerError, "Git internals"):
            WORKERS.normalize_scope(".git/hooks")

    def test_tmux_version_parser_handles_supported_formats(self) -> None:
        self.assertEqual(WORKERS.parse_tmux_version("tmux 3.4"), (3, 4))
        self.assertEqual(WORKERS.parse_tmux_version("tmux 3.5a"), (3, 5))
        self.assertIsNone(WORKERS.parse_tmux_version("unknown"))


if __name__ == "__main__":
    unittest.main()
