import os
import time

from .._utils import import_file, write_if_different


def test_import_file(tmpdir):
    filename = str(tmpdir / "spam.py")
    with open(filename, "w") as f:
        f.write("magic = 12345")
    module = import_file(filename)
    assert module.magic == 12345


def test_write_if_different(tmpdir):
    filename = str(tmpdir / "test.txt")
    write_if_different(filename, b"abc")
    time1 = os.path.getmtime(filename)
    time.sleep(0.01)
    write_if_different(filename, b"abc")
    time2 = os.path.getmtime(filename)
    assert time2 == time1
    time.sleep(0.01)
    write_if_different(filename, b"abcd")
    time3 = os.path.getmtime(filename)
    assert time3 > time1
