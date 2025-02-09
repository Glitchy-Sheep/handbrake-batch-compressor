"""
The module provides a class to compress videos using HandbrakeCLI.

It will be used to compress the videos and to log the progress.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from shlex import split

from src.cli.handbrake_cli_output_capturer import (
    HandbrakeProgressInfo,
    parse_handbrake_cli_output,
)
from src.cli.logger import log


class HandbrakeCompressor:
    """Handles video compression using HandbrakeCLI."""

    def __init__(self, handbrakecli_options: str = '') -> None:
        """Initialize the HandbrakeCompressor with the given handbrakecli options."""
        self.handbrakecli_options = handbrakecli_options

    def compress(
        self,
        input_video: Path,
        output_video: Path,
        on_update: Callable[[HandbrakeProgressInfo], None] = lambda _: None,
    ) -> bool:
        """
        Compress a single video file.

        Returns True if the compression was successful, False otherwise.
        """
        compress_cmd = [
            'handbrakecli',
            '-i',
            str(input_video),
            '-o',
            str(output_video),
            *split(self.handbrakecli_options),
        ]

        stderr_log_filename = Path('last_compression.log')

        with stderr_log_filename.open('w+', encoding='utf-8') as log_file:
            process = subprocess.Popen(  # noqa: S603 - compress_cmd is safe and checked before, but maybe we can remove this ignore with a more elegant solution
                compress_cmd,
                stdout=subprocess.PIPE,
                stderr=log_file,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            if process.stdout:
                for line in process.stdout:
                    info = parse_handbrake_cli_output(line)
                    on_update(info)

            process.wait()

        if not output_video.exists():
            log.error(
                f'Compression failed for {input_video.name}. Check {stderr_log_filename} for details.',
            )
            return False

        return True
