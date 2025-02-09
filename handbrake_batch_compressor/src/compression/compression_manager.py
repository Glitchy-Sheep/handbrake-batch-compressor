"""The module provides a class to manage the batch compression of videos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from handbrake_batch_compressor.src.cli.logger import log
from handbrake_batch_compressor.src.cli.statistics_logger import StatisticsLogger
from handbrake_batch_compressor.src.compression.compression_statistics import (
    CompressionStatistics,
)
from handbrake_batch_compressor.src.utils.ffmpeg_helpers import get_video_properties
from pydantic import BaseModel
from rich.progress import Progress

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


class CompressionManagerOptions(BaseModel):
    """Main options for the compression manager."""

    show_stats: bool = False
    delete_original_files: bool = False
    keep_only_smaller: bool = False
    progress_ext: str = 'compressing'
    complete_ext: str = 'compressed'


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
        with Progress(
            console=log.console,
            transient=True,
            refresh_per_second=1,
        ) as progress:
            all_videos_task = progress.add_task(
                description=f'Compressing videos (0/{len(self.video_files)}) 0%',
                total=len(self.video_files),
            )

            for idx, video in enumerate(self.video_files):
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

                current_compression = progress.add_task(
                    total=100,
                    description=f'Compressing {video.name} (0%)',
                )

                self.compress_video(
                    video,
                    on_progress_update=lambda info,
                    task=current_compression: progress.update(
                        task,
                        description=f'[italic]FPS: {info.fps_current or ""}[/italic] - [underline] Average FPS: {info.fps_average or ""}',
                        completed=info.progress,
                    ),
                )

                progress.update(
                    all_videos_task,
                    advance=1,
                    description=f'Compressing videos ({idx + 1}/{len(self.video_files)}) {int((idx + 1) / len(self.video_files) * 100)}%',
                )
                progress.remove_task(current_compression)

        if self.options.show_stats:
            self.statistics_logger.log_stats()

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

        success = self.compressor.compress(
            video,
            output_video,
            on_update=on_progress_update or (lambda _: None),
        )

        if success:
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

            if (
                self.options.keep_only_smaller
                and output_video.stat().st_size > video.stat().st_size
            ):
                self.statistics.skip_file(video)
                log.info(
                    f"Skipped {video.name} ([yellow]didn't pass keep_only_smaller[/yellow])",
                    highlight=False,
                )
                output_video.unlink()
                return

            if self.options.delete_original_files:
                video.unlink()
