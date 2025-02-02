"""Logger for the application."""

import logging

from rich.console import Console
from rich.logging import RichHandler

_console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[
        RichHandler(console=_console, show_path=False),
    ],
)


class AppLogger:
    """Wrapper around the logging library with some extra features."""

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)
        self.console = _console

    def info(self, msg: str, *, should_log: bool = True) -> None:
        if should_log:
            self._log.info(f"ℹ {msg}")

    def success(self, msg: str, *, should_log: bool = True) -> None:
        if should_log:
            self._log.info(f"✔ {msg}")

    def error(self, msg: str, *, should_log: bool = True) -> None:
        if should_log:
            self._log.error(f"❌ {msg}")

    def wait(self, msg: str, *, should_log: bool = True) -> None:
        if should_log:
            self._log.info(f"⏳ {msg}")

    def skip_lines(self, count: int) -> None:
        self.console.print("\n" * count, end="")


log = AppLogger()
