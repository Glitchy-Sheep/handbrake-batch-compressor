import os

from src.videofiles_traverser import get_video_files_paths
from test.conftest import VideoSampleData


def test_get_video_files_paths(generate_video_files_data: VideoSampleData):
    expected_path_count = len(generate_video_files_data.video_files)
    paths = list(get_video_files_paths(generate_video_files_data.path))
    assert len(paths) == expected_path_count


def test_is_absolute_path(generate_video_files_data: VideoSampleData):
    paths = list(get_video_files_paths(generate_video_files_data.path))

    for path in paths:
        assert os.path.isabs(path)
