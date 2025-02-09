"""The module provides functions to check if the arguments passed to the CLI are valid."""

import sys
from pathlib import Path
from textwrap import dedent

from handbrake_batch_compressor.src.cli.logger import log


def check_target_path(target_path: Path) -> None:
    """Check if the target path is a directory and exists otherwise exits."""
    if not target_path.is_dir():
        log.error("Your target path is not a directory or doesn't exist")
        sys.exit(1)


def check_extensions_arguments(progress_ext: str, complete_ext: str) -> None:
    """
    Check if the progress and complete extensions are valid otherwise exits.

    Valid extensions:
        - No dots
        - No empty
    """
    if progress_ext.count('.') > 0 or complete_ext.count('.') > 0:
        log.error('Progress and complete extensions cannot contain dots.')
        sys.exit(1)

    if progress_ext == complete_ext:
        log.error('Progress and complete extensions cannot be the same.')
        sys.exit(1)

    if len(progress_ext) == 0 or len(complete_ext) == 0:
        log.error('Progress and complete extensions cannot be empty.')
        sys.exit(1)


def check_handbrakecli_options(handbrakecli_options: str) -> None:
    """
    Check if the handbrakecli options are valid otherwise exits.

    Options are generally valid if they are not input/output options.
    """
    if (
        '-i' in handbrakecli_options
        or '-o' in handbrakecli_options
        or '--input' in handbrakecli_options
        or '--output' in handbrakecli_options
    ):
        log.error(
            dedent(
                """
            You should not use input/output handbrakecli options, it will fail the process.
            The utility will automatically add them for you.
            """,
            ),
        )
        sys.exit(1)
