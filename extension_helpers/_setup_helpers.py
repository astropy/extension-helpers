# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module contains a number of utilities for use during
setup/build/packaging that are useful to astropy as a whole.
"""

import logging
import os
import shutil
import subprocess
import sys
from collections import defaultdict

from setuptools import Extension, find_packages
from setuptools.command.build_ext import new_compiler

from ._utils import (
    abi_to_versions,
    get_limited_api_option,
    import_file,
    walk_skip_hidden,
)

__all__ = ["get_compiler", "get_extensions", "pkg_config"]

log = logging.getLogger(__name__)


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


def get_extensions(srcdir="."):
    """
    Collect all extensions from Cython files and ``setup_package.py`` files.

    If numpy is importable, the numpy include path will be added to all Cython
    extensions which are automatically generated.

    This function obtains that information by iterating through all
    packages in ``srcdir`` and locating a ``setup_package.py`` module.
    This module can contain the ``get_extensions()`` function which returns
    a list of :class:`setuptools.Extension` objects.

    """
    ext_modules = []
    packages = []
    package_dir = {}

    # Use the find_packages tool to locate all packages and modules
    packages = find_packages(srcdir)

    # Update package_dir if the package lies in a subdirectory
    if srcdir != ".":
        package_dir[""] = srcdir

    for setuppkg in iter_setup_packages(srcdir, packages):
        # get_extensions must include any Cython extensions by their .pyx
        # filename.
        if hasattr(setuppkg, "get_extensions"):
            ext_modules.extend(setuppkg.get_extensions())

    # Locate any .pyx files not already specified, and add their extensions in.
    # The default include dirs include numpy to facilitate numerical work.
    includes = []
    try:
        import numpy

        includes = [numpy.get_include()]
    except ImportError:
        pass

    ext_modules.extend(get_cython_extensions(srcdir, packages, ext_modules, includes))

    # Now remove extensions that have the special name 'skip_cython', as they
    # exist Only to indicate that the cython extensions shouldn't be built
    for i, ext in reversed(list(enumerate(ext_modules))):
        if ext.name == "skip_cython":
            del ext_modules[i]

    # On Microsoft compilers, we need to pass the '/MANIFEST'
    # commandline argument.  This was the default on MSVC 9.0, but is
    # now required on MSVC 10.0, but it doesn't seem to hurt to add
    # it unconditionally.
    if get_compiler() == "msvc":
        for ext in ext_modules:
            ext.extra_link_args.append("/MANIFEST")

    if len(ext_modules) > 0:
        main_package_dir = min(packages, key=len)
        src_path = os.path.join(os.path.dirname(__file__), "src")
        shutil.copyfile(
            os.path.join(src_path, "compiler.c"),
            os.path.join(srcdir, main_package_dir, "_compiler.c"),
        )
        ext = Extension(
            main_package_dir + ".compiler_version", [os.path.join(main_package_dir, "_compiler.c")]
        )
        ext_modules.append(ext)

    # Since https://github.com/astropy/extension-helpers/pull/67,
    # extensions that used absolute paths in source names stopped working.
    # Absolute paths in source paths are undesirable but we need to
    # preserve backward-compatibility until we bump the major release,
    # so we check for the case of absolute paths and emit a deprecation
    # warning for now.
    for extension in ext_modules:
        sources = []
        fixed = []
        for source in extension.sources:
            if os.path.isabs(source):
                try:
                    source = os.path.relpath(source)
                except ValueError:
                    # In some cases it's impossible to use a relative path, for
                    # instance if the source files are on a different drive. In
                    # this case there's not much we can do so we just proceed.
                    pass
                fixed.append(source)
            sources.append(source)
        if fixed:
            log.warning(
                "Extension {} contains source files "
                "({}) that are specified using an absolute "
                "path, which will not be supported in future.".format(
                    extension.name, ", ".join(fixed)
                )
            )

        extension.sources = sources

    abi = get_limited_api_option(srcdir=srcdir)
    if abi:
        version_info, version_hex = abi_to_versions(abi)

        if version_info is None:
            raise ValueError(f"Unrecognized abi version for limited API: {abi}")

        log.info(
            f"Targeting PEP 384 limited API supporting Python >= {version_info[0], version_info[1]}"
        )

        for ext in ext_modules:
            ext.py_limited_api = True
            ext.define_macros.append(("Py_LIMITED_API", version_hex))

    return ext_modules


def iter_setup_packages(srcdir, packages):
    """A generator that finds and imports all of the ``setup_package.py``
    modules in the source packages.

    Returns
    -------
    modgen : generator
        A generator that yields (modname, mod), where `mod` is the module and
        `modname` is the module name for the ``setup_package.py`` modules.

    """

    for packagename in packages:
        package_parts = packagename.split(".")
        package_path = os.path.join(srcdir, *package_parts)
        setup_package = os.path.join(package_path, "setup_package.py")

        if os.path.isfile(setup_package):
            module = import_file(setup_package, name=packagename + ".setup_package")
            yield module


def iter_pyx_files(package_dir, package_name):
    """
    A generator that yields Cython source files (ending in '.pyx') in the
    source packages.

    Returns
    -------
    pyxgen : generator
        A generator that yields (extmod, fullfn) where `extmod` is the
        full name of the module that the .pyx file would live in based
        on the source directory structure, and `fullfn` is the path to
        the .pyx file.
    """
    for dirpath, _dirnames, filenames in walk_skip_hidden(package_dir):
        for fn in filenames:
            if fn.endswith(".pyx"):
                fullfn = os.path.join(dirpath, fn)
                # Package must match file name
                extmod = ".".join([package_name, fn[:-4]])
                yield (extmod, fullfn)

        break  # Don't recurse into subdirectories


def get_cython_extensions(srcdir, packages, prevextensions=tuple(), extincludedirs=None):
    """
    Looks for Cython files and generates Extensions if needed.

    Parameters
    ----------
    srcdir : str
        Path to the root of the source directory to search.
    prevextensions : list
        The extensions that are already defined, as a list of of
        `~setuptools.Extension` objects.  Any .pyx files already here will
        be ignored.
    extincludedirs : list or None
        Directories to include as the `include_dirs` argument to the generated
        `~setuptools.Extension` objects, as a list of strings.

    Returns
    -------
    exts : list
        The new extensions that are needed to compile all .pyx files (does not
        include any already in `prevextensions`).
    """

    # Vanilla setuptools and old versions of distribute include Cython files
    # as .c files in the sources, not .pyx, so we cannot simply look for
    # existing .pyx sources in the previous sources, but we should also check
    # for .c files with the same remaining filename. So we look for .pyx and
    # .c files, and we strip the extension.
    prevsourcepaths = []
    ext_modules = []

    for ext in prevextensions:
        for s in ext.sources:
            if s.endswith((".pyx", ".c", ".cpp")):
                sourcepath = os.path.realpath(os.path.splitext(s)[0])
                prevsourcepaths.append(sourcepath)

    for package_name in packages:
        package_parts = package_name.split(".")
        package_path = os.path.join(srcdir, *package_parts)

        for extmod, pyxfn in iter_pyx_files(package_path, package_name):
            sourcepath = os.path.realpath(os.path.splitext(pyxfn)[0])
            if sourcepath not in prevsourcepaths:
                ext_modules.append(Extension(extmod, [pyxfn], include_dirs=extincludedirs))

    return ext_modules


def pkg_config(packages, default_libraries, executable="pkg-config"):
    """
    Uses pkg-config to update a set of setuptools Extension arguments
    to include the flags necessary to link against the given packages.

    If the pkg-config lookup fails, default_libraries is applied to
    libraries.

    Parameters
    ----------
    packages : list
        The pkg-config packages to look up, as a list of strings.

    default_libraries : list
        The library names to use if the pkg-config lookup fails, a list of
        strings.

    Returns
    -------
    config : dict
        A dictionary containing keyword arguments to
        :class:`~setuptools.Extension`.  These entries include:

        - ``include_dirs``: A list of include directories
        - ``library_dirs``: A list of library directories
        - ``libraries``: A list of libraries
        - ``define_macros``: A list of macro defines
        - ``undef_macros``: A list of macros to undefine
        - ``extra_compile_args``: A list of extra arguments to pass to
          the compiler
    """

    flag_map = {
        "-I": "include_dirs",
        "-L": "library_dirs",
        "-l": "libraries",
        "-D": "define_macros",
        "-U": "undef_macros",
    }
    command = f"{executable} --libs --cflags {' '.join(packages)}"

    result = defaultdict(list)

    try:
        pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = pipe.communicate()[0].strip()
    except subprocess.CalledProcessError as e:
        lines = [
            (f"{executable} failed. This may cause the build to fail below."),
            f"  command: {e.cmd}",
            f"  returncode: {e.returncode}",
            f"  output: {e.output}",
        ]
        log.warning("\n".join(lines))
        result["libraries"].extend(default_libraries)
    else:
        if pipe.returncode != 0:
            lines = [
                f"pkg-config could not lookup up package(s) {', '.join(packages)}.",
                "This may cause the build to fail below.",
            ]
            log.warning("\n".join(lines))
            result["libraries"].extend(default_libraries)
        else:
            for token in output.split():
                # It's not clear what encoding the output of
                # pkg-config will come to us in.  It will probably be
                # some combination of pure ASCII (for the compiler
                # flags) and the filesystem encoding (for any argument
                # that includes directories or filenames), but this is
                # just conjecture, as the pkg-config documentation
                # doesn't seem to address it.
                arg = token[:2].decode("ascii")
                value = token[2:].decode(sys.getfilesystemencoding())
                if arg in flag_map:
                    if arg == "-D":
                        value = tuple(value.split("=", 1))
                    result[flag_map[arg]].append(value)
                else:
                    result["extra_compile_args"].append(value)

    return result
