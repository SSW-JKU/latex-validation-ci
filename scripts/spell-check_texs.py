#!/usr/bin/env python
import json
import re
import argparse
import logging as log
import subprocess
import os
import requests
from typing import List

from github import Github
from pathlib import Path
from filelock import FileLock

from config import Config
from summary_md_file import SummaryMdFile
from tex_checks_utils import count_total_warnings, get_repo_and_action_path_env_variables

already_checked_files = set()
nr_of_total_warnings = 0
choices = {
    'zip_console_report_opt': 'ZIPP_CONSOLE_REPORT',
    'comment_in_code_and_make_report_opt': 'WRITE_PR_COMMENTS_AND_MD_REPORT_AS_PR_COMMENT',
    'make_report_for_pr_comment_opt': 'WRITE_MD_REPORT_AS_PR_COMMENT',
    'make_report_for_github_summary_opt': 'WRITE_MD_REPORT_AS_GITHUB_SUMMARY'
}

CONFIG_FILE_REL_PATH = 'ltex_config.txt'
LOCK_FILE = '/ltex_cli_plus.lock'
LOCK = FileLock(LOCK_FILE)


class SpellingNotification:
    def __init__(self, file: str, type: str, line: int, column: int, message: str, code_snippet: str, suggestions: str):
        self.file = file
        self.line = line
        self.column = column
        self.type = type
        self.message = message
        self.code_snippet = code_snippet
        self.suggestions = suggestions
        self.message_and_suggestions_mixed = f'{message}{suggestions}'

    def __repr__(self):
        return f"SpellingNotification(file={self.file}, type={self.type}, line={self.line}, column={self.column}, " \
               f" message={self.message}, code_snippet={self.code_snippet}, suggestions={self.suggestions})"


def post_pr_comments(notifications: List[SpellingNotification]):
    """
        Posts spell-check notifications (by ltex) as PR-review comments using PyGit

        Args:
            notifications: List[SpellingNotification]

        Returns:
            void
    """

    # Authenticate to GitHub
    token = os.getenv('GITHUB_TOKEN')
    g = Github(token)

    # Retrieve the repository and pull request
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    log.info(f'repo: {repo}')
    pr_number = os.getenv('GITHUB_REF').split('/')
    log.info(f'pr_number: {pr_number}')
    pr = repo.get_pull(int(pr_number[-2]))

    # Fetch the file's diff
    file_diff = next((f for f in pr.get_files() if f.filename == notifications[0].file), None)
    log.info(f'diff pr.get_files: {file_diff.raw_data}')

    response = requests.get(pr.diff_url)
    log.info(f'response: {response.status_code}, {response.text}')
    if response.status_code == 200:
        diff_content = response.text
        print(f'diff_url content: {diff_content}')

    log.info(f'Existing notifications to be commented is: {notifications[0].file}')

    # Get the commit ID (SHA) of the latest commit in the pull request
    commit = repo.get_commit(sha=pr.head.sha)

    for notification in notifications:
        body = f'{notification.message_and_suggestions_mixed}'
        pr.create_review_comment(
            body=body,
            commit=commit,
            path=notification.file,
            line=notification.line
        )

        # FAILED ATTEMPT to check for existing comments at the specified line, in order to overwrite them
        # review_comments = pr.get_review_comments()
        # if existing_comments:
        # Update the existing comment
        #    existing_comments[0].edit(body)
        # else:
        # Create a new comment
        #    pr.create_review_comment(
        #        body=body,
        #        commit=commit,
        #        path=notification.file,
        #        line=notification.line
        #    )

    g.close()


def line_is_in_diff(line, changedlines):
    """
        Checks if a line (nr) is in the diff.

        Args:
            line (int): line nr.
            changedlines (List(int)): changedlines of current file in diff.

        Returns:
            boolean: line is among changedlines.
    """
    line_in_diff = False
    for changedline in changedlines:
        if changedline - 2 <= line <= changedline + 2:
            line_in_diff = True
    return line_in_diff


def analize_report(option, base_dir, command, changedlines):
    """
        Performs spell-check (with ltex) on specified tex file,
        IF option == choices['comment_in_code_and_make_report_opt']:
            posts resulting ltex-warnings/messages/errors (notifications) as PR-review-comments,
            if respective line, where ltex-notification appears, is in diff and
        collects the remaining notifications for later convertion to report (md-file).

        Args:
            option (str): one of the options of choices (see global variable "choices").
            base_dir (str): Path of repo base directory.
            command (str): ltex command to perform spell-check on a specific ltex file, considering a ltex-config file
            changedlines (List(int)): List of line nr. of ltex file, to be analysed, in diff.

        Returns:
            List(SpellingNotifications): Collection of remaining notifications
    """

    # Run ltex for specified ltex file
    try:
        with LOCK:
            log.info(f'command: {command}')
            output = subprocess.check_output(command, shell=True, encoding='utf-8', errors='replace')
            log.info(f'Attention, unexpected output of ltex is: {output}')
        return []

    # As soon as ltex finds 1 warning or error, it returns return code 2
    except subprocess.CalledProcessError as e:
        output = e.output
        log.info(f"Got error: {e.stderr}, and output.")
        lines = output.split("\n")

        # Run over lines of raw ltex-report and parse warnings/errors/messages into objects SpellingNotification
        files = set()
        notifications = {'notifications_to_comment': [], 'notifications_to_report': []}
        i = 0
        while i < len(lines):
            first_line = lines[i]
            second_line = lines[i + 1] if i + 1 < len(lines) else ""
            step = 2

            # Matches lines like: "/home/runner/work/sw1-latex-exercise-ci/sw1-latex-exercise-ci/24SS/UE01/Unterricht/Lernziele.tex:57:136: info: 'yes': Möglicher Tippfehler gefunden. [AUSTRIAN_GERMAN_SPELLER_RULE]"
            pattern = (
                r"^(?P<file>.+?):(?P<line>\d+):(?P<column>\d+):\s*(?P<type>\w+):\s*(?P<message>.+).*$"
            )
            match = re.match(pattern, first_line)
            global nr_of_total_warnings
            if match:
                file = match.group('file')
                file = file.removeprefix(base_dir).removeprefix("/")
                files.add(file)

                # Avoid checking especially nested tex files (import), twice
                if file not in already_checked_files:
                    nr_of_total_warnings = nr_of_total_warnings + 1
                    type = match.group('type')
                    line = int(match.group('line'))
                    column = int(match.group('column'))
                    message = match.group('message').strip()
                    code_snippet = second_line.strip()
                    suggestions = ""

                    # Suggestions may span across multiple lines
                    while (i + step) < len(lines) and not re.match(pattern, lines[i + step]):
                        suggestions = f'{suggestions}\n{lines[i + step].strip()}'
                        step = step + 1

                    if option == choices['comment_in_code_and_make_report_opt'] and line_is_in_diff(line, changedlines):
                        # Merge multiple notifications for one line in tex file into one SpellingNotification
                        # to create one PR-review-comment
                        notif = next(
                            (n for n in notifications['notifications_to_comment'] if n.file == file and n.line == line),
                            None)
                        if notif:
                            notif.message = f'{notif.message}\n{message}'
                            notif.suggestions = f'{notif.suggestions}\n{suggestions}'
                            notif.message_and_suggestions_mixed \
                                = f'{notif.message_and_suggestions_mixed}\n\n{message}{suggestions}'
                        else:
                            notifications['notifications_to_comment'].append(
                                SpellingNotification(file, type, line, column, message, code_snippet, suggestions))
                    else:
                        notifications['notifications_to_report'].append(
                            SpellingNotification(file, type, line, column, message, code_snippet, suggestions))
            else:
                step = 1
            i = i + step

        # Notification for lines that are in diff, can be commented directly in the code (PR-review-comment)
        if len(notifications['notifications_to_comment']) > 0:
            post_pr_comments(notifications['notifications_to_comment'])

        # Update checked files
        already_checked_files.update(files)

        # Notification for lines not in diff, must be reported in an extra report (md-file)
        return notifications['notifications_to_report']


def clean_up_data(data, changed_files_paths):
    """
        Cleans up "raw" changed files information from diff (action) to only filter out
        AddedLines in tex files of interest (in our case changed files).

        Args:
            data (dict): "raw" changed files information from diff.
            changed_files_paths (List(String)): paths of files of interest (changed files).

        Returns:
            dict: AddedLine numbers of tex files of interest.
    """
    filtered_data = [entry for entry in data['files'] if entry["path"] in changed_files_paths]
    cleaned_up_data = []
    for entry in filtered_data:
        changed_lines = []
        for chunk in entry['chunks']:
            for change in chunk['changes']:
                if change['type'] == "AddedLine":  # ignore changes about DeletedLine, UnchangedLine
                    changed_lines.append(change['lineAfter'])
        cleaned_up_data.append({'path': entry['path'], 'changed_lines': changed_lines})
    return cleaned_up_data


def use_ltex(tex_file_path, option, changedlines):
    """
        Performs spell-check on the tex file specified,
        the resulting ltex-warnings/messages/errors (notifications) will be provided, depending on option:
            as captured-console-output in html or
            as md-file and/or
            as PR-review-comments (if line where notification is situated is in diff).

        Args:
            tex_file_path (str): Path to tex file to be spell-checked.
            option (str): one of the options of choices (see global variable 'choices').
            changedlines (List(int)): line nr. of file to be spell-checked, in diff.

        Returns:
            List(SpellingNotification): if option != choices['zip_console_report_opt'],
                                        returns list of notifications to be later written to the md-report-file.
    """

    base_dir, action_base_dir = get_repo_and_action_path_env_variables()

    # Create paths to tex file, ltex executable and ltex config file
    tex_file_abs_path = os.path.join(base_dir, tex_file_path)
    log.info(f'tex-file: {tex_file_abs_path}')
    config_file_abs_path = os.path.join(action_base_dir, CONFIG_FILE_REL_PATH)
    log.info(f'config-file: {config_file_abs_path}')
    ltex_dir = os.getenv('LTEX_PLUS_DIR')
    if not ltex_dir:
        ltex_dir = 'ltex-ls-plus-18.5.1/bin/ltex-cli-plus'  # running locally
    ltex_path = os.path.join(base_dir, ltex_dir)
    log.info(f'ltex-plus: {ltex_path}')

    # Create report file path
    parts = tex_file_path.split('/')
    filename_without_extension = parts[-1].split('.')[0]
    parts[-1] = f'{filename_without_extension}_report.html'
    tex_file_path = '-'.join(parts)

    if option == choices['zip_console_report_opt']:
        # report_folder = ".github/scripts/test_exercise_files/ltex_reports" # for local run
        report_folder = os.getenv('SPELLING_REPORT_FOLDER')
        log.info(f'report_folder: {report_folder}')

        # Create the directory if it doesn't exist
        os.makedirs(f'{base_dir}/{report_folder}', exist_ok=True)

        # Perform spell check and save console output to html-file
        with LOCK:
            command = f'script -q -c "{ltex_path} --client-configuration={config_file_abs_path} {tex_file_abs_path}" /dev/null | ansi2html > {report_folder}/{tex_file_path}'
            subprocess.run(command, shell=True, check=True)

        # Console output is only captured, need to count warnings for PR-comment
        global nr_of_total_warnings
        # Matches lines like: /home/runner/work/sw1-latex-exercise-ci/sw1-latex-exercise-ci/24SS/UE01/Unterricht/Lernziele.tex:57:136: info: 'yes': Möglicher Tippfehler gefunden. [AUSTRIAN_GERMAN_SPELLER_RULE]
        pattern = r"^(?P<file>.+?):(?P<line>\d+):(?P<column>\d+):\s*(?P<type>\w+):\s*(?P<message>.+).*$"
        nr_of_total_warnings += count_total_warnings(base_dir, report_folder, tex_file_path, pattern)
    else:
        command = f'{ltex_path} --client-configuration={config_file_abs_path} {tex_file_abs_path}'
        return analize_report(option, base_dir, command, changedlines)


def delete_old_comments_in_changed_files(filtered_paths):
    """
        Deletes all PR-review-comments in the files of interest,
        to avoid multiple PR-review-comments per line due to later comment-addition by the spell-checking process

        Args:
            filtered_paths (List(str)): List of paths to files of interest (to be spell-checked later).

        Returns:
            void.
    """

    # Delete all old comments
    token = os.getenv('GITHUB_TOKEN')
    g = Github(token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pr_number = os.getenv('GITHUB_REF').split('/')
    pr = repo.get_pull(int(pr_number[-2]))
    review_comments = pr.get_review_comments()
    for comment in review_comments:
        if comment.path in filtered_paths:
            comment.delete()
            print(f"Deleted comment: {comment.path}, {comment.position}, {comment.id}")
    g.close()


def comment_in_code_and_make_report_opt(option, filtered_paths, changedlines):
    """
        Performs spell-check (with ltex) on specified tex files,
        posts resulting ltex-warnings/messages/errors (notifications) as PR-review-comments,
        if respective line, where ltex-notification appears, is in diff and
        collects the remaining notifications to then write them to a report (md-file).

        Args:
            option (str): one of the options of choices (see global variable "choices").
            filtered_paths (List(str)): List of paths to tex files to be spell-checked.
            changedlines (str): Path to changed files information of diff
                                (created by another action GrantBirki/git-diff-action@v2.8.0)

        Returns:
            void.
    """
    summary_file = SummaryMdFile('spell_check_report.md',
                                 len(filtered_paths),
                                 is_complementary_to_code_comments=True)
    log.info(f'File {summary_file.file_name} successfully created.')

    # Delete old comments in order to avoid multiple comments for same line
    delete_old_comments_in_changed_files(filtered_paths)

    # Make report to PR comments
    with open(changedlines, 'r') as file:
        diff = json.load(file)
        log.info(f'Found data: {diff["type"]}')
    changed_files = clean_up_data(diff, filtered_paths)

    log.info(f'Changed lines are: {changed_files}')
    for changed_file in changed_files:
        if not any(changed_file in s for s in already_checked_files):
            notifications_not_in_diff = use_ltex(changed_file['path'], option, changed_file['changed_lines'])
            # log.info(f'It is time to report by md: {notifications_not_in_diff}')

            # Write report for warnings outside diff to summary md file
            if notifications_not_in_diff:
                summary_file.add_overview_line(changed_file['path'],
                                               0,
                                               len(notifications_not_in_diff),
                                               0)

                for notification in notifications_not_in_diff:
                    summary_file.add_notification_entry(notification)
    summary_file.add_details_summary_end()
    log.info('Report finnished.')


def make_md_report_without_comments(option, filtered_paths):
    """
        Performs spell-check (with ltex) on specified tex files,
        collects the ltex-notifications (warnings/messages/errors) to then write them to a report (md-file)
        for later use as GITHUB_STEP_SUMMARY or PR-comment posting.
        (PR-comment (comment in PR) != PR-review-comment (comment in PR in line of a file))

        Args:
            option (str): one of the options of choices (see global variable "choices").
            filtered_paths (List(str)): List of paths to tex files to be spell-checked.

        Returns:
            void.
    """
    summary_file = SummaryMdFile('spell_check_report.md',
                                 len(filtered_paths))

    for path in filtered_paths:
        if not any(path in s for s in already_checked_files):
            notifications = use_ltex(path, option, None)

            if notifications:
                # Write resulting ltex-notifications to md-file
                # log.info(f'It is time to report by md: {notifications}')
                summary_file.add_overview_line(path,
                                               0,
                                               len(notifications),
                                               0)

                for notification in notifications:
                    summary_file.add_notification_entry(notification)
            else:
                log.warning(f'Notifications for {path}: {notifications}')

    # Add details html-tag
    summary_file.add_details_summary_end()
    log.info('Report finnished.')


def main():
    # Define the logger format
    LOG_LEVEL = log.DEBUG
    log.basicConfig(format='%(levelname)s: %(message)s', level=LOG_LEVEL)

    # Define input argument parser
    log.info("Start check.")
    parser = argparse.ArgumentParser()
    parser.add_argument('-cf', '--changedfiles', required=True, help="Paths to changed files to be spell-checked.")
    parser.add_argument('-o', '--option', choices=[choices['zip_console_report_opt'],
                                                   choices['comment_in_code_and_make_report_opt'],
                                                   choices['make_report_for_pr_comment_opt'],
                                                   choices['make_report_for_github_summary_opt']],
                        required=True,
                        help='Choose between 4 options: ZIPP_CONSOLE_REPORT to capture console output to html-report, '
                             'WRITE_PR_COMMENTS_AND_MD_REPORT_AS_PR_COMMENT: writes pr-review-comments directly in code '
                             '(if in diff) and reports the rest as .md-file'
                             'WRITE_MD_REPORT_AS_PR_COMMENT: writes all warnings as md-file and posts it as pr-comment'
                             'WRITE_MD_REPORT_AS_GITHUB_SUMMARY: writes all warnings as md-file and posts it '
                             'as GITHUB_SUMMARY')
    parser.add_argument('-cl', '--changedlines',
                        help="Path to the diff-JSON file from action GrantBirki/git-diff-action@v2.8.0. "
                             "(required for option WRITE_PR_COMMENTS_AND_MD_REPORT_AS_PR_COMMENT)")
    parser.add_argument('-c', '--config', required=True,
                        help="Config for CI/CD pipeline, likely .lecture-build-ci.json")
    parser.add_argument('-wd', '--workdir', required=True, help="Working directory, likely repo root.")
    args = parser.parse_args()
    args.workdir = Path(args.workdir)

    log.info(f'Chosen option: {args.option}')
    if args.option == choices['comment_in_code_and_make_report_opt'] and (
      not args.changedlines or not os.getenv('GITHUB_TOKEN')):
        raise argparse.ArgumentTypeError(
            "When setting --option to WRITE_PR_COMMENTS_AND_MD_REPORT, changedlines and the env-variable GITHUB_TOKEN "
            "must be set.")

    config_file = Config(args)
    log.info(f'Added/Modified tex-file: {args.changedfiles}')
    log.info(f'Added/Modified tex-file lines: {args.changedlines}')

    # Filter paths that contain the specific directory defined in config in their path
    filtered_paths = [p for p in eval(args.changedfiles) if config_file.active_semester in p]
    log.info(f'Changed tex-files from {config_file.active_semester}: {filtered_paths}')

    # Perform spell-check and provide result depending on args.option
    if args.option == choices['zip_console_report_opt']:
        for path in filtered_paths:
            if not any(path in s for s in already_checked_files):
                use_ltex(path, args.option, None)

    elif args.option == choices['comment_in_code_and_make_report_opt']:
        comment_in_code_and_make_report_opt(args.option, filtered_paths, args.changedlines)

    # workflow: choices['make_report_for_pr_comment_opt'] or choices['make_report_for_github_summary_opt']
    else:
        make_md_report_without_comments(args.option, filtered_paths)

    # Append the environment variable to GITHUB_ENV
    with open(os.getenv('GITHUB_ENV'), 'a') as env_file:
        env_file.write(f"TOTAL_SPELLINGCHECK_WARNINGS={nr_of_total_warnings}\n")


if __name__ == "__main__":
    main()
