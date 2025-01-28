import os

import typer

from src.batch_video_compressor import BatchVideoCompressor
from src.third_party_installers import setup_software
from src.logger import log
from src.videofiles_traverser import get_video_files_paths


def check_target_path(target_path):
    target_path = os.path.abspath(target_path)
    if not os.path.isdir(target_path):
        log.error("Your target path is not a directory or doesn't exist")
        return


def get_video_files(target_path):
    log.wait("Collecting all your video files...")
    video_files = set(get_video_files_paths(target_path))

    if len(video_files) == 0:
        log.error("No video files found.")
        return

    log.success(f"Found {len(video_files)} video files.")
    return video_files


def find_incomplete_files(video_files: list[str], progress_ext: str) -> list[str]:
    """
    Find all files with the progress extension indicating
    that they were not processed properly.
    """
    return [file for file in video_files if file.endswith(progress_ext)]


def find_complete_files(video_files: list[str], complete_ext) -> list[str]:
    return [file for file in video_files if file.endswith(complete_ext)]


def remove_incomplete_files(incomplete_files) -> int:
    """
    Remove incomplete files and update the task queue.
    """
    deleted_count = 0
    for file in incomplete_files:
        try:
            os.remove(file)
            deleted_count += 1
        except OSError as e:
            log.error(f"Failed to remove file {file}: {e}")

    if deleted_count > 0:
        log.success(f"Deleted {deleted_count} incomplete files.")


def main(target_path, progress_ext="compressing.mp4", complete_ext="compressed.mp4"):
    check_target_path(target_path)
    setup_software()

    # All video files, unprocessed, processed and incomplete
    video_files = get_video_files(target_path)

    # Completed files should be ignored as its originals
    completed_files = find_complete_files(video_files, complete_ext)

    # All incomplete files should be deleted and ignored
    incomplete_files = find_incomplete_files(video_files, progress_ext)

    remove_incomplete_files(incomplete_files)

    unprocessed_files = [
        file
        for file in video_files
        if file not in completed_files and file not in incomplete_files
    ]

    compressor = BatchVideoCompressor(unprocessed_files)
    compressor.compress_videos()


if __name__ == "__main__":
    typer.run(main)
