import sys
from configparser import ConfigParser

from ._openmp_helpers import add_openmp_flags_if_available  # noqa: F401
from ._setup_helpers import get_compiler, get_extensions, pkg_config  # noqa: F401
from ._utils import import_file, write_if_different  # noqa: F401
from .version import version as __version__  # noqa: F401


def _finalize_distribution_hook(distribution):
    """
    Entry point for setuptools which allows extension-helpers to be enabled
    from setup.cfg without the need for setup.py.
    """
    import os
    from pathlib import Path

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    found_config = False

    config_files = distribution.find_config_files()
    if len(config_files) > 0:
        cfg = ConfigParser()
        cfg.read(config_files[0])
        if cfg.has_option("extension-helpers", "use_extension_helpers"):
            found_config = True
            if cfg.get("extension-helpers", "use_extension_helpers").lower() == "true":
                distribution.ext_modules = get_extensions()

    pyproject = Path(distribution.src_root or os.curdir, "pyproject.toml")
    if pyproject.exists() and not found_config:
        with pyproject.open("rb") as f:
            pyproject_cfg = tomllib.load(f)
            if (
                "tool" in pyproject_cfg
                and "extension-helpers" in pyproject_cfg["tool"]
                and "use_extension_helpers" in pyproject_cfg["tool"]["extension-helpers"]
                and pyproject_cfg["tool"]["extension-helpers"]["use_extension_helpers"]
            ):
                distribution.ext_modules = get_extensions()
