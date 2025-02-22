"""Main module for the video compressor and the entry point for the CLI."""

from __future__ import annotations

import sys
from pathlib import Path  # noqa: TC003 - is used by typer
from typing import Annotated

import typer
import typer.rich_utils

from handbrake_batch_compressor.src.cli.cli_guards import (
    check_extensions_arguments,
    check_handbrakecli_options,
    check_target_path,
)
from handbrake_batch_compressor.src.cli.guide import show_guide_and_exit
from handbrake_batch_compressor.src.cli.logger import log
from handbrake_batch_compressor.src.compression.compression_manager import (
    CompressionManager,
    CompressionManagerOptions,
    EffectiveCompressionBehavior,
    IneffectiveCompressionBehavior,
)
from handbrake_batch_compressor.src.compression.handbrake_compressor import (
    HandbrakeCompressor,
)
from handbrake_batch_compressor.src.errors.cancel_compression_by_user import (
    CompressionCancelledByUserError,
)
from handbrake_batch_compressor.src.errors.handbrake_cli_exceptions import (
    CompressionFailedError,
)
from handbrake_batch_compressor.src.utils.ffmpeg_helpers import VideoResolution
from handbrake_batch_compressor.src.utils.files import get_video_files_paths
from handbrake_batch_compressor.src.utils.smart_filters import SmartFilter
from handbrake_batch_compressor.src.utils.third_party_installers import setup_software

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='rich',
)


def show_version_and_exit() -> None:
    """Show version and exit."""
    __version__ = '3.0.0'
    log.raw_log(f'handbrake-batch-compressor {__version__}')
    sys.exit(0)


def remove_incomplete_files(incomplete_files: set[Path]) -> None:
    """Remove incomplete files and update the task queue."""
    for file in incomplete_files:
        if file.exists():
            try:
                file.unlink()
            except OSError as e:
                log.error(f'Failed to remove file {file}: {e}')
        else:
            log.error(f'File {file} does not exist, skipping.')


@app.command()
def main(  # noqa: PLR0913: too many arguments because of typer
    target_path: Annotated[
        Path | None,
        typer.Option(
            '--target-path',
            '-t',
            help='The path where your videos are.',
        ),
    ] = None,
    handbrakecli_options: Annotated[
        str,
        typer.Option(
            '--handbrakecli-options',
            '-o',
            help="You can pass HandbrakeCLI options through this argument. (Don't forget to quote them in one string, see [bold green]Example 3[/bold green])",
        ),
    ] = '',
    progress_ext: Annotated[
        str,
        typer.Option(
            '--progress-extension',
            '-p',
            help='Extension which will be added to the file while processing it.',
        ),
    ] = 'compressing',
    complete_ext: Annotated[
        str,
        typer.Option(
            '--complete-extension',
            '-c',
            help="Extension which will be added to the file when it's complete.",
        ),
    ] = 'compressed',
    *,
    show_stats: Annotated[
        bool,
        typer.Option(
            '--show-stats',
            '-s',
            help='Should stats be shown during the compression and after it.',
        ),
    ] = False,
    #
    # File operation options
    #
    ineffective_compression_behavior: Annotated[
        IneffectiveCompressionBehavior,
        typer.Option(
            '--ineffective-compression-behavior',
            '-i',
            help='How to [bold]handle ineffective compressions[/bold]. ([bold red]delete[/bold red], [bold yellow]skip[/bold yellow], [bold green]keep[/bold green])'
            "\n\n* [bold red]delete[/bold red] will delete the compressed video if it's larger [bold]and mark original as compressed[/bold]."
            "\n\n* [bold yellow]skip[/bold yellow] will delete only the compressed file if it's larger and keep original."
            '\n\n* [bold green]keep[/bold green] will keep both files in any case.',
        ),
    ] = IneffectiveCompressionBehavior.skip,
    effective_compression_behavior: Annotated[
        EffectiveCompressionBehavior,
        typer.Option(
            '--effective-compression-behavior',
            '-e',
            help='How to [bold]handle effective compressions[/bold]. ([bold red]delete_original[/bold red], [bold yellow]keep_both[/bold yellow])'
            '\n\n* [bold red]delete_original[/bold red] will delete the original file and keep the compressed file.'
            '\n\n* [bold green]keep[/bold green] will keep both files in any case.',
        ),
    ] = EffectiveCompressionBehavior.keep,
    skip_failed_files: Annotated[
        bool,
        typer.Option(
            '--skip-failed-files',
            help='Skip files that failed to compress, instead of stopping the processing.',
        ),
    ] = False,
    #
    # ---------- Smart Filter options ----------
    #
    filter_min_bitrate: Annotated[
        int | None,
        typer.Option(
            '--filter-min-bitrate',
            '-b',
            help='The minimum bitrate in kbytes. Videos below this threshold will be skipped.',
        ),
    ] = None,
    filter_min_frame_rate: Annotated[
        int | None,
        typer.Option(
            '--filter-min-frame-rate',
            '-f',
            help='The minimum frame rate. Videos below this threshold will be skipped.',
        ),
    ] = None,
    filter_min_resolution: Annotated[
        VideoResolution | None,
        typer.Option(
            '--filter-min-resolution',
            '-r',
            help='The minimum resolution. Videos below this threshold will be skipped.',
            parser=VideoResolution.parse_resolution,
            metavar='<WIDTH>x<HEIGHT>',
        ),
    ] = None,
    # ---------- HandbrakeCLI options guide ----------
    guide: Annotated[
        bool,
        typer.Option(
            '--guide',
            '-g',
            help='Show compression guide and exit. See it if you are not sure what to do.',
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            '--version',
            '-v',
            help='Show version and exit.',
        ),
    ] = False,
) -> None:
    """
    Compress your video files in batch with HandbrakeCLI.

    [bold green]Examples:[/bold green]
    1. Compress all videos in `./videos` and delete originals:
    - [bold] ./main.py -t ./videos -d [/bold]
    2. Compress files with custom encoder and quality:
    - [bold] ./main.py -t ./videos -o "--encoder qsv_h264 --quality 20" [/bold]
    3. Compress using a preset:
    - [bold] ./main.py -t ./videos -o "--preset 'Fast 720p30'" [/bold]
    4. Compress files and leave only those smaller than the original and show stats:
    - [bold] ./main.py -t ./videos -k -s [/bold]
    5. Compress files excluding files with resolution and bitrate lower than the specified ones:
    - [bold] ./main.py -t ./videos --filter-min-resolution 720x480 --filter-min-bitrate 100 [/bold]
    """
    if version:
        show_version_and_exit()
        return

    if guide:
        show_guide_and_exit()
        return

    if target_path is None:
        log.error('You must specify a target path. (See [bold]--help)[/bold]')
        sys.exit(1)

    check_target_path(target_path)
    check_extensions_arguments(progress_ext, complete_ext)
    check_handbrakecli_options(handbrakecli_options)

    setup_software()

    # All video files, unprocessed, processed and incomplete
    log.wait('Collecting all your video files...')
    video_files = set(get_video_files_paths(target_path))

    if len(video_files) == 0:
        log.success('No video files found. - Nothing to do.')
        sys.exit(0)

    log.success(f'Found {len(video_files)} video files.')

    complete_files: set[Path] = set()
    incomplete_files: set[Path] = set()
    unprocessed_files: set[Path] = set()

    for file in video_files:
        extensions = {x.replace('.', '') for x in file.suffixes}
        if complete_ext in extensions:
            complete_files.add(file)
        elif progress_ext in extensions:
            incomplete_files.add(file)
        else:
            unprocessed_files.add(file)

    # Remove complete files from unprocessed
    for original_file in (
        # filename.complete_ext.ext -> filename.ext
        x.parent / f'{x.stem.replace(f".{complete_ext}", "")}{x.suffix}'
        for x in complete_files
    ):
        unprocessed_files.discard(original_file)

    log.info(f'Found complete files: {len(complete_files)}')
    log.info(f'Found incomplete files: {len(incomplete_files)}')
    log.info(f'Found unprocessed files: {len(unprocessed_files)}')

    if len(incomplete_files) > 0:
        remove_incomplete_files(incomplete_files)
        log.success(f'Removed {len(incomplete_files)} incomplete files. 🧹✨')

    smart_filter = SmartFilter(
        minimal_resolution=filter_min_resolution,
        minimal_bitrate_kbytes=filter_min_bitrate,
        minimal_frame_rate=filter_min_frame_rate,
    )

    compression_manager = CompressionManager(
        video_files=unprocessed_files,
        compressor=HandbrakeCompressor(handbrakecli_options=handbrakecli_options),
        smart_filter=smart_filter,
        options=CompressionManagerOptions(
            show_stats=show_stats,
            progress_ext=progress_ext,
            complete_ext=complete_ext,
            skip_failed_files=skip_failed_files,
            ineffective_compression_behavior=ineffective_compression_behavior,
            effective_compression_behavior=effective_compression_behavior,
        ),
    )

    compression_manager.compress_all_videos()

    log.success('Everything is done! 🎉')


def bootstrap() -> None:
    """
    Entry point of the CLI binary.

    It's separated from module into a function for proper error handling
    after installation.
    """
    try:
        app()

    # Typer will throw 130 exit code on ctrl + c interruption
    except SystemExit as e:
        sigterm_code = 130
        if e.code == sigterm_code:
            actual_exception = CompressionCancelledByUserError()
            log.success(str(actual_exception))
    except CompressionFailedError as e:
        log.error(str(e))
    except CompressionCancelledByUserError as e:
        log.success(str(e))


if __name__ == '__main__':
    bootstrap()
