from .._distutils_helpers import get_compiler

POSSIBLE_COMPILERS = ['unix', 'msvc', 'bcpp', 'cygwin', 'mingw32']


def test_get_compiler():
    assert get_compiler() in POSSIBLE_COMPILERS
