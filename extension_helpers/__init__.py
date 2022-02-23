from configparser import ConfigParser

from ._openmp_helpers import add_openmp_flags_if_available
from ._setup_helpers import get_compiler, get_extensions, pkg_config
from ._utils import import_file, write_if_different
from .version import version as __version__


def _finalize_distribution_hook(distribution):
    """
    Entry point for setuptools which allows extension-helpers to be enabled
    from setup.cfg without the need for setup.py.
    """
    config_files = distribution.find_config_files()
    if len(config_files) == 0:
        return
    cfg = ConfigParser()
    cfg.read(config_files[0])
    if (cfg.has_option("extension-helpers", "use_extension_helpers") and
            cfg.get("extension-helpers", "use_extension_helpers").lower() == 'true'):
        distribution.ext_modules = get_extensions()
