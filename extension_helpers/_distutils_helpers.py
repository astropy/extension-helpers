"""
This module contains various utilities for introspecting the distutils
module and the setup process.

Some of these utilities require the
`extension_helpers.setup_helpers.register_commands` function to be called first,
as it will affect introspection of setuptools command-line arguments.  Other
utilities in this module do not have that restriction.
"""

import os
import sys

from setuptools.command.build_ext import new_compiler
from setuptools.dist import Distribution
from setuptools.errors import DistutilsError

from ._utils import silence

__all__ = ['get_compiler']


def get_dummy_distribution():
    """
    Returns a distutils Distribution object used to instrument the setup
    environment before calling the actual setup() function.
    """

    # Pre-parse the Distutils command-line options and config files to if
    # the option is set.
    dist = Distribution({'script_name': os.path.basename(sys.argv[0]),
                         'script_args': sys.argv[1:]})

    with silence():
        try:
            dist.parse_config_files()
            dist.parse_command_line()
        except (DistutilsError, AttributeError, SystemExit):
            # Let distutils handle DistutilsErrors itself AttributeErrors can
            # get raise for ./setup.py --help SystemExit can be raised if a
            # display option was used, for example
            pass

    return dist


def get_compiler():
    """
    Determines the compiler that will be used to build extension modules.

    Returns
    -------
    compiler : str
        The compiler option specified for the build, build_ext, or build_clib
        command; or the default compiler for the platform if none was
        specified.

    """
    return new_compiler().compiler_type
