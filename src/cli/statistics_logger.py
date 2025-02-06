"""A module for logging compression statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.markup import escape

from src.utils.files import human_readable_size

if TYPE_CHECKING:
    from src.cli.logger import AppLogger
    from src.compression.compression_statistics import (
        CompressionStatistics,
        FileStatistics,
    )


class StatisticsLogger:
    """
    A class for logging compression statistics.

    It uses the AppLogger implementation to log the statistics.
    """

    def __init__(self, statistics: CompressionStatistics, logger: AppLogger) -> None:
        self.statistics = statistics
        self.log = logger

    def log_stats(self, info: FileStatistics | None = None) -> None:
        """Log the compression stats for the given file or overall stats if info is not provided."""
        # Determine stats based on input (file-specific or overall)
        stats = info if info else self.statistics.overall_stats

        # Format compression rate and sizes
        is_positive = '+' not in stats.compression_rate
        color = 'green' if is_positive else 'red'
        bold = ' bold' if is_positive else ''

        compression_rate = (
            f'[{color}{bold}]{escape(stats.compression_rate)}[/{color}{bold}]'
        )
        init_size = (
            f'[{color}]{human_readable_size(stats.initial_size_bytes)}[/{color}]'
        )
        final_size = f'[{color}]{human_readable_size(stats.final_size_bytes)}[/{color}]'

        # Log the message, adjusting for file path if necessary
        if info:
            self.log.success(
                f'Compressed {info.path.name} (size: {init_size} -> {final_size}) {compression_rate}',
                highlight=False,
            )
        else:
            self.log.success(
                f'Overall stats: {compression_rate} (size: {init_size} -> {final_size})',
                highlight=False,
            )
            if self.statistics.overall_stats.files_skipped > 0:
                self.log.info(
                    f'Skipped {self.statistics.overall_stats.files_skipped} files',
                )
