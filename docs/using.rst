Using extension-helpers
=======================

To use extension-helpers in your package, you will need to make sure your
package uses a ``pyproject.toml`` file as described in `PEP 518
<https://www.python.org/dev/peps/pep-0518/>`_.

You can then add extension-helpers to the build-time dependencies in your
``pyproject.toml`` file::

    [build-system]
    requires = ["setuptools", "wheel", "extension-helpers"]

If you have Cython extensions, you will need to make sure ``cython`` is included
in the above list too.

The main functionality in extension-helpers is the
:func:`~extension_helpers.get_extensions` function which can be
used to collect package extensions. Defining functions is then done in two ways:

* For simple Cython extensions, :func:`~extension_helpers.get_extensions`
  will automatically generate extension modules with no further work.

* For other extensions, you can create ``setup_package.py`` files anywhere
  in your package, and these files can then include a ``get_extensions``
  function that returns a list of :class:`distutils.core.Extension` objects.

In the second case, the idea is that for large packages, extensions can be defined
in the relevant sub-packages rather than having to all be listed in the main
``setup.py`` file.

To use this, you should modify your ``setup.py`` file to use
:func:`~extension_helpers.get_extensions`  as follows::

    from extension_helpers import get_extensions
    ...
    setup(..., ext_modules=get_extensions())

Note that if you use this, extension-helpers will also we create a
``packagename.compiler_version`` submodule that contain information about the
compilers used.

Python limited API
------------------

Your package may opt in to the :pep:`384` Python Limited API so that a single
binary wheel works with many different versions of Python on the same platform.
To opt in to the Python Limited API, add the following standard setuptools
option to your project's ``setup.cfg`` file::

    [bdist_wheel]
    py_limited_api = cp36

Here, ``36`` denotes API compatibility with Python >= 3.6. Replace with the
lowest major and minor version number that you wish to support.

The ``get_extensions()`` functions will automatically detect this option and
add the necessary compiler flags to build your extension modules.
