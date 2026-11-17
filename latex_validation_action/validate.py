import logging
from pathlib import Path
from typing import Annotated, Final

import typer

from .lint_texs import lint_tex
from .spell_check_texs import Option

app = typer.Typer()

LOG_LEVEL: Final = logging.DEBUG
logging.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)


@app.command(help="Run linting on changed files")
def lint(
    changed_files: Annotated[
        list[str], typer.Option("--changed-files", "-cf", help="Paths to changed files to be linted")
    ],
    workdir: Annotated[Path, typer.Option("--workdir", "-wd", help="Working directory, likely repo root")],
    active_semester: Annotated[str, typer.Option(help="Active semester, e.g. WS23")],
    lint_pr_comment_with_zipped_report: Annotated[
        bool, typer.Option(help="Zip report and post download link as PR-comment")
    ] = False,
    lint_summary: Annotated[bool, typer.Option(help="Write lint report as summary in md-format")] = False,
) -> None:
    lint_tex(changed_files, workdir, active_semester, lint_pr_comment_with_zipped_report, lint_summary)


@app.command(name="spell-check", help="Run spell-checking on changed files")
def spell_check(
    changed_files: Annotated[
        list[str], typer.Option("--changed-files", "-cf", help="Paths to changed files to be linted")
    ],
    option: Annotated[
        Option,
        typer.Option(
            help=(
                "Choose between 4 options: ZIPP_CONSOLE_REPORT to capture console output to html-report, "
                "WRITE_PR_COMMENTS_AND_MD_REPORT_AS_PR_COMMENT: writes pr-review-comments directly in code "
                "(if in diff) and reports the rest as .md-file"
                "WRITE_MD_REPORT_AS_PR_COMMENT: writes all warnings as md-file and posts it as pr-comment"
                "WRITE_MD_REPORT_AS_GITHUB_SUMMARY: writes all warnings as md-file and posts it "
                "as GITHUB_SUMMARY"
            )
        ),
    ],
    workdir: Annotated[Path, typer.Option("--workdir", "-wd", help="Working directory, likely repo root")],
    active_semester: Annotated[str, typer.Option(help="Active semester, e.g. WS23")],
    changed_lines: Annotated[
        Path | None,
        typer.Option(
            help=(
                "Path to the diff-JSON file from action GrantBirki/git-diff-action@v2.8.0. "
                "(required for option WRITE_PR_COMMENTS_AND_MD_REPORT_AS_PR_COMMENT"
            )
        ),
    ] = None,
) -> None:
    pass


if __name__ == "__main__":
    app()
