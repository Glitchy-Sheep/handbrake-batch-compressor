import os
import subprocess
from shlex import split
from typing import Callable

from rich.progress import Progress

from src.file_utils import FileUtils
from src.handbrake_cli_output_capturer import (
    HandbrakeProgressInfo,
    parse_handbrake_cli_output,
)
from src.logger import log


class BatchVideoCompressor:
    def __init__(
        self,
        verbose: bool,
        delete_original_files: bool,
        video_files: set[str],
        progress_ext="compressing",
        complete_ext="compressed",
        handbrakecli_options="",
    ):
        self.progress_ext = progress_ext
        self.complete_ext = complete_ext
        self.video_files = video_files
        self.verbose = verbose
        self.delete_original_files = delete_original_files
        self.handbrake_cli_options = handbrakecli_options

    def compress_video(
        self,
        input_video: str,
        output_video: str,
        on_update: Callable[[HandbrakeProgressInfo], None] = None,
    ):
        compress_cmd = [
            "handbrakecli",
            "-i",
            input_video,
            "-o",
            output_video,
            *split(self.handbrake_cli_options, " "),
        ]

        log.wait(f"Compressing {input_video}...", should_log=not self.verbose)

        stderr_log_filename = "last_compression.log"

        with open(stderr_log_filename, "w+", encoding="utf-8") as last_compression_log:
            handbrakecli = subprocess.Popen(
                compress_cmd,
                shell=True,
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
        with open(stderr_log_filename, "r", encoding="utf-8") as errlog:
            for line in errlog.readlines():
                if "ERROR" in line:
                    log.skip_lines(4)
                    log.error(
                        f"HANDBRAKECLI got an error for file: '{os.path.basename(input_video)}'\n"
                        f"Please see the last_compression.log file for more details.\n"
                        "Or see the short help message below:\n"
                        "\n"
                        f"{line}"
                        "\n"
                        "Handbrake CLI command was: \n"
                        "\n"
                        f"{compress_cmd}"
                    )

                    exit(1)

        log.success(
            f"Compressed {os.path.basename(input_video)}!",
            should_log=not self.verbose,
        )

    def compress_videos(self):
        with Progress(
            console=log.console,
            transient=True,
            refresh_per_second=4 if self.verbose else 1,
        ) as progress:
            all_videos_task = progress.add_task(
                description=f"Compressing videos (0/{len(self.video_files)}) 0%",
                total=len(self.video_files),
            )

            for idx, video in enumerate(self.video_files):
                current_compression = progress.add_task(
                    total=100,
                    description=f"Compressing {os.path.basename(video)} (0%)",
                )

                input_video = video

                # filename.ext -> filename.compressing.ext
                output_video = FileUtils.add_subextension(video, self.progress_ext)

                # Compress
                self.compress_video(
                    input_video,
                    output_video,
                    on_update=lambda info: progress.update(
                        current_compression,
                        completed=info.progress,
                        description=f"[italic]FPS: {info.fps_current or ''}[/italic] - [underline] Average FPS: {info.fps_average or ''}",
                    ),
                )

                # filename.compressing.ext -> filename.compressed.ext
                final_name = output_video.replace(self.progress_ext, self.complete_ext)
                os.rename(output_video, final_name)

                if self.delete_original_files:
                    os.remove(input_video)

                progress.remove_task(current_compression)

                progress.update(
                    all_videos_task,
                    advance=1,
                    description=f"Compressing videos ({idx + 1}/{len(self.video_files)}) {int((idx + 1) / len(self.video_files) * 100)}%",
                    refresh=True,
                )
