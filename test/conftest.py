import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from pydantic import BaseModel

from src.videofiles_traverser import supported_videofile_extensions


@pytest.fixture
def video_720p_2mb_mp4():
    file = Path(
        "test/natural_video_files/SampleVideo_1280x720_2mb.mp4",
    )
    assert file.exists(), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_5mb_mp4():
    file = Path(
        "test/natural_video_files/SampleVideo_1280x720_5mb.mp4",
    )
    assert file.exists(), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_2mb_mkv():
    file = Path(
        "test/natural_video_files/SampleVideo_1280x720_2mb.mkv",
    )
    assert file.exists(), f"File {file} not found."
    return file


@pytest.fixture
def video_720p_5mb_mkv():
    file = Path(
        "test/natural_video_files/SampleVideo_1280x720_5mb.mkv",
    )
    assert file.exists(), f"File {file} not found."
    return file


class VideoSampleData(BaseModel):
    path: Path
    video_files: list[Path]


@pytest.fixture
def generate_video_files_data() -> Generator[VideoSampleData, None, None]:
    """
    Create video files under /test/data with nested folders and junk files
    return the list of video files with
    """
    target_dir = Path("test/data")

    Path.mkdir(target_dir, parents=True, exist_ok=True)

    video_files = [Path(f"test.{ext}") for ext in supported_videofile_extensions]
    video_files += [
        Path(f"nested/test.{ext}") for ext in supported_videofile_extensions
    ]

    fake_files = [
        Path("test.txt"),
        Path("test.mp3"),
        Path("nested/test.txt"),
        Path("nested/test.mp3"),
        Path("nested/test2/test.txt"),
        Path("nested/test2/test.mp3"),
    ]

    # Generate test data
    for file in video_files:
        fullpath = (target_dir / file).absolute()
        Path.mkdir(fullpath.parent, exist_ok=True, parents=True)
        with Path.open(fullpath, "w"):
            pass

    # Generate junk to mess with
    for fake_file in fake_files:
        fullpath = (target_dir / fake_file).absolute()
        Path.mkdir(fullpath.parent, exist_ok=True, parents=True)
        Path.write_text(fullpath, "")

    yield VideoSampleData(
        path=target_dir,
        video_files=video_files,
    )

    shutil.rmtree(target_dir)
