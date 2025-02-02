"""
The module provides functions to apply smart filters on the videos.

It will be used to skip some files according to their properties like resolution, audio channels, etc.
"""

from pathlib import Path

from src.ffmpeg_helpers import VideoResolution, get_video_properties


class NotAFileError(Exception):
    """Exception raised when a video_path is not a file."""

    def __init__(self, video_path: Path) -> None:
        super().__init__(f'{video_path} is not a file.')


class SmartFilter:
    """
    Smart filter determines whether a video should be compressed or not.

    It considers the following parameters:
        - Resolution
        - Frame rate
        - Bitrate
    """

    def __init__(
        self,
        minimal_resolution: VideoResolution = None,
        minimal_bitrate_kbytes: int | None = None,
        minimal_frame_rate: int | None = None,
    ) -> None:
        self.minimal_resolution = minimal_resolution
        self.minimal_bitrate_kbytes = minimal_bitrate_kbytes
        self.minimal_frame_rate = minimal_frame_rate

    def should_compress(self, video_path: Path) -> bool:
        if not video_path.is_file():
            raise NotAFileError(video_path)

        video_properties = get_video_properties(video_path)
        if video_properties is None:
            return False

        actual_resolution = video_properties.resolution
        actual_bitrate_kbytes = video_properties.bitrate_kbytes
        actual_frame_rate = video_properties.frame_rate

        exceeds_bitrate = (
            self.minimal_bitrate_kbytes is None
            or actual_bitrate_kbytes >= self.minimal_bitrate_kbytes
        )
        exceeds_frame_rate = (
            self.minimal_frame_rate is None
            or actual_frame_rate >= self.minimal_frame_rate
        )
        exceeds_resolution = (
            self.minimal_resolution is None
            or actual_resolution >= self.minimal_resolution
        )

        count_of_filters = 3

        return (
            sum([exceeds_bitrate, exceeds_frame_rate, exceeds_resolution])
            == count_of_filters
        )
