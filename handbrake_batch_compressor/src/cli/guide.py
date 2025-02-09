"""Special guide to show if user specifies an --guide option."""

import sys

from src.cli.logger import log

GUIDE = """\

[bold green]===================[/bold green]
[bold green]HandBrake CLI Guide[/bold green]
[bold green]===================[/bold green]

This guide helps you configure HandBrake CLI settings for optimal video compression.

[bold green]Videos have three main properties that affect their size and quality:[/bold green]

  [bold italic red]Resolution[/bold italic red]
      [bold]What it is:[/bold] The width and height of the video (e.g., 1920x1080).
      [bold]What it affects:[/bold] Higher resolution improves clarity but increases file size. Lower resolution reduces size but may make the video look blurry.

  [bold italic red]Bitrate[/bold italic red]
      [bold]What it is:[/bold] The amount of data processed per second (e.g., 2000 kbps).
      [bold]What it affects:[/bold] Higher bitrate improves quality but increases file size. Lower bitrate reduces size but may introduce artifacts or loss of detail.

  [bold italic red]FPS (Frames Per Second)[/bold italic red]
      [bold]What it is:[/bold] The number of frames displayed per second (e.g., 24, 30, 60).
      [bold]What it affects:[/bold] Higher FPS makes motion smoother but increases file size. Lower FPS reduces size but may make motion look choppy.

[bold green]About --quality[/bold green]:

    It may seem strange, but:
    The higher the --quality value, the stronger the compression (smaller file size), but the lower the quality.
    (See https://handbrake.fr/docs/en/latest/workflow/adjust-quality.html)

    [bold green]CRF (--quality)             File Size[/bold green]
    18-20   Without losses      🟥 Big
    21-23   Great quality       🟧 Medium
    24-26   Good quality        🟨 Small
    27-30   Acceptable quality  🟩 Tiny
    31+     Strong artifacts    🟦 Very tiny

[bold green]About encoders and presets[/bold green]:

  [bold]What it is:[/bold] An encoder is a tool that compresses video into a specific format (e.g., H.264, H.265).
  Some encoders are using your GPU and some are using your CPU.
  Correct encoder can increase encoding speed.

  [bold green]Choosing an encoder:[/bold green]

      H.264: Best for compatibility and balanced performance.
      H.265: (HEVC): Better compression (smaller files) but requires more processing power sometimes.

  [bold green]GPU vs CPU:[/bold green]
    Choose between GPU and CPU encoding according to your system's capabilities.

      [bold]To use GPU[/bold] encoding choose one of the following encoders:
          - [italic]qsv_h264[/italic] or [italic]qsv_h265[/italic] for [blue]Intel Graphics[/blue]
          - [italic]vce_h264[/italic] or [italic]vce_h265[/italic] for [red]AMD[/red]
          - [italic]nvenc_h264[/italic] or [italic]nvenc_h265[/italic] for [green]Nvidia[/green]

      [bold]To use CPU[/bold] encoding choose one of the following encoders:
          - [italic]x264[/italic]
          - [italic]x265[/italic]

[bold yellow]If you don't know what options to set[/bold yellow]
[bold yellow]My advice is to set --handbrakecli-options to[/bold yellow]:

  [bold]-o "--encoder YOUR_BEST_ENCODER --quality 30 --preset 'Very Fast 720p30'"[/bold]

  These setting is a good compromise between quality and size.
  But you need to set your own encoder (see [bold green]GPU vs CPU[/bold green] above).
"""


def show_guide_and_exit() -> None:
    """Show the guide and exit."""
    log.console.print(GUIDE, highlight=True)
    sys.exit(0)
