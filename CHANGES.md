## v1.3.0 - 2025-05-27

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

* Automatically set compiler flags to target PEP 384 Python limited API by @lpsinger in https://github.com/astropy/extension-helpers/pull/26

#### Other Changes

* Bump the actions group across 1 directory with 2 updates by @dependabot in https://github.com/astropy/extension-helpers/pull/92
* MNT: Replace ubuntu-20.04 with ubuntu-22.04 by @pllim in https://github.com/astropy/extension-helpers/pull/100
* Bump the actions group across 1 directory with 2 updates by @dependabot in https://github.com/astropy/extension-helpers/pull/99
* Bump stefanzweifel/git-auto-commit-action from 5.1.0 to 5.2.0 in /.github/workflows in the actions group by @dependabot in https://github.com/astropy/extension-helpers/pull/104
* Bump minimum version of Python to 3.10 and update versions by @astrofrog in https://github.com/astropy/extension-helpers/pull/106

**Full Changelog**: https://github.com/astropy/extension-helpers/compare/v1.2.0...v1.3.0

## v1.2.0 - 2024-10-16

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

* Support pathlib.Path in write_if_different and import_file by @astrofrog in https://github.com/astropy/extension-helpers/pull/84

#### Bug Fixes

* TST: fix pyproject-only test (ensure build-time dependencies are installed) by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/80

#### Other Changes

* TST: drop legacy pytest fixture tmpdir, use tmp_path instead by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/81
* Test downstream with Python 3.12 by @astrofrog in https://github.com/astropy/extension-helpers/pull/86
* MNT: Use hash for Action workflow versions and update if needed by @pllim in https://github.com/astropy/extension-helpers/pull/88
* Bump actions/checkout from 4.2.0 to 4.2.1 in /.github/workflows in the actions group by @dependabot in https://github.com/astropy/extension-helpers/pull/89

**Full Changelog**: https://github.com/astropy/extension-helpers/compare/v1.1.1...v1.2.0

## v1.1.1 - 2023-12-07

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

* get_extensions: use shutil.copyfile to avoid PermissionError by @doronbehar in https://github.com/astropy/extension-helpers/pull/59
* Fix bug that caused extension-helpers to not work correctly if pyproject was the only configuration file present by @astrofrog in https://github.com/astropy/extension-helpers/pull/66

#### Other Changes

* Replace all instances of distutils in docs with setuptools by @lpsinger in https://github.com/astropy/extension-helpers/pull/65
* Fix typos by @lpsinger in https://github.com/astropy/extension-helpers/pull/64
* MNT: handle deprecation warnings seen in tests by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/67
* Add note about pinning extension-helpers by @astrofrog in https://github.com/astropy/extension-helpers/pull/72
* DEP: drop dependency on tomli on Python 3.11 and newer by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/73
* TST: treat warnings as errors by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/74
* MNT: find and replace log.warn -> log.warning (the warn method is deprecated) by @neutrinoceros in https://github.com/astropy/extension-helpers/pull/75
* Infrastructure updates by @astrofrog in https://github.com/astropy/extension-helpers/pull/68
* Bump actions/checkout from 2 to 4 by @dependabot in https://github.com/astropy/extension-helpers/pull/77
* Bump stefanzweifel/git-auto-commit-action from 4 to 5 by @dependabot in https://github.com/astropy/extension-helpers/pull/76
* Add back support for absolute source paths but deprecate it by @astrofrog in https://github.com/astropy/extension-helpers/pull/70

### New Contributors

* @doronbehar made their first contribution in https://github.com/astropy/extension-helpers/pull/59
* @neutrinoceros made their first contribution in https://github.com/astropy/extension-helpers/pull/67
* @dependabot made their first contribution in https://github.com/astropy/extension-helpers/pull/77

**Full Changelog**: https://github.com/astropy/extension-helpers/compare/v1.1.0...v1.1.1

## v1.1.0 - 2023-07-24

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

- Support enabling via `pyproject.toml` by @WilliamJamieson in https://github.com/astropy/extension-helpers/pull/48

#### Bug Fixes

- OpenMP functions should detect the Intel oneAPI compiler by @lpsinger in https://github.com/astropy/extension-helpers/pull/44

#### Infrastructure

- Skip hypothesis tests in downstream testing by @astrofrog in https://github.com/astropy/extension-helpers/pull/39
- Set language for docs by @lpsinger in https://github.com/astropy/extension-helpers/pull/45
- Update python requirements by @WilliamJamieson in https://github.com/astropy/extension-helpers/pull/50
- Add pre-commit configuration by @astrofrog in https://github.com/astropy/extension-helpers/pull/53
- Set testpaths to avoid picking up other tests by @astrofrog in https://github.com/astropy/extension-helpers/pull/54
- Added configuration required to update changelog when doing release through GitHub UI by @astrofrog in https://github.com/astropy/extension-helpers/pull/56

### New Contributors

- @WilliamJamieson made their first contribution in https://github.com/astropy/extension-helpers/pull/50
- @pre-commit-ci made their first contribution in https://github.com/astropy/extension-helpers/pull/55

**Full Changelog**: https://github.com/astropy/extension-helpers/compare/v1.0.0...v1.1.0

## 1.0.0 - 2022-03-16

- Added support for coverage>=5 for the extension-helpers test suite. [#24]
- Removed any direct usage of distutils. [#34]
- Remove support for the undocumented --compiler argument to setup.py. [#36]
- Added support for enabling extension-helpers from setup.cfg. [#33]

## 0.1 - 2019-12-18

- Initial release of extension-helpers, which was forked from astropy-helpers 4.0.
