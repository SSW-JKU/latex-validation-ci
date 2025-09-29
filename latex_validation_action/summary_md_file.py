#!/usr/bin/env python
import os
import threading

from tex_checks_utils import get_repo_and_action_path_env_variables

file_lock = threading.Lock()


class SummaryMdFile:
    def __init__(self, file_name, total_files, make_content_expandable=True, is_complementary_to_code_comments=False):
        """
            Multiplies two numbers and returns the result.

            Args:
                file_name (str): file name for md-report-file (attention: must contain "lint" if a lint-report).
                total_files (int): total number of analysed files, that will be reported.
                make_content_expandable (bool): Option, integrate the possiblity to fold in report by clicking,
                    if this md-file is to be posted as PR-comment or GITHUB_STEP_SUMAMRY. For this purpose the html-code:
                        # Titel 1
                        <details>
                            <summary>Click here</summary>
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor ...
                        </details>
                    is added, as in GitHub PR-comments simple html-code can be integrated into Markdown code.
                is_complementary_to_code_comments (bool):
                    Is only used for spell-checking (ltex) with the option to create in-code-PR-review-comments.
                    Determines if titel at start of report file is:
                        "# Additional summary of other warnings: Spelling check with LTex"
                        or
                        "# Summary: Spelling check with LTex"

            Returns:
        """

        self.add_details_summary = make_content_expandable

        base_dir, _ = get_repo_and_action_path_env_variables()
        self.file_name = os.path.join(base_dir, file_name)

        with open(self.file_name, 'wb') as f:
            if 'lint' in self.file_name:
                f.write('# Summary: Lint check with chktex\n'.encode())
            else:
                if is_complementary_to_code_comments:
                    f.write('# Additional summary of other warnings: Spelling check with LTex\n'.encode())
                else:
                    f.write('# Summary: Spelling check with LTex\n'.encode())
            f.write(f'Total files analized: {total_files}\n'.encode())

            if self.add_details_summary:
                f.write('<details>\n<summary>Click to expand full report</summary>\n\n\n'.encode())

    def add_overview_line(self, tex_file_path, nr_errors, nr_warnings, nr_messages):
        """
            Adds header of a bundle of notifications for a specific tex file.

            Args:
                tex_file_path (str): rel. path to tex file.
                nr_errors (int): number of errors for tex_file_path.
                nr_warnings (int): number of errors for tex_file_path.
                nr_messages (int): number of errors for tex_file_path.

            Returns:
                void
        """
        with file_lock:
            with open(self.file_name, 'ab+') as f:
                f.write(f'## Path: {tex_file_path}\n'
                        f'{nr_errors} errors printed, {nr_warnings} warnings printed, {nr_messages} messages printed\n\n'.encode())

    def add_notification_entry(self, notification):
        """
            Writes information of notification by spell-checker or linter to md-file.

            Args:
                notification (SpellingNotification or LintNotification): notification to be written to md-report file.

            Returns:
                void
        """
        with file_lock:
            with open(self.file_name, 'ab+') as f:
                if not hasattr(notification, 'suggestions'):
                    f.write(f'### Path: {notification.file}\n'
                            f'* **Type:** {notification.type}\n'
                            f'* **Line:** {notification.line}\n'
                            f'* **Message:** {notification.message}\n'
                            f'* **Context:**\n'
                            f'```\n'
                            f'{notification.code_snippet}\n'
                            f'```\n\n'.encode())
                elif hasattr(notification, 'suggestions'):
                    f.write(f'### Path: {notification.file}\n'
                            f'* **Type:** {notification.type}\n'
                            f'* **Line:** {notification.line}\n'
                            f'* **Message:** {notification.message}\n'
                            f'* **Context:**\n'
                            f'```\n'
                            f'{notification.code_snippet}\n'
                            f'{notification.suggestions}\n'
                            f'```\n\n'.encode())
                else:
                    print('Error: Incorrect notification type.')

    def add_details_summary_end(self):
        with file_lock:
            with open(self.file_name, 'ab+') as f:
                f.write(f'</details>'.encode())
