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
