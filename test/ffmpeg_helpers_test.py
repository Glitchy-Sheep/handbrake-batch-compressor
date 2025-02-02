from pathlib import Path

from src.ffmpeg_helpers import VideoProperties, get_video_properties


def test_get_video_resolution(video_720p_2mb_mp4: Path):
    video_properties: VideoProperties = get_video_properties(
        video_720p_2mb_mp4,
    )

    assert video_properties.resolution.width == 1280
    assert video_properties.resolution.height == 720
    assert video_properties.resolution.area == 921600

    assert str(video_properties.resolution) == '1280x720'

    assert video_properties.bitrate_kbytes == 842
    assert video_properties.frame_rate == 25.0
