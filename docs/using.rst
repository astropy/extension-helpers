Using extension-helpers
=======================

To use extension-helpers in your package, you will need to make sure your
package uses a ``pyproject.toml`` file as described in `PEP 518
<https://www.python.org/dev/peps/pep-0518/>`_.

You can then add extension-helpers to the build-time dependencies in your
``pyproject.toml`` file::

    [build-system]
    requires = ["setuptools",
                "wheel",
                "extension-helpers==1.*"]

If you have Cython extensions, you will need to make sure ``cython`` is included
in the above list too.

.. note:: It is highly recommended to pin the version of extension-helpers
          to a major version, such as ``1.*``, since extension-helpers uses
          `semantic versioning <https://semver.org>`_
          and there will therefore likely be breaking changes when the major version is bumped.
          If you do not specify any pinning, then old versions of your package that are already
          on PyPI may no longer be installable on source without disabling the build isolation
          and installing build dependencies manually.

The main functionality in extension-helpers is the
:func:`~extension_helpers.get_extensions` function which can be
used to collect package extensions. Defining functions is then done in two ways:

* For simple Cython extensions, :func:`~extension_helpers.get_extensions`
  will automatically generate extension modules with no further work.

* For other extensions, you can create ``setup_package.py`` files anywhere
  in your package, and these files can then include a ``get_extensions``
  function that returns a list of :class:`setuptools.Extension` objects.

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

It is also possible to enable extension-helpers in ``setup.cfg`` instead of
``setup.py`` by adding the following configuration to the ``setup.cfg`` file::

    [extension-helpers]
    use_extension_helpers = true

Moreover, one can also enable extension-helpers in ``pyproject.toml`` by adding
the following configuration to the ``pyproject.toml`` file::

    [tool.extension-helpers]
    use_extension_helpers = true

.. note::
  For backwards compatibility, the setting of ``use_extension_helpers`` in
  ``setup.cfg`` will override any setting of it in ``pyproject.toml``.

Python limited API
------------------

Your package may opt in to the :pep:`384` Python Limited API so that a single
binary wheel works with many different versions of Python on the same platform.
For this to work, any C extensions you write needs to make use only of
`certain C functions <https://docs.python.org/3/c-api/stable.html#limited-api-list>`__.

To opt in to the Python Limited API, add the following standard setuptools
option to your project's ``setup.cfg`` file::

    [bdist_wheel]
    py_limited_api = cp311

Here, ``311`` denotes API compatibility with Python >= 3.11. Replace with the
lowest major and minor version number that you wish to support.

You can also set this option in ``pyproject.toml``, using::

    [tool.distutils.bdist_wheel]
    py-limited-api = "cp312"

although note that this option is not formally documented/supported by the Python
packaging infrastructure and may change in future.

Alternatively, if you use setuptools 65.4 or later, you can dynamically opt in
to limited API builds by setting the ``EXTENSION_HELPERS_PY_LIMITED_API``
environment variable, e.g.::

    EXTENSION_HELPERS_PY_LIMITED_API='cp311' python -m build

If you define ``py_limited_api`` in ``setup.cfg``, you can use
``EXTENSION_HELPERS_PY_LIMITED_API`` to opt **out** of the limited API builds
by setting ``EXTENSION_HELPERS_PY_LIMITED_API`` to an empty string. There is however
no way to opt out if you use ``py-limited-api`` in ``pyproject.toml``.

The ``get_extensions()`` functions will automatically detect these options and
add the necessary compiler flags to build your extension modules.
