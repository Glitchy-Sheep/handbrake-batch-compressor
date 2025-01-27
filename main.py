import os

import typer

from src.batch_video_compressor import BatchVideoCompressor
from src.software_installers import ffmpeg, handbrake_cli
from src.logger import log
from src.videofiles_traverser import get_video_files_paths


def setup_software():
    if not ffmpeg.is_installed():
        log.wait("Installing FFmpeg...")
        ffmpeg.install()

    log.success("FFmpeg is installed.")

    if not handbrake_cli.is_installed():
        log.wait("Installing Handbrake CLI...")
        handbrake_cli.install()

    log.success("Handbrake CLI is installed.")


def main(target_path):
    target_path = os.path.abspath(target_path)
    if not os.path.isdir(target_path):
        log.error("Your target path is not a directory or doesn't exist")
        return

    setup_software()

    log.wait("Collecting all your video files...")
    video_files = list(get_video_files_paths(target_path))

    if len(video_files) == 0:
        log.error("No video files found.")
        return

    log.success(f"Found {len(video_files)} video files.")


if __name__ == "__main__":
    typer.run(main)
