import os
import time

import pytest

from .._utils import import_file, write_if_different


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
