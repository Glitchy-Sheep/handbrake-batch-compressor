import os

import typer

from src.batch_video_compressor import BatchVideoCompressor
from src.file_utils import FileUtils
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


def remove_incomplete_files(incomplete_files) -> int:
    """
    Remove incomplete files and update the task queue.
    """
    for file in incomplete_files:
        try:
            os.remove(file)
        except OSError as e:
            log.error(f"Failed to remove file {file}: {e}")


def main(
    target_path: str,
    progress_ext: str = "compressing",
    complete_ext: str = "compressed",
    verbose: bool = False,
):
    check_target_path(target_path)
    setup_software()

    if progress_ext.count(".") > 0 or complete_ext.count(".") > 0:
        log.error("Progress and complete extensions cannot contain dots.")
        return

    # All video files, unprocessed, processed and incomplete
    video_files = get_video_files(target_path)

    complete_files = set()
    incomplete_files = set()
    unprocessed_files = set()

    for file in video_files:
        extensions = FileUtils.extension_set(file)
        if complete_ext in extensions:
            complete_files.add(file)
        elif progress_ext in extensions:
            incomplete_files.add(file)
        else:
            unprocessed_files.add(file)

    for file in map(FileUtils.filename_with_original_extension, complete_files):
        print(file)
        unprocessed_files.discard(file)

    log.info(f"Found complete files: {len(complete_files)}")
    log.info(f"Found incomplete files: {len(incomplete_files)}")
    log.info(f"Found unprocessed files: {len(unprocessed_files)}")

    if len(incomplete_files) > 0:
        remove_incomplete_files(incomplete_files)
        log.success(f"Removed {len(incomplete_files)} incomplete files. 🧹✨")

    compressor = BatchVideoCompressor(
        verbose=verbose,
        video_files=unprocessed_files,
        progress_ext=progress_ext,
        complete_ext=complete_ext,
    )
    compressor.compress_videos()


if __name__ == "__main__":
    typer.run(main)
