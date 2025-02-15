"""Module for exceptions related to canceling compression by the user."""


class CompressionCancelledByUserError(Exception):
    """Exception raised when the compression is cancelled by the user."""

    def __init__(self) -> None:
        super().__init__('Compression cancelled by the user.')
