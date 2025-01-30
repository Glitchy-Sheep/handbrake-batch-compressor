import os
import subprocess

from shlex import split
from textwrap import dedent
from rich.progress import Progress
from typing import Callable


from src.file_utils import FileUtils
from src.logger import log
from src.handbrake_cli_output_capturer import (
    HandbrakeProgressInfo,
    parse_handbrake_cli_output,
)


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

        try:
            log.wait(f"Compressing {input_video}...", should_log=not self.verbose)
            handbrakecli = subprocess.Popen(
                compress_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            for line in handbrakecli.stdout:
                info = parse_handbrake_cli_output(line)
                on_update(info)

            handbrakecli.wait()

            log.success(
                f"Compressed {os.path.basename(input_video)}!",
                should_log=not self.verbose,
            )
        except subprocess.CalledProcessError as e:
            log.error(
                dedent(
                    f"""
                    HANDBRAKECLI throw an error for {input_video}
                    {
                        "Try to run the same command with -v for more info" 
                        if not self.verbose 
                        else "You can read the error details above"
                    }
                    """,
                )
            )

            exit(1)

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
                    description=f"Compressing videos ({idx+1}/{len(self.video_files)}) {int((idx+1) / len(self.video_files) * 100)}%",
                    refresh=True,
                )
