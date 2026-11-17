#!/usr/bin/env python
import argparse
import logging as log
import os
import re
import subprocess
from pathlib import Path

from .config import Config
from .summary_md_file import SummaryMdFile
from .tex_checks_utils import count_total_warnings, get_repo_and_action_path_env_variables

already_checked_files: set[str] = set()
nr_of_total_warnings_for_zip: int = 0
nr_of_total_warnings_for_md_file: int = 0

# CHKTEX_EXEC_REL_PATH = 'chktex'
CHKTEX_CONFIG_FILE_REL_PATH = "chktexrc.in"


class LintNotification:
    file: str
    type: str
    line: int
    message: str
    code_snippet: str

    def __init__(self, file: str, type: str, line: int, message: str, code_snippet: str) -> None:
        self.file = file
        self.type = type
        self.line = line
        self.message = message
        self.code_snippet = code_snippet

    def __repr__(self) -> str:
        return (
            f"LintNotification(file={self.file},"
            f"type={self.type}, line={self.line}, message={self.message}, code_snippet={self.code_snippet})"
        )


def find_line_number(filename: str | Path, target_string: str) -> int | None:
    with open(filename, encoding="UTF-8") as file:
        for line_number, line in enumerate(file, start=1):
            if target_string in line:
                return line_number
    return None


def uncomment_prelude_import(tex_file_abs_path: str | Path, target_line: int, do_uncomment: bool) -> None:
    if do_uncomment:
        replacement = "%\\input{../../prelude}\n"
    else:
        replacement = "\\input{../../prelude}\n"

    with open(tex_file_abs_path, encoding="UTF-8") as file:
        lines = file.readlines()
        with open(tex_file_abs_path, "w") as updated_file:
            if target_line <= len(lines):
                lines[target_line - 1] = replacement
                # file.seek(0)
                updated_file.writelines(lines)
            else:
                print(f"Line {target_line} does not exist in the file.")


def analize_report(base_dir: str, command: str, target_file_path: str, summary_file: SummaryMdFile) -> None:
    """Performs linting (with chktex) on specified tex file,
    collects the chktex-warnings/errors/messages (notifications) and writes them to a report file (md-file).

    Args:
        base_dir (str): Path of repo base directory.
        command (str): chktex command to perform linting on a specific chktex file, considering a chktex-config file
        target_file_path(str): relative path to tex file to be linted
        summary_file (SummaryMdFile): summary file object where are notifications are written (md-file)

    """
    try:
        log.info(f"command: {command}")
        output = subprocess.check_output(command, shell=True, encoding="utf-8", errors="replace")
        # log.info(output)
        lines = output.split("\n")

        # Run over lines of raw chktex-report and parse warnings/errors/messages into objects LintNotification
        i = 0
        files: set[str] = set()
        notifications: list[LintNotification] = []
        nr_of_notifications: dict[str, int] = {"Error": 0, "Warning": 0, "Message": 0}
        while i < len(lines):
            first_line = lines[i]
            second_line = lines[i + 1] if i + 1 < len(lines) else ""
            third_line = lines[i + 2] if i + 2 < len(lines) else ""
            step = 3

            # Match lines like: "Warning 21, 43, This command might not be intended."
            pattern = "(.+), (Warning|Error|Message) (\\d+), (\\d+), (.+)"
            match = re.match(pattern, first_line)
            if match:
                file = match.group(1).removeprefix(base_dir)
                file = os.path.abspath(file)
                files.add(file)

                # Avoid checking tex files twice
                if file not in already_checked_files:
                    global nr_of_total_warnings_for_md_file
                    nr_of_total_warnings_for_md_file += 1
                    type = f"{match.group(2)} {match.group(3)}"
                    line = int(match.group(4))
                    message = match.group(5)
                    code_snippet = f"{second_line}\n{third_line}"
                    notification_kind = type.split(maxsplit=1)[0]
                    nr_of_notifications[notification_kind] = nr_of_notifications[notification_kind] + 1

                    # A message may span across multiple lines
                    while (i + step) < len(lines) and not re.match(pattern, lines[i + step]):
                        message = f"{message}\n{lines[i + step]}"
                        step = step + 1

                    notifications.append(LintNotification(file, type, line, message, code_snippet))
            else:
                step = 1
            i = i + step

        if notifications:
            # Write report to summary md file
            summary_file.add_overview_line(
                target_file_path,
                nr_of_notifications["Error"],
                nr_of_notifications["Warning"],
                nr_of_notifications["Message"],
            )

            for notification in notifications:
                summary_file.add_notification_entry(notification)
        else:
            log.info(f"After chktex-run notifications are: {notifications}")

        # Update checked files
        already_checked_files.update(files)

    except subprocess.CalledProcessError as e:
        output = str(e.output, "utf-8")
        print(output)


def use_chktex(
    tex_file_path: str,
    create_zipped_report: bool,
    create_md_summary: bool,
    summary_file: SummaryMdFile | None,
) -> None:
    """Performs linting on the tex file specified,
    the resulting chktex-warnings/messages/errors (notifications) will be provided, depending on option:
        as captured-console-output in html or
        as md-file.

    Args:
        tex_file_path (str): Path to tex file to be linted.
        create_zipped_report (bool): Option to capture chktex's console output into a html file.
        create_md_summary (bool): Option to transform chktex's notifications to a md-report file.
        summary_file (SummaryMdFile | None): summary file object where are notifications are written (md-file)

    """
    # Retrieve the value of GITHUB_WORKSPACE
    base_dir, action_base_dir = get_repo_and_action_path_env_variables()

    tex_file_abs_path = os.path.join(base_dir, tex_file_path)
    print(f"tex-file: {tex_file_abs_path}")
    config_file_abs_path = os.path.join(action_base_dir, CHKTEX_CONFIG_FILE_REL_PATH)
    print(f"config-file: {config_file_abs_path}")
    # chktex_path = os.path.join(action_base_dir, CHKTEX_EXEC_REL_PATH)
    # print(f'chktex: {chktex_path}')

    # Create report file path
    parts = tex_file_path.split("/")
    filename_without_extension = parts[-1].split(".")[0]
    parts[-1] = f"{filename_without_extension}_lint-report.html"
    html_report_path = "-".join(parts)

    # Perform linting and save console output to html-file
    if create_zipped_report:
        # report_folder = "" # set manually if required to run locally
        report_folder = str(os.getenv("LINT_REPORT_FOLDER"))
        log.info(f"report_folder: {report_folder}")

        # Create the directory if it doesn't exist
        os.makedirs(f"{base_dir}/{report_folder}", exist_ok=True)

        # Perform spell check and save console output to html-file
        command = f'script -q -c "chktex -g -l {config_file_abs_path} {tex_file_abs_path}" /dev/null | ansi2html > {report_folder}/{html_report_path}'
        subprocess.run(command, shell=True, check=True)

        # Console output is only captured, need to count warnings for PR-comment
        pattern = "(.+), (Warning|Error|Message) (\\d+), (\\d+), (.+)"
        log.info(f"count_total_warnings: {report_folder}/{html_report_path}")
        global nr_of_total_warnings_for_zip
        nr_of_total_warnings_for_zip += count_total_warnings(base_dir, report_folder, html_report_path, pattern)

    # Perform linting, process output and create md. file
    if create_md_summary:
        command = f'script -q -c "chktex -g -l {config_file_abs_path} {tex_file_abs_path}" /dev/null'
        if not summary_file:
            log.error("Summary file is none, writing report not feasible.")
        else:
            analize_report(base_dir, command, tex_file_path, summary_file)


def str_to_bool(value: str) -> bool:
    """Performs type check if given value (given as str) is a bool"""
    if value.lower() in {"false", "f", "0", "no", "n"}:
        return False
    if value.lower() in {"true", "t", "1", "yes", "y"}:
        return True
    if value.lower() in {"none"}:
        print("Oh no, bool-arguments is none!")
        return True
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def main() -> None:
    # Define the logger format
    LOG_LEVEL = log.DEBUG
    log.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)

    # Define input argument parser
    log.info("Start check.")
    parser = argparse.ArgumentParser()
    parser.add_argument("-cf", "--changedfiles", type=str, required=True, help="Paths to changed files to be linted.")
    parser.add_argument(
        "-c", "--config", required=True, help="Config for CI/CD pipeline, likely .lecture-build-ci.json"
    )
    parser.add_argument("-wd", "--workdir", required=True, help="Working directory, likely repo root.")
    parser.add_argument(
        "--lint_pr_comment_with_zipped_report",
        type=str_to_bool,
        nargs="?",
        const=True,
        default=False,
        help="Feature: zip report and post download link as PR-comment",
    )
    parser.add_argument(
        "--lint_summary",
        type=str_to_bool,
        nargs="?",
        const=True,
        default=False,
        help="Feature: Write lint report as summary in md-format.",
    )
    args = parser.parse_args()
    args.workdir = Path(args.workdir)

    config_file = Config(args)
    create_zipped_report: bool = args.lint_pr_comment_with_zipped_report
    log.info(f"lint_pr_comment_with_zipped_report is set: {create_zipped_report}")
    create_md_summary: bool = args.lint_summary
    log.info(f"create_md_summary is set: {create_md_summary}")
    log.info(f"Added/Modified tex-file: {args.changedfiles}")

    # Filter paths that contain the specific directory defined in config in their path
    filtered_paths: list[str] = [p for p in args.changedfiles.split(",") if config_file.active_semester in p]
    log.info(f"Changed tex-files from {config_file.active_semester}: {filtered_paths}")

    # Perform spell-check and provide result depending on lint_pr_comment_with_zipped_report and lint_summary
    summary_file: SummaryMdFile | None
    if create_md_summary:
        summary_file = SummaryMdFile("lint_summary.md", len(filtered_paths))
    else:
        summary_file = None
    for path in filtered_paths:
        if not any(path in s for s in already_checked_files):
            use_chktex(path, create_zipped_report, create_md_summary, summary_file)

    if summary_file is not None:
        summary_file.add_details_summary_end()

    # append the environment variable to GITHUB_ENV
    gh_env = str(os.getenv("GITHUB_ENV"))
    with open(gh_env, "a") as env_file:
        env_file.write(f"TOTAL_LINT_WARNINGS_ZIP={nr_of_total_warnings_for_zip}\n")
        env_file.write(f"TOTAL_LINT_WARNINGS_REPORT={nr_of_total_warnings_for_md_file}\n")


if __name__ == "__main__":
    main()
