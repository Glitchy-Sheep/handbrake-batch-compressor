"""The module provides helper functions to work with files."""

import os
from collections.abc import Generator
from pathlib import Path

supported_videofile_extensions = {
    'mp4',
    'mkv',
    'avi',
    'mov',
    'wmv',
    'flv',
    'webm',
    'm4v',
    '3gp',
}


def human_readable_size(size: int, decimal_places: int = 2) -> str:
    """
    Return a human-readable string representing the size of a file.

    Usage example:
        path = Path("example.txt")

        file_size = path.stat().st_size  # Get file size in bytes
        print(human_readable_size(file_size))
    """
    kb_size = 1024

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < kb_size:
            return f'{size:.{decimal_places}f} {unit}'
        size /= kb_size
    return f'{size:.{decimal_places}f} PB'


def get_video_files_paths(path: str) -> Generator[str, None, None]:
    """Get all video files paths in a directory."""
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(supported_videofile_extensions)):
                yield (Path(root) / file).absolute()
