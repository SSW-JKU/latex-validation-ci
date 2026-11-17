"""Defines configuration environments and classes."""

import json
from argparse import Namespace
from pathlib import Path
from typing import Any, Final

EXERCISE_DIR_NAME: Final = "Aufgabe"
LESSON_DIR_NAME: Final = "Unterricht"
LESSON_SUFFIX: Final = "_Lernziele"
SOLUTION_SUFFIX: Final = "_solution"

# Determines whether the "old" solution build system should be used
OLD_SOLUTION_BUILD_SEMESTER_CUTOFF: Final = 23


class Config:
    """Base configuration object that tracks all directory paths.

    Parses the configuration from an initially provided JSON configuration file.
    """

    active_semester: str
    workdir: Path
    exercises: list[str]
    exercises_entry_point: str
    lesson_entry_point: str
    options: Namespace

    def __init__(self, options: Namespace) -> None:
        """Create a new configuration.

        Parse the JSON file referenced by `options.config` and use
        `options.workdir` as a base path.

        Args:
            options (Namespace) : The passed CLI options.

        """
        with Path(options.config).open(encoding="UTF-8") as cf:
            json_config: dict[str, Any] = json.load(cf)

        self.active_semester = json_config["activeSemester"]
        self.workdir = options.workdir.joinpath(self.active_semester)
        self.exercises = json_config["exercises"]
        self.exercises_entry_point = json_config["entryPoints"]["exercise"]
        self.lesson_entry_point = json_config["entryPoints"]["lesson"]

    def determine_semester(self) -> int:
        """Extract the semester number from the `active_semester` string.

        Returns:
            (int) The parsed semester number.

        """
        return int(self.active_semester[:2])
