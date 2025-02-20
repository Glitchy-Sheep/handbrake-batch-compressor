"""Module for Handbrake CLI and compression-related exceptions."""

from pathlib import Path


class CompressionFailedError(Exception):
    """Exception raised when the compression failed."""

    def __init__(self, input_video: Path, error_log_file: Path) -> None:
        self.error_log_file = error_log_file
        super().__init__(
            f'Compression failed for {input_video.name}. \nCheck {error_log_file} for details.',
        )
