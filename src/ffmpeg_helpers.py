"""
The module provides functions to get the resolution of a video.

It will be used for smart filters.
"""

import av
from pydantic import BaseModel

from src.logger import log


class InvalidResolutionError(Exception):
    """Exception raised for an invalid resolution."""

    def __init__(self, resolution: str) -> None:
        super().__init__(f'Invalid resolution: {resolution}')


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

    @staticmethod
    def parse_resolution(resolution: str) -> 'VideoResolution':
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
    frame_rate: int
    bitrate_kbytes: int


def get_video_properties(video_path: str) -> VideoProperties | None:
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
        bitrate_kbytes = stream.codec_context.bit_rate // 1024
        probe.close()
        return VideoProperties(
            resolution=resolution,
            frame_rate=frame_rate,
            bitrate_kbytes=bitrate_kbytes,
        )
    except (av.error.InvalidDataError, IndexError) as e:
        log.error(f'Error getting video properties: {e}')
        return None
