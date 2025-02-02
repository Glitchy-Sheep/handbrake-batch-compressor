"""The module provides a class to install a software on Windows, Linux, and macOS."""

import os
import subprocess

from pydantic import BaseModel

from src.logger import log


class InstallCommand(BaseModel):
    """
    Class representing a command to install a software on Windows, Linux, and macOS.

    You should specify how to install the software on each platform.
    """

    win: str
    linux: str
    mac: str

    def run(self) -> None:
        """
        Run the install command for the current platform.

        The platform is detected using the `os.name` variable.
        """
        if os.name == 'nt':
            cmd = self.win
        elif os.name == 'posix':
            cmd = self.linux
        else:
            cmd = self.mac

        subprocess.run(  # noqa: S603, warning about unsanitized subprocess
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )


class Software:
    """
    Class representing a software to install.

    You should specify how to check if the software is installed and how to install it.
    """

    def __init__(self, install_cmd: InstallCommand, check_cmd: str) -> None:
        self.check_cmd = check_cmd
        self.install_cmd = install_cmd

    def is_installed(self) -> bool:
        try:
            subprocess.run(  # noqa: S603 , warning about unsanitized subprocess
                self.check_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def install(self) -> None:
        self.install_cmd.run()


def setup_software() -> None:
    """
    Install all the required software for the script to work.

    Including: FFmpeg and Handbrake CLI.
    """
    ffmpeg = Software(
        install_cmd=InstallCommand(
            win='winget install ffmpeg',
            linux='sudo apt-get install ffmpeg',
            mac='brew install ffmpeg',
        ),
        check_cmd='ffmpeg -version',
    )

    handbrake_cli = Software(
        install_cmd=InstallCommand(
            win='winget install Handbrake.Handbrake.CLI',
            linux='sudo apt-get install handbrake-cli',
            mac='brew install handbrake-cli',
        ),
        check_cmd='handbrakecli --version',
    )

    if not ffmpeg.is_installed():
        log.wait('Installing FFmpeg...')
        ffmpeg.install()

    log.success('FFmpeg is installed.')

    if not handbrake_cli.is_installed():
        log.wait('Installing Handbrake CLI...')
        handbrake_cli.install()

    log.success('Handbrake CLI is installed.')
