import os


class FileUtils:
    """
    Helper class for working with filenames in a more convenient way
    """

    @staticmethod
    def base_name(filename):
        """
        Convert filename to its base name without directories
        and extensions.

        e.g:
            filename = "path/to/file.extra.ext.mp4"
            base_name = "file"
        """
        filename = os.path.basename(filename)

        first_dot = filename.find(".")
        if first_dot == -1:
            return filename

        return filename[:first_dot]

    @staticmethod
    def extension_set(filename: str) -> set[str]:
        """
        Convert filename to a set of its extensions

        e.g:
            filename = "path/to/file.extra.ext.mp4"
            extensions = {"extra", "ext", "mp4"}
        """
        filename = os.path.basename(filename)

        if len(filename) <= 1:
            return set()

        splitted_filename = filename.split(".")
        return set(splitted_filename[1:])

    @staticmethod
    def last_extension(filename: str) -> str:
        """
        Convert filename to its last extension

        e.g:
            filename = "path/to/file.extra.ext.mp4"
            extension = "mp4"
        """
        filename = os.path.basename(filename)
        splitted_filename = filename.split(".")
        return splitted_filename[-1] if len(splitted_filename) > 1 else ""

    @staticmethod
    def add_subextension(filename: str, subextension: str) -> str:
        """
        Add a subextension to a filename

        e.g:
            filename = "path/to/file.mp4"
            subextension = "extra"
            result_filename = "path/to/file.extra.mp4"
        """
        parent = os.path.dirname(filename)
        filename = os.path.basename(filename)

        first_dot = filename.find(".")
        last_dot = filename.rfind(".")

        if first_dot == -1:
            return os.path.join(parent, f"{filename}.{subextension}")

        return os.path.join(
            parent,
            f"{filename[:first_dot]}.{subextension}{filename[last_dot:]}",
        )

    @staticmethod
    def filename_with_original_extension(filename: str) -> str:
        """
        Convert filename to its original extension

        e.g:
            filename = "path/to/file.extra.ext.mp4"
            original_extension = "mp4"
            result_filename = file.mp4
        """
        parent = os.path.dirname(filename)
        filename = os.path.basename(filename)

        first_dot = filename.find(".")
        last_dot = filename.rfind(".")

        if first_dot == last_dot:
            return os.path.join(parent, filename)

        return os.path.join(
            parent, f"{filename[:first_dot]}.{filename[last_dot + 1 :]}"
        )
