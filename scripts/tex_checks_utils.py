import re

from bs4 import BeautifulSoup


def remove_ansi_escape_sequences(text):
    """
        Remove ANSI escape sequences from a string text.
    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def extract_plain_text_from_html(file_path):
    """
        Extract plain text from an HTML file, removing color codes.

        Args:
            file_path(String): path to html report file (captured console output).

        Returns:
            string: text of html-file without color coding/ANSI escape sequences
    """
    with open(file_path, 'r', encoding='latin1') as file:
        html_content = file.read()
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        # Remove any remaining ANSI escape sequences
        return remove_ansi_escape_sequences(text)


def count_total_warnings(base_dir, report_folder, html_report_file_name, pattern):
    """
        Count number of warnings, messages and errors given a chktex or ltex console report (html file)

        Args:
            base_dir (string): Path of repo base directory.
            report_folder (string): Path of directory to where html report can be found.
            html_report_file_name (string): Name of html report file (captured console output).
            pattern (string): regex pattern to match "raw" ltex-report (console output)
                              as SpellingNotification/LintNotification

        Returns:
            int: Number of notifications in html-report according to given pattern (warnings/errors/messages)
    """
    output = extract_plain_text_from_html(f'{base_dir}/{report_folder}/{html_report_file_name}')
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
