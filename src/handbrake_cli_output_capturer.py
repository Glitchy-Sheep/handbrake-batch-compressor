import re
import datetime

from pydantic import BaseModel
from typing import Optional


class HandbrakeProgressInfo(BaseModel):
    progress: str
    fps_current: Optional[str]
    fps_average: Optional[str]
    eta: Optional[str]


def parse_handbrake_cli_output(line: str) -> HandbrakeProgressInfo:
    # Extract percentage
    progress_match = re.search(r"(\d+\.\d+) %", line)
    progress = f"{progress_match.group(1)}%" if progress_match else None

    # Get current FPS
    fps_current_match = re.search(r"([\d.]+) fps", line)
    fps_current = f"{fps_current_match.group(1)} fps" if fps_current_match else None

    # Get Average FPS
    fps_avg_match = re.search(r"avg ([\d.]+) fps", line)
    fps_avg = f"{fps_avg_match.group(1)} fps" if fps_avg_match else None

    # Extract ETA
    eta_match = re.search(r"ETA (\d+h\d+m\d+s)", line)
    eta = None
    if eta_match:
        h, m, s = map(int, re.findall(r"\d+", eta_match.group(1)))
        eta = str(datetime.timedelta(hours=h, minutes=m, seconds=s))

    return HandbrakeProgressInfo(
        progress=progress,
        fps_current=fps_current,
        fps_average=fps_avg,
        eta=eta,
    )
