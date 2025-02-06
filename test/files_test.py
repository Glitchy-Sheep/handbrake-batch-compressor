from src.utils.files import get_video_files_paths, human_readable_size
from test.conftest import VideoSampleData


def test_get_video_files_paths(generate_video_files_data: VideoSampleData):
    expected_path_count = len(generate_video_files_data.video_files)
    paths = list(get_video_files_paths(generate_video_files_data.path))
    assert len(paths) == expected_path_count


def test_is_absolute_path(generate_video_files_data: VideoSampleData):
    paths = list(get_video_files_paths(generate_video_files_data.path))

    for path in paths:
        assert path.is_absolute()


def test_human_readable_size():
    assert human_readable_size(1024) == '1.00 KB'
    assert human_readable_size(1048576) == '1.00 MB'
    assert human_readable_size(1073741824) == '1.00 GB'
    assert human_readable_size(1099511627776) == '1.00 TB'
    assert human_readable_size(1125899906842624) == '1.00 PB'
    assert human_readable_size(245323223) == '233.96 MB'  # just some random float
