"""Main module for the video compressor and the entry point for the CLI."""

import sys
from pathlib import Path
from typing import Annotated

import typer
import typer.rich_utils

from src.batch_video_compressor import BatchVideoCompressor
from src.cli_guards import (
    check_extensions_arguments,
    check_handbrakecli_options,
    check_target_path,
)
from src.logger import log
from src.third_party_installers import setup_software
from src.videofiles_traverser import get_video_files_paths

app = typer.Typer(
    no_args_is_help=True,
    cls=True,
    add_completion=False,
    rich_help_panel=True,
    rich_markup_mode="rich",
)


def remove_incomplete_files(incomplete_files: set[str]) -> int:
    """Remove incomplete files and update the task queue."""
    for file in incomplete_files:
        file_path = Path(file)
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as e:
                log.error(f"Failed to remove file {file}: {e}")
        else:
            log.warning(f"File {file} does not exist, skipping.")


@app.command()
def main(
    target_path: Annotated[
        Path,
        typer.Option(
            "--target-path",
            "-t",
            help="The path where your videos are.",
        ),
    ],
    handbrakecli_options: Annotated[
        str,
        typer.Option(
            "--handbrakecli-options",
            "-o",
            help="You can pass HandbrakeCLI options through this argument. (Don't forget to quote them in one string)",
        ),
    ],
    progress_ext: Annotated[
        str,
        typer.Option(
            "--progress-extension",
            "-p",
            help="Extension which will be added to the file while processing it.",
        ),
    ] = "compressing",
    complete_ext: Annotated[
        str,
        typer.Option(
            "--complete-extension",
            "-c",
            help="Extension which will be added to the file when it's complete.",
        ),
    ] = "compressed",
    *,
    delete_original_files: Annotated[
        bool,
        typer.Option(
            "--delete-original-files",
            "-d",
            help="Should the original files be deleted after compression.",
        ),
    ] = False,
) -> None:
    """
    Compress your video files in batch with HandbrakeCLI.

    1. Set `--target-path` to the directory containing your videos.
    2. The utility will compress all video files in it recursively.

    Use `--delete-original-files` to replace the original files with compressed ones.
    ⚠ [bold red]Be cautious![/bold red] This deletes the original videos right after compression.

    The utility uses file extensions to skip already compressed videos.
    Customize with `--progress-extension` and `--complete-extension` (ensure they are unique and do not contain dots).

    [bold green]Examples:[/bold green]
    1. Compress all videos in `./videos` and delete originals:
    - [bold] ./main.py -t ./videos -d [/bold]
    2. Compress files with custom encoder and quality:
    - [bold] ./main.py -t ./videos --handbrakecli-options "--encoder qsv_h264 --quality 20" [/bold]
    3. Compress using a preset:
    - [bold] ./main.py -t ./videos --handbrakecli-options "--preset 'Fast 720p30'" [/bold]
    """
    check_target_path(target_path)
    check_extensions_arguments(progress_ext, complete_ext)
    check_handbrakecli_options(handbrakecli_options)

    setup_software()

    # All video files, unprocessed, processed and incomplete
    log.wait("Collecting all your video files...")
    video_files = set(get_video_files_paths(target_path))

    if len(video_files) == 0:
        log.success("No video files found. - Nothing to do.")
        sys.exit(1)

    log.success(f"Found {len(video_files)} video files.")

    complete_files = set()
    incomplete_files = set()
    unprocessed_files = set()

    for file in video_files:
        extensions = {x.replace(".", "") for x in file.suffixes}
        if complete_ext in extensions:
            complete_files.add(file)
        elif progress_ext in extensions:
            incomplete_files.add(file)
        else:
            unprocessed_files.add(file)

    # Remove complete files from unprocessed
    for original_file in (
        # filename.complete_ext.ext -> filename.ext
        x.parent / f"{x.stem.replace(f'.{complete_ext}', '')}{x.suffix}"
        for x in complete_files
    ):
        unprocessed_files.discard(original_file)

    log.info(f"Found complete files: {len(complete_files)}")
    log.info(f"Found incomplete files: {len(incomplete_files)}")
    log.info(f"Found unprocessed files: {len(unprocessed_files)}")

    if len(incomplete_files) > 0:
        remove_incomplete_files(incomplete_files)
        log.success(f"Removed {len(incomplete_files)} incomplete files. 🧹✨")

    compressor = BatchVideoCompressor(
        delete_original_files=delete_original_files,
        video_files=unprocessed_files,
        progress_ext=progress_ext,
        complete_ext=complete_ext,
        handbrakecli_options=handbrakecli_options,
    )
    compressor.compress_videos()

    log.success("Everything is done! 🎉")


if __name__ == "__main__":
    app()
