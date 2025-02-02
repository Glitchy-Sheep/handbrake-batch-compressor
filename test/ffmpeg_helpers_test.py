from pathlib import Path

from src.ffmpeg_helpers import (
    get_video_bitrate,
    get_video_frame_rate,
    get_video_resolution,
)


def test_get_video_resolution(video_720p_2mb_mp4: Path):
    resolution = get_video_resolution(video_720p_2mb_mp4)

    assert resolution.width == 1280
    assert resolution.height == 720
    assert resolution.area == 921600


def test_get_video_bitrate(video_720p_2mb_mp4: Path):
    bitrate = get_video_bitrate(video_720p_2mb_mp4)

    assert bitrate == 842


def test_get_video_frame_rate(video_720p_2mb_mp4: Path):
    frame_rate = get_video_frame_rate(video_720p_2mb_mp4)

    assert frame_rate == 25.0
