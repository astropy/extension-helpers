import os
import time

import pytest

from .._utils import (
    abi_to_versions,
    get_limited_api_option,
    import_file,
    write_if_different,
)


@pytest.mark.parametrize("path_type", ("str", "path"))
def test_import_file(tmp_path, path_type):
    filepath = tmp_path / "spam.py"
    if path_type == "str":
        filepath = str(filepath)
    with open(filepath, "w") as f:
        f.write("magic = 12345")
    module = import_file(filepath)
    assert module.magic == 12345


@pytest.mark.parametrize("path_type", ("str", "path"))
def test_write_if_different(tmp_path, path_type):
    filepath = tmp_path / "test.txt"
    if path_type == "str":
        filepath = str(filepath)
    write_if_different(filepath, b"abc")
    time1 = os.path.getmtime(filepath)
    time.sleep(0.01)
    write_if_different(filepath, b"abc")
    time2 = os.path.getmtime(filepath)
    assert time2 == time1
    time.sleep(0.01)
    write_if_different(filepath, b"abcd")
    time3 = os.path.getmtime(filepath)
    assert time3 > time1


class TestGetLimitedAPIOption:

    def test_nofiles(self, tmp_path):
        assert get_limited_api_option(tmp_path) is None

    def test_empty_setup_cfg(self, tmp_path):
        (tmp_path / "setup.cfg").write_text("")
        assert get_limited_api_option(tmp_path) is None

    def test_empty_pyproject_toml(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("")
        assert get_limited_api_option(tmp_path) is None

    def test_setup_cfg(self, tmp_path):

        (tmp_path / "setup.cfg").write_text("[bdist_wheel]\npy_limited_api=cp311")
        assert get_limited_api_option(tmp_path) == "cp311"

        # Make sure things still work even if an empty pyproject.toml file is present

        (tmp_path / "pyproject.toml").write_text("")
        assert get_limited_api_option(tmp_path) == "cp311"

        # And if the pyproject.toml has the right section but not the right option

        (tmp_path / "setup.cfg.toml").write_text("[tool.distutils.bdist_wheel]\nspam=1\n")
        assert get_limited_api_option(tmp_path) == "cp311"

    def test_pyproject(self, tmp_path):

        (tmp_path / "pyproject.toml").write_text(
            '[tool.distutils.bdist_wheel]\npy-limited-api="cp312"\n'
        )
        assert get_limited_api_option(tmp_path) == "cp312"

        # Make sure things still work even if an empty setup.cfg file is present

        (tmp_path / "setup.cfg.toml").write_text("\n")
        assert get_limited_api_option(tmp_path) == "cp312"

        # And if the setup.cfg has the right section but not the right option

        (tmp_path / "setup.cfg.toml").write_text("[bdist_wheel]\nspam=1\n")
        assert get_limited_api_option(tmp_path) == "cp312"


def test_abi_to_versions_invalid():
    assert abi_to_versions("spam") == (None, None)


def test_abi_to_versions_valid():
    assert abi_to_versions("cp39") == ((3, 9), "0x03090000")
    assert abi_to_versions("cp310") == ((3, 10), "0x030A0000")
    assert abi_to_versions("cp311") == ((3, 11), "0x030B0000")
    assert abi_to_versions("cp312") == ((3, 12), "0x030C0000")
    assert abi_to_versions("cp313") == ((3, 13), "0x030D0000")
