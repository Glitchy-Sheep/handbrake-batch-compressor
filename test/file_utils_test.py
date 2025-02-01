import os

from src.file_utils import FileUtils


class TestBaseName:
    def test_base_name_with_extension(self):
        assert FileUtils.base_name(os.path.join("path", "to", "file.mp4")) == "file"

    def test_base_name_without_extension(self):
        assert FileUtils.base_name("plainfile") == "plainfile"

    def test_base_name_with_empty_string(self):
        assert FileUtils.base_name("") == ""

    def test_base_name_with_only_dot(self):
        assert FileUtils.base_name(os.path.sep) == ""


class TestExtensionSet:
    def test_extension_set_with_extension(self):
        assert FileUtils.extension_set(os.path.join("path", "to", "file.mp4")) == {
            "mp4",
        }

    def test_extension_set_with_multiple_extensions(self):
        assert FileUtils.extension_set(
            os.path.join("path", "to", "file.mp4.extra"),
        ) == {"mp4", "extra"}

    def test_extension_set_without_extension(self):
        assert FileUtils.extension_set("plainfile") == set()

    def test_extension_set_with_empty_string(self):
        assert FileUtils.extension_set("") == set()

    def test_extension_set_with_only_dot(self):
        assert FileUtils.extension_set(os.path.sep) == set()


class TestLastExtension:
    def test_last_extension_with_extension(self):
        assert FileUtils.last_extension(os.path.join("path", "to", "file.mp4")) == "mp4"

    def test_last_extension_without_extension(self):
        assert FileUtils.last_extension("plainfile") == ""

    def test_last_extension_with_empty_string(self):
        assert FileUtils.last_extension("") == ""

    def test_last_extension_with_only_dot(self):
        assert FileUtils.last_extension(os.path.sep) == ""


class TestAddSubextension:
    def test_add_subextension(self):
        assert FileUtils.add_subextension(
            os.path.join("path", "to", "file.mp4"),
            "extra",
        ) == os.path.join("path", "to", "file.extra.mp4")

    def test_add_subextension_without_extension(self):
        assert FileUtils.add_subextension("plainfile", "extra") == "plainfile.extra"

    def test_add_subextension_with_empty_string(self):
        assert FileUtils.add_subextension("", "extra") == ".extra"


class TestFilenameWithOriginalExtension:
    def test_filename_with_original_extension(self):
        assert FileUtils.filename_with_original_extension(
            os.path.join("path", "to", "file.extra.mp4"),
        ) == os.path.join("path", "to", "file.mp4")

    def test_filename_with_original_extension_with_one_ext(self):
        assert FileUtils.filename_with_original_extension(
            os.path.join("path", "to", "file.mp4"),
        ) == os.path.join("path", "to", "file.mp4")

    def test_filename_with_original_extension_without_extension(self):
        assert FileUtils.filename_with_original_extension("plainfile") == "plainfile"

    def test_filename_with_original_extension_with_empty_string(self):
        assert FileUtils.filename_with_original_extension("") == ""
