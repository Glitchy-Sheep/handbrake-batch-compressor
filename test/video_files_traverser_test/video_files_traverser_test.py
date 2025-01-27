import pytest
import os
import shutil

from src.videofiles_traverser import (
    get_video_files_paths,
    supported_videofile_extensions,
)


@pytest.fixture
def generate_video_files_data():
    os.makedirs("data", exist_ok=True)

    # generate plain video files
    for ext in supported_videofile_extensions:
        with open(f"data/test{ext}", "w"):
            pass

    # generate nested video files
    os.makedirs("data/nested", exist_ok=True)
    for ext in supported_videofile_extensions:
        with open(f"data/nested/test{ext}", "w"):
            pass

    yield

    shutil.rmtree("data")


def test_get_video_files_paths(generate_video_files_data):
    # nested and plain video files
    expected_path_count = len(supported_videofile_extensions) * 2

    paths = list(get_video_files_paths("data"))

    assert len(paths) == expected_path_count


def test_is_absolute_path(generate_video_files_data):
    paths = list(get_video_files_paths("/data"))
    assert all(paths is os.path.abspath(path) for path in paths)
