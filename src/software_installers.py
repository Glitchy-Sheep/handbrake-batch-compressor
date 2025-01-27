import os
import subprocess

from pydantic import BaseModel

from src.logger import log


class InstallCommand(BaseModel):
    win: str
    linux: str
    mac: str

    def run(self):
        if os.name == "nt":
            cmd = self.win
        elif os.name == "posix":
            cmd = self.linux
        else:
            cmd = self.mac

        subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )


class Software:
    def __init__(self, install_cmd: InstallCommand, check_cmd: str):
        self.check_cmd = check_cmd
        self.install_cmd = install_cmd

    def is_installed(self):
        try:
            subprocess.run(
                self.check_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def install(self):
        self.install_cmd.run()


ffmpeg = Software(
    install_cmd=InstallCommand(
        win="winget install ffmpeg",
        linux="sudo apt-get install ffmpeg",
        mac="brew install ffmpeg",
    ),
    check_cmd="ffmpeg -version",
)

handbrake_cli = Software(
    install_cmd=InstallCommand(
        win="winget install Handbrake.Handbrake.CLI",
        linux="sudo apt-get install handbrake-cli",
        mac="brew install handbrake-cli",
    ),
    check_cmd="handbrakecli --version",
)
