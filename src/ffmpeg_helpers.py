import av

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
    try:
        probe = av.open(video_path)
        width = probe.streams.video[0].width
        height = probe.streams.video[0].height
        probe.close()
        return VideoResolution(width=width, height=height)
    except Exception as e:
        log.error(f"Error getting video resolution: {e}")
        return None
