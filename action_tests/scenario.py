"""
Module that provides templates for defining integration test scenarios.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, Optional

from .test_repository import TestRepository, git


def assert_that(cond: bool, *msg: str) -> None:
    """
    Asserts that the given `cond` is `True` and otherwise raises an
    `AssertionError` with the given `msg`.

    Args:
        cond (bool) : The condition to check
        *msg (str) : The error message to add to the raised error
    """
    if not cond:
        raise AssertionError(*msg)


def assert_eq(expected: Any, actual: Any, *msg: str) -> None:
    """
    Asserts that the given values match and raises an `AssertionError` with the
    given `msg`.

    Args:
        expected (Any) : The expected value
        actual (Any) : The actual value
        *msg (str) : The error message to add to the raised error
    """
    assert_that(expected == actual, *msg, f"Expected: <{expected}>, Actual: <{actual}>")


def check_commit(
    commit: str,
    expected_name: str,
    expected_email: str,
    expected_msg: Optional[str] = None,
) -> None:
    """ "
    Checks the given commit line for conformance to the expected arguments.

    Args:
        commit (str) : The commit oneline summary of name, email and message
        expected_name (str) : The expected committer name
        expected_email (str) : The expected committer email
        expected_msg (Optional[str]) : The expected commit message or `None` if
                                       it should not be checked
    """
    name, email, *msg = commit.split(":")
    assert_eq(expected_name, name, "Invalid commit author name")
    assert_eq(expected_email, email, "Invalid commit author email")
    if expected_msg:
        assert_eq(expected_msg, ":".join(msg), "Mismatching commit message")


class Scenario(ABC):
    """
    An abstract integration test scenario.
    """

    def __init__(self, name: str, expected_outcome: str) -> None:
        self.name = name
        self.path = Path(".") / "action_tests" / "_files" / name
        self.expected_outcome = expected_outcome

    def assert_files_exist(self, repo: TestRepository, *paths: list[str]) -> None:
        """
        Asserts that the given files exist.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *paths (list[str]) : The (relative) paths to the target files
        """
        for path in paths:
            self.assert_file_exists(repo, *path)

    def assert_files_missing(self, repo: TestRepository, *paths: list[str]) -> None:
        """
        Asserts that the given files do not exist.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *paths (list[str]) : The (relative) paths to the target files
        """
        for path in paths:
            self.assert_file_missing(repo, *path)

    def assert_file_exists(self, repo: TestRepository, *path: str) -> None:
        """
        Asserts that the given file exists.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *path (str) : The (relative) path to the target file
        """
        file_path = repo.local_path.joinpath(*path)
        assert_that(
            file_path.is_file(),
            "File does not exist or is not a regular file:",
            str(file_path),
        )

    def assert_file_missing(self, repo: TestRepository, *path: str) -> None:
        """
        Asserts that the given file does not exist.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
            *path (str) : The (relative) path to the target file
        """
        file_path = repo.local_path.joinpath(*path)
        assert_that(
            not file_path.is_file(),
            "File does exist but shouldn't:",
            str(file_path),
        )

    def get_oneline_log(self, repo: TestRepository) -> str:
        """
        Retrieves the git log output for the current repository in --oneline
        format and using the pattern '%cn:%ce:%s'.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        Returns:
            (str) The log output
        """
        return git(
            "log",
            "--oneline",
            r"--format=%cn:%ce:%s",
            check=True,
            cwd=repo.local_path,
        ).stdout.strip()

    # pylint: disable=line-too-long
    def check_outcome(self, outcome: str) -> None:
        """
        Checks the previous action outcome based on the expected one.
        (see https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#steps-context).

        Args:
            outcome (str) : The outcome of the previously executed action.
        """
        assert_eq(self.expected_outcome, outcome, "Invalid action outcome")

    @abstractmethod
    def verify(self, repo: TestRepository) -> None:
        """
        Verifies this test scenario by checking the commits and files.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory
        """


class ScenarioManager:
    """
    Manages created `Scenarios` and simplifies access and iteration over them.
    """

    def __init__(self, *scenarios: Scenario) -> None:
        # register scenario to simplify access and iteration
        self._scenarios = dict[str, "Scenario"]()
        for s in scenarios:
            self._add_scenario(s)

    def _add_scenario(self, s: Scenario) -> None:
        """
        Registers the given scenario in the `scenarios` dictionary.

        Args:
            s (Scenario) : The test scenario to register.
        """
        assert s.name not in self._scenarios, f"Scenario '{s.name}' already registered."
        self._scenarios[s.name] = s

    def get_scenario(self, name: str) -> Optional["Scenario"]:
        """
        Retrieves the scenario registered under the given `name`.

        Args:
            name (str) : The name that identifies the target scenario

        Returns:
            (Scenario | None) The scenario or `None` if no such scenario is
            registered
        """
        return self._scenarios.get(name, None)

    def scenarios(self) -> Iterable[tuple[str, "Scenario"]]:
        """
        Returns all registered scenarios.

        Returns:
            (Iterable[tuple[str, Scenario]]) an iterable of name-scenario tuples
        """
        return self._scenarios.items()
