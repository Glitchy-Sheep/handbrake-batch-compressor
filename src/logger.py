import logging

from rich.logging import RichHandler
from rich.console import Console

_console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[
        RichHandler(console=_console, show_path=False),
    ],
)


class AppLogger:
    def __init__(self):
        self._log = logging.getLogger(__name__)
        self.console = _console

    def info(self, msg, should_log=True):
        if should_log:
            self._log.info(f"ℹ {msg}")

    def success(self, msg, should_log=True):
        if should_log:
            self._log.info(f"✔ {msg}")

    def error(self, msg, should_log=True):
        if should_log:
            self._log.error(f"❌ {msg}")

    def wait(self, msg, should_log=True):
        if should_log:
            self._log.info(f"⏳ {msg}")

    def skip_lines(self, count):
        for _ in range(count):
            print("")


log = AppLogger()
