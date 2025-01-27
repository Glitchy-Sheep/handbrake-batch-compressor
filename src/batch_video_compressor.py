import os
import subprocess

from src.logger import log


class BatchVideoCompressor:
    def __init__(
        self,
        video_files: list[str],
        progress_ext=".compressing.mp4",
        complete_ext=".compressed.mp4",
    ):
        self.progress_ext = progress_ext
        self.complete_ext = complete_ext
        self.video_files = video_files

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
            subprocess.run(compress_cmd, check=True)
            log.info(f"Compressed {input_video} to {output_video}")
        except subprocess.CalledProcessError as e:
            log.error(f"Error compressing {input_video}: {e}")

    def compress_videos(self):
        for video in self.video_files:
            input_video = video
            input_video_ext = os.path.splitext(video)[1]

            output_video = video.replace(input_video_ext, self.progress_ext)
            self.compress_video(input_video, output_video)

            final_name = output_video.replace(self.progress_ext, self.complete_ext)

            while os.path.exists(final_name):
                final_name = final_name.replace(
                    self.complete_ext,
                    f"_{self.complete_ext}",
                )

            os.rename(output_video, final_name)
