#!/usr/bin/env python

"""
Preparation and verification script for the integration tests.
This script prepares the test repositories and sets up the test files for the integration tests or
performs verification after the action was executed.
"""

import subprocess
import shutil
import argparse

from .test_repository import TestRepository, git, REMOTE_PATH, LOCAL_PATH
from .scenarios import SCENARIOS


def _check_git_installed() -> None:
    try:
        git("--version")
        print("Git is available.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise EnvironmentError("Git is not installed or not found in PATH.") from e


def _prepare() -> None:
    print("Setting up repositories and files")

    for name, scenario in SCENARIOS.scenarios():
        print("-- Setting up scenario:", name)
        test_repo = TestRepository(name, REMOTE_PATH, LOCAL_PATH)
        test_repo.initialize_repo()
        print("---- Remote path:", test_repo.remote_path)
        print("---- Local path:", test_repo.local_path)

        shutil.copytree(scenario.path, test_repo.local_path, dirs_exist_ok=True)

        test_repo.commit_all("Initial commit")
        test_repo.push()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set up test git repositories for testing and verify "
        "their contents afterwards."
    )
    parser.add_argument(
        "outcome",
        type=str,
        nargs="?",
        help="The outcome of the action execution.",
    )
    parser.add_argument(
        "--check",
        type=str,
        required=False,
        help="Performs checks for the given scenario.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    _check_git_installed()
    args = _parse_args()
    if args.check:
        s = SCENARIOS.get_scenario(args.check)
        if s is None:
            raise ValueError(f"Scenario '{args.check}' not found.")
        print(f"Verifying integration test outputs for '{s.name}'")
        repo = TestRepository(s.name, REMOTE_PATH, LOCAL_PATH)
        s.check_outcome(args.outcome)
        s.verify(repo)
    else:
        _prepare()
