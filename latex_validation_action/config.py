"""
Defines configuration environments and classes.
"""

from argparse import Namespace
from pathlib import Path
import json

EXERCISE_DIR_NAME = 'Aufgabe'
LESSON_DIR_NAME = 'Unterricht'
LESSON_SUFFIX = '_Lernziele'
SOLUTION_SUFFIX = '_solution'

# Determines whether the "old" solution build system should be used
OLD_SOLUTION_BUILD_SEMESTER_CUTOFF = 23


class Config():
    """
    Base configuration object that tracks all directory
    paths by parsing them from an initially provided JSON configuration file.
    """

    def __init__(self, options: Namespace) -> None:
        """
        Creates a new configuration by parsing the given JSON and using the
        provided working directory as a base path.

        Args:
            config_file (Path) : The path to the initial config JSON.
            workdir (Path) : The directory that should be used as a base path.
            options (Namespace) : The passed CLI options.
        """
        with open(options.config, 'r', encoding='UTF-8') as cf:
            json_config = json.load(cf)
            self.active_semester: str = json_config['activeSemester']
            self.workdir: Path = options.workdir.joinpath(self.active_semester)
            self.exercises: list[str] = json_config['exercises']
            self.exercises_entry_point: str = json_config['entryPoints']['exercise']
            self.lesson_entry_point: str = json_config['entryPoints']['lesson']
            self.options = options

    def determine_semester(self) -> int:
        """
        Extracts the semester number from the `self.active_semester` string.

        Returns:
            (int) The parsed semester number.
        """
        return int(self.active_semester[:2])
