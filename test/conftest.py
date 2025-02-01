import os
import shutil
from typing import Generator
from pydantic import BaseModel
import pytest

from src.videofiles_traverser import supported_videofile_extensions


@pytest.fixture
def video_720p_2mb_mp4():
    file = os.path.abspath(
        "test/natural_video_files/SampleVideo_1280x720_2mb.mp4",
    )
    assert os.path.exists(file), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_5mb_mp4():
    file = os.path.abspath(
        "test/natural_video_files/SampleVideo_1280x720_5mb.mp4",
    )
    assert os.path.exists(file), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_2mb_mkv():
    file = os.path.abspath(
        "test/natural_video_files/SampleVideo_1280x720_2mb.mkv",
    )
    assert os.path.exists(file), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_5mb_mkv():
    file = os.path.abspath(
        "test/natural_video_files/SampleVideo_1280x720_5mb.mkv",
    )
    assert os.path.exists(file), f"File {file} not found."
    return file


class VideoSampleData(BaseModel):
    path: str
    video_files: list[str]


@pytest.fixture
def generate_video_files_data() -> Generator[VideoSampleData, None, None]:
    """
    Create video files under /test/data with nested folders and junk files
    return the list of video files with
    """
    target_dir = "test/data"

    os.makedirs(target_dir, exist_ok=True)

    video_files = [f"test.{ext}" for ext in supported_videofile_extensions]
    video_files += [f"nested/test.{ext}" for ext in supported_videofile_extensions]

    fake_files = [
        "test.txt",
        "test.mp3",
        "nested/test.txt",
        "nested/test.mp3",
        "nested/test2/test.txt",
        "nested/test2/test.mp3",
    ]

    # Generate test data
    for file in video_files:
        file = os.path.abspath(os.path.join(target_dir, file))
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w"):
            pass

    # Generate junk to mess with
    for file in fake_files:
        file = os.path.abspath(os.path.join(target_dir, file))
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w"):
            pass

    yield VideoSampleData(
        path=target_dir,
        video_files=video_files,
    )

    shutil.rmtree(target_dir)
