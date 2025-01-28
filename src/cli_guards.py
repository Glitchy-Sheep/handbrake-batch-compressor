import os

from src.logger import log


def check_target_path(target_path):
    target_path = os.path.abspath(target_path)
    if not os.path.isdir(target_path):
        log.error("Your target path is not a directory or doesn't exist")
        exit(1)


def check_extensions_arguments(progress_ext, complete_ext):
    if progress_ext.count(".") > 0 or complete_ext.count(".") > 0:
        log.error("Progress and complete extensions cannot contain dots.")
        exit(1)

    if progress_ext == complete_ext:
        log.error("Progress and complete extensions cannot be the same.")
        exit(1)

    if len(progress_ext) == 0 or len(complete_ext) == 0:
        log.error("Progress and complete extensions cannot be empty.")
        exit(1)
