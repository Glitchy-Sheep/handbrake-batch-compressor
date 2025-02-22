"""The module provides a class to manage the batch compression of videos."""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.rule import Rule

from handbrake_batch_compressor.src.cli.logger import log
from handbrake_batch_compressor.src.cli.statistics_logger import StatisticsLogger
from handbrake_batch_compressor.src.compression.compression_statistics import (
    CompressionStatistics,
)
from handbrake_batch_compressor.src.errors.cancel_compression_by_user import (
    CompressionCancelledByUserError,
)
from handbrake_batch_compressor.src.errors.handbrake_cli_exceptions import (
    CompressionFailedError,
)
from handbrake_batch_compressor.src.utils.ffmpeg_helpers import get_video_properties

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from handbrake_batch_compressor.src.cli.handbrake_cli_output_capturer import (
        HandbrakeProgressInfo,
    )
    from handbrake_batch_compressor.src.compression.handbrake_compressor import (
        HandbrakeCompressor,
    )
    from handbrake_batch_compressor.src.utils.smart_filters import SmartFilter


class IneffectiveCompressionBehavior(str, Enum):
    """
    Option to choose how to handle ineffective compressions (when compressed file is larger).

    mark_original - Mark the original file as compressed.
    delete_compressed - Delete the larger file and mark the other one as compressed.
    keep_both - Keep both files in any case.
    """

    mark_original = 'mark_original'
    delete_compressed = 'delete_compressed'
    keep_both = 'keep_both'


class EffectiveCompressionBehavior(str, Enum):
    """
    Option to choose how to handle effective compressions (when compressed file is smaller).

    delete_original - Delete the original file.
    keep_both - Keep both files in any case.
    """

    delete_original = 'delete_original'
    keep_both = 'keep_both'


class CompressionManagerOptions(BaseModel):
    """Main options for the compression manager."""

    show_stats: bool = False
    progress_ext: str = 'compressing'
    complete_ext: str = 'compressed'
    skip_failed_files: bool = False
    ineffective_compression_behavior: IneffectiveCompressionBehavior
    effective_compression_behavior: EffectiveCompressionBehavior


class CompressionManager:
    """Manages the batch compression of multiple videos."""

    def __init__(
        self,
        video_files: set[Path],
        *,
        compressor: HandbrakeCompressor,
        smart_filter: SmartFilter,
        options: CompressionManagerOptions,
    ) -> None:
        self.video_files = video_files
        self.compressor = compressor
        self.smart_filter = smart_filter
        self.options = options

        self.statistics = CompressionStatistics()
        self.statistics_logger = StatisticsLogger(self.statistics, log)

    def compress_all_videos(self) -> None:
        """Compress all the videos in the given directory."""
        general_progress = Progress(
            'Compressing videos: {task.description} ([bold blue]{task.completed}/{task.total}[/bold blue])',
            BarColumn(bar_width=None),
            'Time Elapsed: ',
            TimeElapsedColumn(),
            console=log.console,
            transient=True,
        )

        task_progress = Progress(
            '{task.description}',
            BarColumn(bar_width=None),
            '[progress.percentage]{task.percentage:>3.0f}%',
            'Current ETA: ',
            TimeRemainingColumn(),
            transient=True,
        )

        video_name_max_length = 30

        with Live(
            Align.left(
                Panel(
                    Group(
                        general_progress,
                        Rule(),
                        task_progress,
                    ),
                ),
                vertical='middle',
                width=120,
            ),
            refresh_per_second=1,
            console=log.console,
            transient=True,
        ):
            all_videos_task = general_progress.add_task(
                description='Compressing videos',
                total=len(self.video_files),
            )

            for video in self.video_files:
                video_properties = get_video_properties(video)

                if video_properties is None:
                    log.error(
                        f"""Error getting video properties for {video.name}. The file is probably corrupted. Skipping...""",
                    )
                    self.statistics.skip_file(video)
                    continue

                if not self.smart_filter.should_compress(video_properties):
                    log.info(
                        f"""Skipping {video.name} because it doesn't meet the smart filter criteria...""",
                    )
                    self.statistics.skip_file(video)
                    continue

                shortened_video_name = video.name[:video_name_max_length]
                shortened_video_name += (
                    '...' if len(video.name) > video_name_max_length else ''
                )

                current_compression = task_progress.add_task(
                    total=100,
                    description=f'Compressing {shortened_video_name}',
                )

                general_progress.update(
                    all_videos_task,
                    description=shortened_video_name,
                )

                self.compress_video(
                    video,
                    on_progress_update=lambda info,
                    task=current_compression: task_progress.update(
                        task,
                        description=f'[italic]FPS: {info.fps_current or ""}[/italic] - [underline] Average FPS: {info.fps_average or ""}',
                        completed=info.progress,
                    ),
                )

                general_progress.update(
                    all_videos_task,
                    advance=1,
                )
                task_progress.remove_task(current_compression)

        if self.options.show_stats:
            self.statistics_logger.log_stats()

    def handle_effective_compression(self, video: Path) -> None:
        if (
            self.options.effective_compression_behavior
            == EffectiveCompressionBehavior.delete_original
        ):
            log.info(f'Deleting original video {video.name}')
            video.unlink()
        elif (
            self.options.effective_compression_behavior
            == EffectiveCompressionBehavior.keep_both
        ):
            pass

    def handle_ineffective_compression(self, output_video: Path, video: Path) -> None:
        if (
            self.options.ineffective_compression_behavior
            == IneffectiveCompressionBehavior.mark_original
        ):
            self.statistics.skip_file(video)
            output_video.unlink()
            video.rename(output_video)
            log.info(
                f'Deleting ineffective compression: {output_video.name} and marking the {video.name} as compressed.',
            )
        elif (
            self.options.ineffective_compression_behavior
            == IneffectiveCompressionBehavior.delete_compressed
        ):
            output_video.unlink()
            self.statistics.skip_file(video)
            log.info(
                f'Skipping ineffective compression: {output_video.name}.',
            )
        elif (
            self.options.ineffective_compression_behavior
            == IneffectiveCompressionBehavior.keep_both
        ):
            pass

    def compress_video(
        self,
        video: Path,
        on_progress_update: Callable[[HandbrakeProgressInfo], None] | None = None,
    ) -> None:
        """Compresses a single video file using handbrakecli."""
        # filename.ext -> filename.compressing.ext
        output_video = (
            video.parent / f'{video.stem}.{self.options.progress_ext}{video.suffix}'
        ).absolute()

        try:
            asyncio.run(
                self.compressor.compress(
                    video,
                    output_video,
                    on_update=on_progress_update or (lambda _: None),
                ),
            )
        except (CompressionFailedError, CompressionCancelledByUserError) as e:
            # If the compression failed during encoding - remove the output video
            # because it's useless
            if output_video.exists():
                output_video.unlink()

            if isinstance(e, CompressionFailedError) and self.options.skip_failed_files:
                log.error(str(e))
                log.warning(
                    'Skipping the video according to the [bold]--skip-failed-files[/bold] flag',
                )
                self.statistics.skip_file(video)
                return

            raise

        completed_stem = output_video.stem.replace(
            self.options.progress_ext,
            self.options.complete_ext,
        )
        output_video = output_video.rename(
            video.parent / f'{completed_stem}{video.suffix}',
        )

        if self.options.show_stats:
            current_video_stats = self.statistics.add_compression_info(
                video,
                output_video,
            )
            self.statistics_logger.log_stats(current_video_stats)

        # Now compressed video is marked as completed and we still have the original one

        compression_is_ineffective = output_video.stat().st_size > video.stat().st_size

        if compression_is_ineffective:
            self.handle_ineffective_compression(output_video, video)
        else:
            self.handle_effective_compression(video)
