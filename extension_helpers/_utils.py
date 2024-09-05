# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os
import sys
from importlib import machinery as import_machinery
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

__all__ = ["write_if_different", "import_file"]


if sys.platform == "win32":
    import ctypes

    def _has_hidden_attribute(filepath):
        """
        Returns True if the given filepath has the hidden attribute on
        MS-Windows.  Based on a post here:
        http://stackoverflow.com/questions/284115/cross-platform-hidden-file-detection
        """
        if isinstance(filepath, bytes):
            filepath = filepath.decode(sys.getfilesystemencoding())
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
            assert attrs != -1
            result = bool(attrs & 2)
        except (AttributeError, AssertionError):
            result = False
        return result

else:

    def _has_hidden_attribute(filepath):
        return False


def is_path_hidden(filepath):
    """
    Determines if a given file or directory is hidden.

    Parameters
    ----------
    filepath : str
        The path to a file or directory

    Returns
    -------
    hidden : bool
        Returns `True` if the file is hidden
    """

    name = os.path.basename(os.path.abspath(filepath))
    if isinstance(name, bytes):
        is_dotted = name.startswith(b".")
    else:
        is_dotted = name.startswith(".")
    return is_dotted or _has_hidden_attribute(filepath)


def walk_skip_hidden(top, onerror=None, followlinks=False):
    """
    A wrapper for `os.walk` that skips hidden files and directories.

    This function does not have the parameter `topdown` from
    `os.walk`: the directories must always be recursed top-down when
    using this function.

    See also
    --------
    os.walk : For a description of the parameters
    """

    for root, dirs, files in os.walk(top, topdown=True, onerror=onerror, followlinks=followlinks):
        # These lists must be updated in-place so os.walk will skip
        # hidden directories
        dirs[:] = [d for d in dirs if not is_path_hidden(d)]
        files[:] = [f for f in files if not is_path_hidden(f)]
        yield root, dirs, files


def write_if_different(filename, data):
    """
    Write ``data`` to ``filename``, if the content of the file is different.

    This can be useful if e.g. generating ``.c`` or ``.h`` files, to make sure
    that Python does not re-build unchanged files.

    Parameters
    ----------
    filename : str or `pathlib.Path`
        The file name to be written to.
    data : bytes
        The data to be written to ``filename``.
    """

    filepath = Path(filename)

    assert isinstance(data, bytes)

    if filepath.exists():
        original_data = filepath.read_bytes()
    else:
        original_data = None

    if original_data != data:
        filepath.write_bytes(data)


def import_file(filename, name=None):
    """
    Imports a module from a single file without importing the package that
    the file is in.

    This is useful for cases where a file needs to be imported from
    ``setup_package.py`` files without importing the parent package. The
    returned module will have the optional ``name`` if given, or else a name
    generated from the filename.
    """
    # Specifying a traditional dot-separated fully qualified name here
    # results in a number of "Parent module '...' not found while
    # handling absolute import" warnings.  Using the same name, the
    # namespaces of the modules get merged together.  So, this
    # generates an underscore-separated name which is more likely to
    # be unique, and it doesn't really matter because the name isn't
    # used directly here anyway.

    filepath = Path(filename)

    if name is None:
        name = "_".join(filepath.resolve().with_suffix("").parts[1:])

    if not filepath.exists():
        raise ImportError(f"Could not import file {filepath}")

    loader = import_machinery.SourceFileLoader(name, str(filepath))
    spec = spec_from_file_location(name, str(filepath))
    mod = module_from_spec(spec)
    loader.exec_module(mod)

    return mod
