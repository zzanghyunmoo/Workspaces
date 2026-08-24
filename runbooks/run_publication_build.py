#!/usr/bin/env python3
"""Run the public site build with a bounded, process-group timeout."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        process.wait()


def run_build(repo: Path, timeout_seconds: int) -> int:
    if timeout_seconds <= 0:
        raise ValueError("timeout must be positive")
    root = repo.expanduser().resolve()
    process = subprocess.Popen(
        ["npm", "run", "build"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        return process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        terminate_process_group(process)
        return 124


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--timeout", required=True, type=int)
    args = parser.parse_args()
    try:
        return run_build(args.repo, args.timeout)
    except (OSError, ValueError):
        return 125


if __name__ == "__main__":
    sys.exit(main())
