"""
The module provides functions to get the resolution of a video.

It will be used for smart filters.
"""

from __future__ import annotations

import functools
from fractions import Fraction
from typing import TYPE_CHECKING

import av
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

    from av.container.input import InputContainer
    from av.video.stream import VideoStream


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


def estimate_fps_from_timestamps(
    container: InputContainer,
    stream: VideoStream,
) -> Fraction | None:
    """Estimate average FPS from timestamps for VFR (Variable Frame Rate) video."""
    timestamps: list[Fraction] = [
        Fraction(packet.pts, packet.time_base.denominator)  # Convert to Fraction
        for packet in container.demux(stream)
        if packet.pts is not None and packet.time_base is not None
    ]

    if len(timestamps) > 1:
        intervals = [j - i for i, j in zip(timestamps[:-1], timestamps[1:])]
        avg_interval = sum(intervals, start=Fraction(0)) / len(intervals)
        return Fraction(1, avg_interval) if avg_interval > 0 else None

    return None


def extract_bitrate_from_stream(
    container: InputContainer,
    stream: VideoStream,
) -> float:
    """
    Estimate FPS using the following methods:

    - Codec Context
    - Average Rate (if previous is unavailable)
    - Timestamps (if previous is unavailable)
    """
    fps = stream.codec_context.framerate
    if fps is None or fps == 0:
        fps = stream.average_rate
    if fps is None or fps == 0:
        fps = estimate_fps_from_timestamps(container, stream)
    if fps is None or fps == 0:
        fps = 1.0

    return float(fps)


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
        frame_rate = extract_bitrate_from_stream(probe, stream)
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
