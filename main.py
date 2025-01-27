import os

import typer

from src.cli_helpers import install_package, is_ffmpeg_installed
from src.logger import log


def main(target_path):
    target_path = os.path.abspath(target_path)
    if not os.path.isdir(target_path):
        log.error("Your target path is not a directory or doesn't exist")
        return

    if not is_ffmpeg_installed():
        log.wait("Installing FFmpeg...")
        install_package("ffmpeg")

    log.success("FFmpeg is installed.")


if __name__ == "__main__":
    typer.run(main)
