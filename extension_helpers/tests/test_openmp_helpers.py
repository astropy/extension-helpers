import os
import sys
import types
from copy import deepcopy
from importlib import machinery
from distutils.core import Extension

import pytest

from .._openmp_helpers import add_openmp_flags_if_available, generate_openmp_enabled_py


@pytest.fixture
def openmp_expected(request):
    openmp_expected = request.config.getoption("--openmp-expected")
    if openmp_expected is not None:
        return openmp_expected.lower() == 'true'


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
