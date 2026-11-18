"""Defines configuration environments and classes."""

from pathlib import Path
from typing import Final

EXERCISE_DIR_NAME: Final = "Aufgabe"
LESSON_DIR_NAME: Final = "Unterricht"
LESSON_SUFFIX: Final = "_Lernziele"
SOLUTION_SUFFIX: Final = "_solution"

# Determines whether the "old" solution build system should be used
OLD_SOLUTION_BUILD_SEMESTER_CUTOFF: Final = 23


class Config:
    """Base configuration object that tracks all directory paths."""

    active_semester: str
    workdir: Path

    def __init__(self, active_semester: str, workdir: Path) -> None:
        """Create a new configuration.

        Args:
            active_semester (str) : The semester to use for the configuration.
            workdir (Path) : The base path to use for the configuration.

        """
        self.active_semester = active_semester
        self.workdir = workdir.joinpath(active_semester)
