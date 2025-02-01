"""
A module providing a class for batch video compression using HandbrakeCLI.

This class automates the process of compressing all the video files in a given directory
using HandbrakeCLI.

Example usage:
```python
    from src.batch_video_compressor import BatchVideoCompressor

    video_files = get_video_files(target_path)
    compressor = BatchVideoCompressor(video_files)
    compressor.compress_all_videos()
```
"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from shlex import split

from rich.progress import Progress

from src.handbrake_cli_output_capturer import (
    HandbrakeProgressInfo,
    parse_handbrake_cli_output,
)
from src.logger import log


class BatchVideoCompressor:
    """Main class for compressing videos."""

    def __init__(
        self,
        video_files: set[Path],
        *,
        delete_original_files: bool = False,
        progress_ext: str = "compressing",
        complete_ext: str = "compressed",
        handbrakecli_options: str = "",
    ) -> None:
        self.progress_ext = progress_ext
        self.complete_ext = complete_ext
        self.video_files = video_files
        self.delete_original_files = delete_original_files
        self.handbrake_cli_options = handbrakecli_options

    def compress_video(
        self,
        input_video: str,
        output_video: str,
        on_update: Callable[[HandbrakeProgressInfo], None] = lambda _: None,
    ) -> None:
        """
        Compresses a single video file using handbrakecli.

        It also creates a log file for each compression to be able to debug errors.
        on_update is a callback that will be called with HandbrakeProgressInfo on each update from handbrakecli.
        """
        compress_cmd = [
            "handbrakecli",
            "-i",
            input_video,
            "-o",
            output_video,
            *split(self.handbrake_cli_options, " "),
        ]

        stderr_log_filename = Path("last_compression.log")

        with stderr_log_filename.open(
            "w+",
            encoding="utf-8",
        ) as last_compression_log:
            handbrakecli = subprocess.Popen(  # noqa: S603 - compress_cmd is safe and checked before, but maybe we can remove this ignore with a more elegant solution
                compress_cmd,
                stdout=subprocess.PIPE,
                stderr=last_compression_log,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
            )

            for line in handbrakecli.stdout:
                info = parse_handbrake_cli_output(line)
                on_update(info)

            handbrakecli.wait()

        # For some reason handbrakecli doesn't set return code to non zero value on errors
        # it's literally zero even on invalid video encoder value
        # so the only way to detect errors is to check stderr for ERROR tag.
        # TODO(Issue: #2): This code is unreliable in some cases, we need to figure out a better way catch errors
        # with stderr_log_filename.open(encoding="utf-8") as errlog:
        #     for line in errlog:
        #         if "ERROR" in line:
        #             log.skip_lines(4)
        #             log.error(
        #                 f"HANDBRAKECLI got an error for file: '{input_video.name}'\n"
        #                 f"Please see the last_compression.log file for more details.\n"
        #                 "Or see the short help message below:\n"
        #                 "\n"
        #                 f"{line}"
        #                 "\n"
        #                 "Handbrake CLI command was: \n"
        #                 "\n"
        #                 f"{compress_cmd}",
        #             )

        #             sys.exit(1)

    def compress_videos(self) -> None:
        """Traverse all the video files and compress them, removing incomplete ones."""
        with Progress(
            console=log.console,
            transient=True,
            refresh_per_second=1,
        ) as progress:
            all_videos_task = progress.add_task(
                description=f"Compressing videos (0/{len(self.video_files)}) 0%",
                total=len(self.video_files),
            )

            for idx, video in enumerate(self.video_files):
                current_compression = progress.add_task(
                    total=100,
                    description=f"Compressing {video.name} (0%)",
                )

                input_video = video

                # filename.ext -> filename.compressing.ext
                output_video = (
                    video.parent / f"{video.stem}.{self.progress_ext}{video.suffix}"
                ).absolute()

                # Compress
                self.compress_video(
                    input_video,
                    output_video,
                    on_update=lambda info, task=current_compression: progress.update(
                        task_id=task,
                        completed=info.progress,
                        description=f"[italic]FPS: {info.fps_current or ''}[/italic] - [underline] Average FPS: {info.fps_average or ''}",
                    ),
                )

                # filename.compressing.ext -> filename.compressed.ext
                completed_stem = output_video.stem.replace(
                    self.progress_ext,
                    self.complete_ext,
                )
                output_video.rename(video.parent / f"{completed_stem}{video.suffix}")

                if self.delete_original_files and input_video.exists():
                    input_video.unlink()

                progress.remove_task(current_compression)

                progress.update(
                    all_videos_task,
                    advance=1,
                    description=f"Compressing videos ({idx + 1}/{len(self.video_files)}) {int((idx + 1) / len(self.video_files) * 100)}%",
                    refresh=True,
                )
