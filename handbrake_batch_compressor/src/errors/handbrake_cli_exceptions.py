"""Module for Handbrake CLI and compression-related exceptions."""

from pathlib import Path


class CompressionFailedError(Exception):
    """Exception raised when the compression failed."""

    def __init__(self, input_video: Path, stderr_log_filename: Path) -> None:
        super().__init__(
            f'Compression failed for {input_video.name}. \nCheck {stderr_log_filename} for details.',
        )
