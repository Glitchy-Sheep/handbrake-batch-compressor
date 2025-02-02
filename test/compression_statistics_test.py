from pathlib import Path

import pytest

from src.compression_statistics import CompressionStatistics


@pytest.fixture
def video_files(tmp_path: Path, request: pytest.FixtureRequest) -> tuple[Path, Path]:
    input_size = request.param['input_size']
    output_size = request.param['output_size']

    input_file = tmp_path / 'input.mp4'
    output_file = tmp_path / 'output.mp4'

    input_file.write_bytes(bytearray(input_size))
    output_file.write_bytes(bytearray(output_size))

    return input_file, output_file


@pytest.mark.parametrize(
    'video_files',
    [
        {'input_size': 50, 'output_size': 100},
    ],
    indirect=True,
)
def test_per_file_statistics_output_larger(video_files: tuple[Path, Path]):
    statistics = CompressionStatistics()

    input_file, output_file = video_files

    info = statistics.add_compression_info(input_file, output_file)

    assert info.path == input_file
    assert info.initial_size_bytes == 50
    assert info.final_size_bytes == 100
    assert info.diff_size_bytes == 50
    assert info.compression_rate == '+100%'


@pytest.mark.parametrize(
    'video_files',
    [
        {'input_size': 100, 'output_size': 50},
    ],
    indirect=True,
)
def test_per_file_statistics_input_larger(video_files: tuple[Path, Path]):
    statistics = CompressionStatistics()

    input_file, output_file = video_files

    info = statistics.add_compression_info(input_file, output_file)

    assert info.path == input_file
    assert info.initial_size_bytes == 100
    assert info.final_size_bytes == 50
    assert info.diff_size_bytes == -50
    assert info.compression_rate == '-50%'


@pytest.mark.parametrize(
    'video_files',
    [
        {'input_size': 0, 'output_size': 0},
    ],
    indirect=True,
)
def test_per_file_statistics_same_size(video_files: tuple[Path, Path]):
    statistics = CompressionStatistics()

    input_file, output_file = video_files

    info = statistics.add_compression_info(input_file, output_file)

    assert info.path == input_file
    assert info.initial_size_bytes == 0
    assert info.final_size_bytes == 0
    assert info.diff_size_bytes == 0
    assert info.compression_rate == '0%'


@pytest.mark.parametrize(
    'video_files',
    [
        {'input_size': 100, 'output_size': 50},
    ],
    indirect=True,
)
def test_general_statistics(video_files: tuple[Path, Path]):
    statistics = CompressionStatistics()

    input_file, output_file = video_files

    files_count = 3

    for _ in range(files_count):
        statistics.add_compression_info(input_file, output_file)

    info = statistics.overall_stats

    assert info.files_processed == files_count
    assert info.files_skipped == 0

    assert info.final_size_bytes == files_count * 50
    assert info.initial_size_bytes == files_count * 100
    assert info.compression_rate == '-50%'
