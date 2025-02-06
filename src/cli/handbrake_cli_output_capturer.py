"""
The module provides a function to parse Handbrake CLI output and return a HandbrakeProgressInfo object.

This object contains the progress, current FPS, average FPS, and ETA.
"""

import datetime
import re

from pydantic import BaseModel


class HandbrakeProgressInfo(BaseModel):
    """Model representing the progress information captured from Handbrake CLI output."""

    progress: float | None
    fps_current: float | None
    fps_average: float | None
    eta: datetime.timedelta | None


def parse_handbrake_cli_output(line: str) -> HandbrakeProgressInfo:
    """Parse a line of Handbrake CLI output and returns a HandbrakeProgressInfo object."""
    # Extract percentage
    progress_match = re.search(r'(\d+\.\d+) %', line)
    progress = float(progress_match.group(1)) if progress_match else None

    # Get current FPS
    fps_current_match = re.search(r'([\d.]+) fps', line)
    fps_current = float(fps_current_match.group(1)) if fps_current_match else None

    # Get Average FPS
    fps_avg_match = re.search(r'avg ([\d.]+) fps', line)
    fps_avg = float(fps_avg_match.group(1)) if fps_avg_match else None

    # Extract ETA
    eta_match = re.search(r'ETA (\d+h\d+m\d+s)', line)
    eta = None
    if eta_match:
        h, m, s = map(int, re.findall(r'\d+', eta_match.group(1)))
        eta = datetime.timedelta(hours=h, minutes=m, seconds=s)

    return HandbrakeProgressInfo(
        progress=progress,
        fps_current=fps_current,
        fps_average=fps_avg,
        eta=eta,
    )
