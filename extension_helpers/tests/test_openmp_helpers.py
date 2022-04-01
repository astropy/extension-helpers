
import os
import sys
import types
from copy import deepcopy
from importlib import machinery

import pytest
from setuptools import Extension

from .._openmp_helpers import _get_flag_value_from_var, add_openmp_flags_if_available, generate_openmp_enabled_py


@pytest.fixture
def openmp_expected(request):
    try:
        openmp_expected = request.config.getoption("--openmp-expected")
        if openmp_expected is not None:
            return openmp_expected.lower() == 'true'
    except ValueError:
        return None


def test_add_openmp_flags_if_available(openmp_expected):

    using_openmp = add_openmp_flags_if_available(Extension('test', []))

    # Make sure that on Travis (Linux) and AppVeyor OpenMP does get used (for
    # MacOS X usually it will not work but this will depend on the compiler).
    # Having this is useful because we'll find out if OpenMP no longer works
    # for any reason on platforms on which it does work at the time of writing.
    if openmp_expected is not None:
        assert openmp_expected is using_openmp


def test_generate_openmp_enabled_py(openmp_expected):

    # Test file generation
    generate_openmp_enabled_py('')
    assert os.path.isfile('openmp_enabled.py')

    # Load openmp_enabled file as a module to check the result
    loader = machinery.SourceFileLoader('openmp_enabled', 'openmp_enabled.py')
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)

    is_openmp_enabled = mod.is_openmp_enabled()

    # Test is_openmp_enabled()
    assert isinstance(is_openmp_enabled, bool)

    if openmp_expected is not None:
        assert openmp_expected is is_openmp_enabled


def test_get_flag_value_from_var():
    # define input
    var = 'EXTTESTFLAGS'
    flag = '-I'
    # non existing var (at least should not)
    assert _get_flag_value_from_var(flag, var) is None
    # setup env varN
    os.environ[var] = '-I/path/to/file1 -I/path/to/file2 -custom_option1 -custom_option2'
    # non existing flag
    assert _get_flag_value_from_var('-L', var) is None
    # existing flag
    assert _get_flag_value_from_var(flag, var) == ['/path/to/file1', '/path/to/file2']

