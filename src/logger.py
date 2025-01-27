import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


class AppLogger:
    def __init__(self):
        self._log = logging.getLogger(__name__)

    def info(self, msg):
        self._log.info(f"ℹ {msg}")

    def success(self, msg):
        self._log.info(f"✔ {msg}")

    def error(self, msg):
        self._log.error(f"❌ {msg}")

    def wait(self, msg):
        self._log.info(f"⏳ {msg}")


log = AppLogger()
