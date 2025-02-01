"""Get all video files paths (recursively) in a directory using known video file extensions."""

import os
from collections.abc import Generator
from pathlib import Path

supported_videofile_extensions = {
    "mp4",
    "mkv",
    "avi",
    "mov",
    "wmv",
    "flv",
    "webm",
    "m4v",
    "3gp",
}


def get_video_files_paths(path: str) -> Generator[str, None, None]:
    """Get all video files paths in a directory."""
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(supported_videofile_extensions)):
                yield (Path(root) / file).absolute()
