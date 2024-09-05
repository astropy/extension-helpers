import os
import subprocess as sp
import sys

import pytest

from ..conftest import HAS_COVERAGE, SUBPROCESS_COVERAGE, CoverageData

PACKAGE_DIR = os.path.dirname(__file__)


def run_cmd(cmd, args, path=None, raise_error=True):
    """
    Runs a shell command with the given argument list.  Changes directory to
    ``path`` if given, otherwise runs the command in the current directory.

    Returns a 3-tuple of (stdout, stderr, exit code)

    If ``raise_error=True`` raise an exception on non-zero exit codes.
    """

    if path is not None:
        # Transparently support py.path objects
        path = str(path)

    p = sp.Popen([cmd] + list(args), stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
    streams = tuple(s.decode("latin1").strip() for s in p.communicate())
    return_code = p.returncode

    if raise_error and return_code != 0:
        raise RuntimeError(
            f"The command `{cmd}` with args {list(args)!r} exited with code {return_code}.\n"
            f"Stdout:\n\n{streams[0]}\n\nStderr:\n\n{streams[1]}"
        )

    return streams + (return_code,)


def run_setup(setup_script, args):
    # This used to call setuptools.sandbox's run_setup, but due to issues with
    # this and Cython (which caused segmentation faults), we now use subprocess.

    setup_script = os.path.abspath(setup_script)

    path = os.path.dirname(setup_script)
    setup_script = os.path.basename(setup_script)

    if HAS_COVERAGE:
        # In this case, we run the command using the coverage command and we
        # then collect the coverage data into a SUBPROCESS_COVERAGE list which
        # is set up at the start of the testing process and is then combined
        # into a single .coverage file at the end of the testing process.

        p = sp.Popen(
            ["coverage", "run", setup_script] + list(args), cwd=path, stdout=sp.PIPE, stderr=sp.PIPE
        )
        stdout, stderr = p.communicate()

        cdata = CoverageData()
        if HAS_COVERAGE >= 5:
            # Support coverage<5 and >=5; see
            # https://github.com/astropy/extension-helpers/issues/24
            cdata.read()
        else:
            cdata.read_file(os.path.join(path, ".coverage"))

        SUBPROCESS_COVERAGE.append(cdata)

    else:
        # Otherwise we just run the tests with Python

        p = sp.Popen(
            [sys.executable, setup_script] + list(args), cwd=path, stdout=sp.PIPE, stderr=sp.PIPE
        )
        stdout, stderr = p.communicate()

    sys.stdout.write(stdout.decode("utf-8"))
    sys.stderr.write(stderr.decode("utf-8"))

    if p.returncode != 0:
        raise SystemExit(p.returncode)


TEST_PACKAGE_SETUP_PY = """\
#!/usr/bin/env python

from setuptools import setup

NAME = 'extension-helpers-test'
VERSION = {version!r}

setup(name=NAME, version=VERSION,
      packages=['_extension_helpers_test_'],
      zip_safe=False)
"""


def create_testpackage(tmp_path, version="0.1"):
    source = tmp_path / "testpkg"
    os.mkdir(source)

    with source.as_cwd():
        source.mkdir("_extension_helpers_test_")
        init = source.join("_extension_helpers_test_", "__init__.py")
        init.write(f"__version__ = {version!r}")
        setup_py = TEST_PACKAGE_SETUP_PY.format(version=version)
        source.join("setup.py").write(setup_py)

        # Make the new test package into a git repo
        run_cmd("git", ["init"])
        run_cmd("git", ["add", "--all"])
        run_cmd("git", ["commit", "-m", "test package"])

    return source


@pytest.fixture
def testpackage(tmp_path, version="0.1"):
    """
    This fixture creates a simplified package called _extension_helpers_test_
    used primarily for testing ah_boostrap, but without using the
    extension_helpers package directly and getting it confused with the
    extension_helpers package already under test.
    """

    return create_testpackage(tmp_path, version=version)


def cleanup_import(package_name):
    """Remove all references to package_name from sys.modules"""

    for k in list(sys.modules):
        if not isinstance(k, str):
            # Some things will actually do this =_=
            continue
        elif k.startswith("extension_helpers.tests"):
            # Don't delete imported test modules or else the tests will break,
            # badly
            continue
        if k == package_name or k.startswith(package_name + "."):
            del sys.modules[k]
