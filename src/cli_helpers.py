import os
import subprocess

from src.logger import log


def is_ffmpeg_installed():
    try:
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        return False


def clear_scr():
    os.system("cls" if os.name == "nt" else "clear")


def install_package(package_name):

    if os.name == "nt":
        install_command = f"winget install {package_name}"
    elif os.name == "posix":
        install_command = f"sudo apt-get install {package_name}"
    else:
        log.error(
            "Can't install ffmpeg on your OS automatically.\n"
            "Please install it manually."
        )
        exit(1)

    try: 
        subprocess.run(install_command, shell=True)
    except subprocess.CalledProcessError:
        log.error(f"Failed to install {package_name}, please install it manually.")
        exit(1)
