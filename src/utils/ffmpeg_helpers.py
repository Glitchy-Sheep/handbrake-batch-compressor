"""
The module provides functions to get the resolution of a video.

It will be used for smart filters.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import av
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path


class InvalidResolutionError(Exception):
    """Exception raised for an invalid resolution."""

    def __init__(self, resolution: str) -> None:
        super().__init__(f'Invalid resolution: {resolution}')


@functools.total_ordering
class VideoResolution(BaseModel):
    """Data class representing a video resolution."""

    width: int
    height: int

    def __str__(self) -> str:
        """Resolution representation e.g: 1280x720."""
        return f'{self.width}x{self.height}'

    def __eq__(self, other: object) -> bool:
        """
        Compare two resolutions for equality.

        Two resolutions are equal if their width and height are equal.
        """
        if not isinstance(other, VideoResolution):
            return False
        return self.width == other.width and self.height == other.height

    def __lt__(self, other: object) -> bool:
        """
        Compare two resolutions for being one less than the other.

        The comparison is done by comparing the area of the resolutions.
        For example, 1280x720 is less than 1280x719. (By 1280 pixels)
        """
        if not isinstance(other, VideoResolution):
            return False
        return self.area < other.area

    @property
    def area(self) -> int:
        """Calculate the area of the video resolution."""
        return self.width * self.height

    @staticmethod
    def parse_resolution(resolution: str) -> VideoResolution:
        if 'x' not in resolution:
            raise InvalidResolutionError(resolution)

        width, height = resolution.split('x')
        width = int(width)
        height = int(height)

        if width < 0 or height < 0:
            raise InvalidResolutionError(resolution)

        return VideoResolution(width=width, height=height)


class VideoProperties(BaseModel):
    """Basic video properties. (resolution, frame rate, bitrate)"""

    resolution: VideoResolution
    frame_rate: float
    bitrate_kbytes: int


def get_video_properties(video_path: Path) -> VideoProperties | None:
    """
    Get the resolution, frame rate and bitrate of a video as a VideoProperties object.

    If, for some reason, any of this properties can't be determined, return None.
    """
    try:
        probe = av.open(video_path)
        stream = probe.streams.video[0]
        resolution = VideoResolution(
            width=stream.width,
            height=stream.height,
        )
        frame_rate = stream.codec_context.framerate
        bitrate_kbytes = probe.bit_rate // 1024
        probe.close()
    except (av.InvalidDataError, IndexError):
        return None
    else:
        return VideoProperties(
            resolution=resolution,
            frame_rate=float(frame_rate),
            bitrate_kbytes=bitrate_kbytes,
        )
