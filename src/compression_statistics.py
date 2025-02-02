"""
The module provides class for tracking statistics about the compression process.

As such as the number of files processed, their size, how many was skipped, etc.
"""

from pathlib import Path

from pydantic import BaseModel


class SizeDifferenceStatistics(BaseModel):
    """
    Represents the difference between two sizes.

    And rate between them.

    Usage example:
        SizeDifferenceStatistics(
            initial_size=1024,
            final_size=2048,
        )
    """

    initial_size_bytes: int
    final_size_bytes: int

    def _calculate_compression_rate(self, initial_size: int, final_size: int) -> str:
        """
        Differnece in percentage between initial and final file size.

        In a formatted string.

        e.g: +50%, -20%
        """
        if final_size == initial_size:
            return '0%'

        compression_rate_sign = '-' if final_size < initial_size else '+'

        return f'{compression_rate_sign}{
            round(
                abs((final_size - initial_size) / initial_size * 100),
            )
        }%'

    @property
    def compression_rate(self) -> str:
        """
        Difference in percentage between initial and final file size.

        In a formatted string.

        e.g: +50%, -20%
        """
        return self._calculate_compression_rate(
            initial_size=self.initial_size_bytes,
            final_size=self.final_size_bytes,
        )

    @property
    def diff_size_bytes(self) -> int:
        """
        The difference between the initial and final size of the file.

        In bytes.
        """
        return self.final_size_bytes - self.initial_size_bytes


class FileStatistics(SizeDifferenceStatistics):
    """
    Represents statistics about a single file successfull compression.

    Such as its initial and final size, and the difference between them.
    """

    path: Path

    def __hash__(self) -> int:
        """Use path as the hash for set/hash based operations."""
        return hash(self.path)


class GeneralStatistics(SizeDifferenceStatistics):
    """Represents statistics about the complete compression process."""

    files_processed: int
    files_skipped: int


class CompressionStatistics:
    """The class watches the compression process and tracks statistics about it."""

    def __init__(self) -> None:
        self._general_stats = GeneralStatistics(
            files_processed=0,
            files_skipped=0,
            final_size_bytes=0,
            initial_size_bytes=0,
        )
        self.files_statistics: set[FileStatistics] = set()

    def add_compression_info(
        self,
        input_file: Path,
        output_file: Path,
    ) -> FileStatistics:
        """Add a new compression info based on the given input and output files."""
        input_size = input_file.stat().st_size
        output_size = output_file.stat().st_size

        self._general_stats.files_processed += 1
        self._general_stats.final_size_bytes += output_size
        self._general_stats.initial_size_bytes += input_size

        file_stat = FileStatistics(
            path=input_file,
            initial_size_bytes=input_size,
            final_size_bytes=output_size,
        )

        self.files_statistics.add(file_stat)

        return file_stat

    @property
    def overall_stats(self) -> GeneralStatistics:
        """Returns statistics about the complete compression process."""
        return self._general_stats
