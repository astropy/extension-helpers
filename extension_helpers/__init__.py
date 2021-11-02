from ._openmp_helpers import add_openmp_flags_if_available
from ._setup_helpers import get_compiler, get_extensions, pkg_config
from ._utils import import_file, write_if_different
from .version import version as __version__

from configparser import ConfigParser


def _finalize_distribution_hook(distribution):
    """
    Something something setuptools entrypoint
    """
    config_files = distribution.find_config_files()
    cfg = ConfigParser()
    cfg.read(config_files[0])
    if cfg.has_option("extension_helpers", "use_extension_helpers") and cfg.get("extension_helpers", "use_extension_helpers"):
        extension_helpers_cfg = cfg["extension_helpers"]
        distribution.ext_modules = get_extensions(distribution=distribution)
