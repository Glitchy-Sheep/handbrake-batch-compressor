"""
The module provides functions to get the resolution of a video.

It will be used for smart filters.
"""

import av
from pydantic import BaseModel

from src.logger import log


class VideoResolution(BaseModel):
    """Data class representing a video resolution."""

    width: int
    height: int

    def __str__(self) -> str:
        """Resolution representation e.g: 1280x720."""
        return f'{self.width}x{self.height}'

    @property
    def area(self) -> int:
        """Calculate the area of the video resolution."""
        return self.width * self.height


def get_video_resolution(video_path: str) -> VideoResolution:
    """
    Get the resolution of a video as a VideoResolution object.

    If, for some reason, the resolution can't be determined, return None.
    """
    try:
        probe = av.open(video_path)
        width = probe.streams.video[0].width
        height = probe.streams.video[0].height
        probe.close()
        return VideoResolution(width=width, height=height)
    except (av.error.InvalidDataError, av.error.MediaTypeError, IndexError) as e:
        log.error(f'Error getting video resolution: {e}')
        return None
