import os
import re

from bs4 import BeautifulSoup


def get_repo_and_action_path_env_variables():
    """
        Extract plain text from an HTML file, removing color codes.

        Args:

        Returns:
            string: path of current workspace repo
            string: path of GitHub action
    """
    # Retrieve the value of GITHUB_WORKSPACE and GITHUB_ACTION_PATH
    github_workspace = os.getenv('GITHUB_WORKSPACE')
    github_action_workspace = os.getenv('GITHUB_ACTION_PATH')

    # Check if the environment variable is set
    if github_workspace:
        print(f'GITHUB_WORKSPACE is set to: {github_workspace}')
        base_dir = github_workspace
    else:
        print('GITHUB_WORKSPACE is not set.')  # runs locally
        base_dir = ''  # TODO: set abs. local path to this repo, if required to run locally
    if github_action_workspace:
        print(f'GITHUB_ACTION_PATH is set to: {github_action_workspace}')
        action_base_dir = github_action_workspace
    else:
        print('GITHUB_ACTION_PATH is not set.')  # runs locally
        action_base_dir = ''  # TODO: set abs. local path to this repo, if required to run locally

    return base_dir, action_base_dir


def remove_ansi_escape_sequences(text):
    """
        Remove ANSI escape sequences from a string text.
    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def extract_plain_text_from_html(file_path, for_ltex_purposes=False):
    """
        Extract plain text from an HTML file, removing color codes. (always called by LTeX processing methods)

        Args:
            file_path(String): path to html report file (captured console output).
            for_ltex_purposes (bool): indicates it this method was called in the context of LTeX output processing

        Returns:
            string: text of html-file without color coding/ANSI escape sequences
    """
    with open(file_path, 'r', encoding='latin1') as file:
        html_content = file.read()
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()

        # LTeX did not produce any output (and no error was thrown). Analyzed file is fine.
        if not text.strip() and for_ltex_purposes:
            # Find the <body> tag
            body_tag = soup.find('body')

            # Check if the body tag exists and contains non-whitespace content
            if body_tag and not body_tag.get_text(strip=True):
                # The body of the HTML file is empty. Adding placeholder text.
                body_tag.append("Everything is fine. LTeX did not find any improvements.")
                with open(file_path, 'w', encoding='utf-8') as write_file:
                    write_file.write(str(soup))
            else:
                print("The body of the HTML file contains content.")

    # Remove any remaining ANSI escape sequences
    return remove_ansi_escape_sequences(text)


def count_total_warnings(base_dir, report_folder, html_report_file_name, pattern, for_ltex_purposes=False):
    """
        Count number of warnings, messages and errors given a chktex or ltex console report (html file)

        Args:
            base_dir (string): Path of repo base directory.
            report_folder (string): Path of directory to where html report can be found.
            html_report_file_name (string): Name of html report file (captured console output).
            pattern (string): regex pattern to match "raw" ltex-report (console output)
                              as SpellingNotification/LintNotification
            for_ltex_purposes (bool): indicates it this method was called in the context of LTeX output processing

        Returns:
            int: Number of notifications in html-report according to given pattern (warnings/errors/messages)
    """
    output = extract_plain_text_from_html(f'{base_dir}/{report_folder}/{html_report_file_name}', for_ltex_purposes)
    lines = output.split("\n")
    i = 0
    nr_of_total_warnings = 0
    while i < len(lines):
        step = 2
        match = re.match(pattern, lines[i])
        if match:
            nr_of_total_warnings = nr_of_total_warnings + 1

            while (i + step) < len(lines) and not re.match(pattern, lines[i + step]):
                step = step + 1
        else:
            step = 1
        i = i + step

    return nr_of_total_warnings
