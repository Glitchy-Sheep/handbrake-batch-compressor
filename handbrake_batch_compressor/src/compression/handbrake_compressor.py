"""
The module provides a class to compress videos using HandbrakeCLI.

It will be used to compress the videos and to log the progress.
"""

import asyncio
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from shlex import split

import aiofiles

from handbrake_batch_compressor.src.cli.handbrake_cli_output_capturer import (
    HandbrakeProgressInfo,
    parse_handbrake_cli_output,
)
from handbrake_batch_compressor.src.errors.cancel_compression_by_user import (
    CompressionCancelledByUserError,
)
from handbrake_batch_compressor.src.errors.handbrake_cli_exceptions import (
    CompressionFailedError,
)


class HandbrakeCompressor:
    """Handles video compression using HandbrakeCLI."""

    def __init__(self, handbrakecli_options: str = '') -> None:
        """Initialize the HandbrakeCompressor with the given handbrakecli options."""
        self.handbrakecli_options = handbrakecli_options

    async def compress(
        self,
        input_video: Path,
        output_video: Path,
        on_update: Callable[[HandbrakeProgressInfo], None] = lambda _: None,
    ) -> None:
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
        process = await asyncio.create_subprocess_exec(
            *compress_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            # Buffering stderr until we detect that error occurred
            # (stderr contains not only errors but also service info)
            error_buffer = StringIO()

            # Handle stdout line by line to update progress
            async def handle_stdout() -> None:
                if process.stdout is not None:
                    try:
                        while not process.stdout.at_eof():
                            line = await process.stdout.readuntil(b'\r')
                            decoded_line = line.decode('utf-8')
                            info = parse_handbrake_cli_output(decoded_line)
                            on_update(info)
                    except asyncio.IncompleteReadError as e:  # end of stream reached
                        line = e.partial.decode()
                        info = parse_handbrake_cli_output(line)
                        on_update(info)
                        return

            # Handle stderr line by line for saving error messages to buffer
            # after failed compression all the errors will be saved to a log file
            async def handle_stderr() -> None:
                if process.stderr is not None:
                    try:
                        while not process.stderr.at_eof():
                            line = await process.stderr.readuntil(b'\r')
                            decoded_line = line.decode('utf-8')
                            error_buffer.write(decoded_line)
                    except asyncio.IncompleteReadError as e:  # end of stream reached
                        error_buffer.write(e.partial.decode())
                        return

            await asyncio.gather(
                handle_stdout(),
                handle_stderr(),
            )

            await process.wait()

            # Check if the compression was successful
            # (compressed video should exist)
            if not output_video.exists():
                # Log error to file
                async with aiofiles.open(stderr_log_filename, mode='a') as f:
                    await f.write('\n')
                    await f.write('*' * 30 + input_video.name + '*' * 30 + '\n')
                    await f.write(error_buffer.getvalue())

                # Propagate failed compression if there is no result
                raise CompressionFailedError(
                    input_video,
                    stderr_log_filename,
                )

        # In case of ctrl_+ c just cancell the process
        except KeyboardInterrupt as e:
            process.terminate()
            await process.wait()
            if output_video.exists():  # Interrupted encoding can't be successful
                output_video.unlink()  # so delete the output

            raise CompressionCancelledByUserError from e
