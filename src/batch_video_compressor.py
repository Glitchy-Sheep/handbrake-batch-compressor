import os
import subprocess

from src.file_utils import FileUtils
from src.logger import log


class BatchVideoCompressor:
    def __init__(
        self,
        verbose: bool,
        delete_original_files: bool,
        video_files: set[str],
        progress_ext="compressing",
        complete_ext="compressed",
    ):
        self.progress_ext = progress_ext
        self.complete_ext = complete_ext
        self.video_files = video_files
        self.verbose = verbose
        self.delete_original_files = delete_original_files

    def compress_video(self, input_video: str, output_video: str):
        compress_cmd = [
            "handbrakecli",
            "-i",
            input_video,
            "-o",
            output_video,
            "--preset",
            "Fast 720p30",
            "--encoder",
            "qsv_h264",
            "--quality",
            "20",
        ]

        try:
            log.info(f"Compressing {os.path.basename(input_video)}")
            subprocess.run(
                compress_cmd,
                check=True,
                stdout=subprocess.PIPE if not self.verbose else None,
                stderr=subprocess.PIPE if not self.verbose else None,
            )
            log.info(f"Compressed {os.path.basename(input_video)}")
        except subprocess.CalledProcessError as e:
            log.error(f"Error compressing {input_video}: {e}")

    def compress_videos(self):
        for video in self.video_files:
            input_video = video

            # filename.ext -> filename.compressing.ext
            output_video = FileUtils.add_subextension(video, self.progress_ext)

            # Compress
            self.compress_video(input_video, output_video)

            # filename.compressing.ext -> filename.compressed.ext
            final_name = output_video.replace(self.progress_ext, self.complete_ext)
            os.rename(output_video, final_name)

            if self.delete_original_files:
                os.remove(input_video)
