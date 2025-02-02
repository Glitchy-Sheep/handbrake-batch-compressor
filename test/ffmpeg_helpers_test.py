from pathlib import Path

from src.ffmpeg_helpers import VideoProperties, VideoResolution, get_video_properties


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


def test_resolution_comparisons():
    res_1280x720 = VideoResolution(width=1280, height=720)
    res_1280x800 = VideoResolution(width=1280, height=800)
    res_1440x900 = VideoResolution(width=1440, height=900)
    res_1920x1080 = VideoResolution(width=1920, height=1080)

    assert res_1280x800 == VideoResolution.parse_resolution('1280x800')
    assert res_1280x720 < res_1280x800
    assert res_1280x720 < res_1440x900
    assert res_1280x720 < res_1920x1080

    assert res_1440x900 <= VideoResolution.parse_resolution('1440x900')
