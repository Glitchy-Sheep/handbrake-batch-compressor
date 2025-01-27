import ffmpeg

from pydantic import BaseModel

from src.logger import log


class VideoResolution(BaseModel):
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def area(self) -> int:
        return self.width * self.height


def get_video_resolution(video_path: str) -> VideoResolution:
    """
    Get the resolution of a video as a VideoResolution object
    if, for some reason, the resolution can't be determined, return None
    """
    probe = ffmpeg.probe(video_path)
    try:
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        return VideoResolution(
            width=video_stream["width"],
            height=video_stream["height"],
        )
    except:
        return None
