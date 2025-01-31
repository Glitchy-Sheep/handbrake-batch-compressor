from src.ffmpeg_helpers import get_video_resolution


def test_get_video_resolution(video_720p_2mb_mp4):
    resolution = get_video_resolution(video_720p_2mb_mp4)

    assert resolution.width == 1280
    assert resolution.height == 720
    assert resolution.area == 921600
