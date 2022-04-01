# This module defines functions that can be used to check whether OpenMP is
# available and if so what flags to use. To use this, import the
# add_openmp_flags_if_available function in a setup_package.py file where you
# are defining your extensions:
#
#     from extension_helpers.openmp_helpers import add_openmp_flags_if_available
#
# then call it with a single extension as the only argument:
#
#     add_openmp_flags_if_available(extension)
#
# this will add the OpenMP flags if available.

import os
import sys
import glob
import time
import logging
import datetime
import tempfile
import subprocess
import textwrap

from setuptools.command.build_ext import customize_compiler, get_config_var, new_compiler

from ._setup_helpers import check_apple_clang, get_compiler

__all__ = ['add_openmp_flags_if_available']

try:
    # Check if this has already been instantiated, only set the default once.
    _EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_
except NameError:
    import builtins

    # It hasn't, so do so.
    builtins._EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_ = False

log = logging.getLogger(__name__)

CCODE = """
#include <omp.h>
#include <stdio.h>
int main(void) {
  #pragma omp parallel
  printf("nthreads=%d\\n", omp_get_num_threads());
  return 0;
}
"""


def _get_flag_value_from_var(flag, var, delim=' '):
    """
    Extract flags from an environment variable.

    Parameters
    ----------
    flag : str
        The flag to extract, for example '-I' or '-L'
    var : str
        The environment variable to extract the flag from, e.g. CFLAGS or LDFLAGS.
    delim : str, optional
        The delimiter separating flags inside the environment variable
    
    Returns
    -------
    extracted_flags : None|list
        List of flags starting with flag extracted from var  environment
        variable.

    Examples
    --------
    Let's assume the LDFLAGS is set to '-L/usr/local/include -customflag'. This
    function will then return the following:

        >>> _get_flag_value_from_var('-L', 'LDFLAGS')
        '/usr/local/include'

    Notes
    -----
    Environment variables are first checked in ``os.environ[var]``, then in
    ``distutils.sysconfig.get_config_var(var)``.

    This function is not supported on Windows.
    """

    if sys.platform.startswith('win'):
        return None

    # Simple input validation
    if not var or not flag:
        return None
    flag_length = len(flag)
    if not flag_length:
        return None

    # Look for var in os.eviron then in get_config_var
    if var in os.environ:
        flags = os.environ[var]
    else:
        try:
            flags = get_config_var(var)
        except KeyError:
            return None

    # Extract flag from {var:value}
    extracted_flags = []
    if flags:
        for item in flags.split(delim):
            if item.startswith(flag):
                extracted_flags.append(item[flag_length:])
    if len(extracted_flags) > 0:
        return extracted_flags
    else:
        return None


def get_openmp_flags():
    """
    Utility for returning compiler and linker flags possibly needed for
    OpenMP support.

    Returns
    -------
    result : `{'compiler_flags':<flags>, 'linker_flags':<flags>}`

    Notes
    -----
    The flags returned are not tested for validity, use
    `check_openmp_support(openmp_flags=get_openmp_flags())` to do so.
    """

    compile_flags = []
    link_flags = []

    if get_compiler() == 'msvc':
        compile_flags.append('-openmp')
    else:

        include_path = _get_flag_value_from_var('-I', 'CFLAGS')
        if include_path:
            for _ in include_path:
                compile_flags.append('-I' + _)

        include_path = _get_flag_value_from_var('-I', 'CXXFLAGS')
        if include_path:
            for _ in include_path:
                compile_flags.append('-I' + _)

        lib_path = _get_flag_value_from_var('-L', 'LDFLAGS')
        if lib_path:
            for _ in include_path:
                link_flags.append('-L' + _)
                link_flags.append('-Wl,-rpath,' + _)

        if not check_apple_clang():
            compile_flags.append('-fopenmp')
            link_flags.append('-fopenmp')
        else:
            msg = textwrap.dedent(
                """\
                You are using Apple Clang compiler.

                Your system should be prepared:
                1. You should have specfically installed OpenMP,
                   for instance by running `brew install libomp`.
                2. OpenMP source and library should be findable by the compiler.

                By default, OpenMP source and library will be looked in
                `/usr/local/opt/libomp/include` and `/usr/local/opt/libomp/lib`
                respectively.

                To use specific OpenMP source and library paths, you can setup
                the following environment variables `CFLAGS` (or `CXXFLAGS`)
                and `LDFLAGS` before any compilation/installation, e.g.
                ```
                export CFLAGS="-I/usr/local/opt/libomp/include"
                export LDFLAGS="-L/usr/local/opt/libomp/lib"
                ```
                """
            )
            log.warn(msg)
            compile_flags.append('-Xpreprocessor -fopenmp')
            if not 'CFLAGS' in os.environ and not 'CXXFLAGS' in os.environ and \
                os.path.isdir('/usr/local/opt/libomp/include'):
                compile_flags.append('-I/usr/local/opt/libomp/include')
            link_flags.append('-lomp')
            if not 'LDFLAGS' in os.environ and \
                os.path.isdir('/usr/local/opt/libomp/lib'):
                link_flags.append('-L/usr/local/opt/libomp/lib')

    return {'compiler_flags': compile_flags, 'linker_flags': link_flags}


def check_openmp_support(openmp_flags=None):
    """
    Check whether OpenMP test code can be compiled and run.

    Parameters
    ----------
    openmp_flags : dict, optional
        This should be a dictionary with keys ``compiler_flags`` and
        ``linker_flags`` giving the compiliation and linking flags respectively.
        These are passed as `extra_postargs` to `compile()` and
        `link_executable()` respectively. If this is not set, the flags will
        be automatically determined using environment variables.

    Returns
    -------
    result : bool
        `True` if the test passed, `False` otherwise.
    """

    ccompiler = new_compiler()
    customize_compiler(ccompiler)

    if not openmp_flags:
        # customize_compiler() extracts info from os.environ. If certain keys
        # exist it uses these plus those from sysconfig.get_config_vars().
        # If the key is missing in os.environ it is not extracted from
        # sysconfig.get_config_var(). E.g. 'LDFLAGS' get left out, preventing
        # clang from finding libomp.dylib because -L<path> is not passed to
        # linker. Call get_openmp_flags() to get flags missed by
        # customize_compiler().
        openmp_flags = get_openmp_flags()

    compile_flags = openmp_flags.get('compiler_flags')
    link_flags = openmp_flags.get('linker_flags')

    with tempfile.TemporaryDirectory() as tmp_dir:
        start_dir = os.path.abspath('.')

        try:
            os.chdir(tmp_dir)

            # Write test program
            with open('test_openmp.c', 'w') as f:
                f.write(CCODE)

            os.mkdir('objects')

            # Compile, test program
            ccompiler.compile(['test_openmp.c'], output_dir='objects',
                              extra_preargs=compile_flags)

            # Link test program
            objects = glob.glob(os.path.join('objects', '*' + ccompiler.obj_extension))
            ccompiler.link_executable(objects, 'test_openmp',
                                      extra_preargs=link_flags)

            # Run test program
            output = subprocess.check_output('./test_openmp')
            output = output.decode(sys.stdout.encoding or 'utf-8').splitlines()

            if 'nthreads=' in output[0]:
                nthreads = int(output[0].strip().split('=')[1])
                if len(output) == nthreads:
                    is_openmp_supported = True
                else:
                    log.warn("Unexpected number of lines from output of test OpenMP "
                             "program (output was {0})".format(output))
                    is_openmp_supported = False
            else:
                log.warn("Unexpected output from test OpenMP "
                         "program (output was {0})".format(output))
                is_openmp_supported = False
        except Exception:
            is_openmp_supported = False

        finally:
            os.chdir(start_dir)

    return is_openmp_supported


def is_openmp_supported():
    """
    Determine whether the build compiler has OpenMP support.
    """
    log_threshold = log.level
    log.setLevel('CRITICAL')
    ret = check_openmp_support()
    log.setLevel(log_threshold)
    return ret


def add_openmp_flags_if_available(extension):
    """
    Add OpenMP compilation flags, if supported (if not a warning will be
    printed to the console and no flags will be added.)

    Returns `True` if the flags were added, `False` otherwise.
    """

    if _EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_:
        log.info("OpenMP support has been explicitly disabled.")
        return False

    openmp_flags = get_openmp_flags()
    using_openmp = check_openmp_support(openmp_flags=openmp_flags)

    if using_openmp:
        compile_flags = openmp_flags.get('compiler_flags')
        link_flags = openmp_flags.get('linker_flags')
        log.info("Compiling Cython/C/C++ extension with OpenMP support")
        extension.extra_compile_args.extend(compile_flags)
        extension.extra_link_args.extend(link_flags)
    else:
        log.warn("Cannot compile Cython/C/C++ extension with OpenMP, reverting "
                 "to non-parallel code")

    return using_openmp


_IS_OPENMP_ENABLED_SRC = """
# Autogenerated by {packagename}'s setup.py on {timestamp!s}

def is_openmp_enabled():
    \"\"\"
    Determine whether this package was built with OpenMP support.
    \"\"\"
    return {return_bool}
"""[1:]


def generate_openmp_enabled_py(packagename, srcdir='.', disable_openmp=None):
    """
    Generate ``package.openmp_enabled.is_openmp_enabled``, which can then be used
    to determine, post build, whether the package was built with or without
    OpenMP support.
    """

    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
    timestamp = datetime.datetime.utcfromtimestamp(epoch)

    if disable_openmp is not None:
        import builtins
        builtins._EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_ = disable_openmp
    if _EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_:
        log.info("OpenMP support has been explicitly disabled.")
    openmp_support = False if _EXTENSION_HELPERS_DISABLE_OPENMP_SETUP_ else is_openmp_supported()

    src = _IS_OPENMP_ENABLED_SRC.format(packagename=packagename,
                                        timestamp=timestamp,
                                        return_bool=openmp_support)

    package_srcdir = os.path.join(srcdir, *packagename.split('.'))
    is_openmp_enabled_py = os.path.join(package_srcdir, 'openmp_enabled.py')
    with open(is_openmp_enabled_py, 'w') as f:
        f.write(src)
