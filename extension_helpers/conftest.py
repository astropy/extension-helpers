# This file contains settings for pytest that are specific to extension-helpers.
# Since we run many of the tests in sub-processes, we need to collect coverage
# data inside each subprocess and then combine it into a single .coverage file.
# To do this we set up a list which run_setup appends coverage objects to.
# This is not intended to be used by packages other than extension-helpers.

import glob
import os

try:
    from coverage import CoverageData
    from coverage import __version__ as coverage_version
except ImportError:
    HAS_COVERAGE = False
    CoverageData = None
else:
    # Set to the major version number
    HAS_COVERAGE = int(coverage_version.split(".")[0])


SUBPROCESS_COVERAGE = []


def pytest_configure(config):
    if HAS_COVERAGE:
        SUBPROCESS_COVERAGE.clear()


def pytest_unconfigure(config):
    if HAS_COVERAGE:
        # Add all files from extension_helpers to make sure we compute the total
        # coverage, not just the coverage of the files that have non-zero
        # coverage.

        lines = {}
        for filename in glob.glob(os.path.join("extension_helpers", "**", "*.py"), recursive=True):
            lines[os.path.abspath(filename)] = []

        for cdata in SUBPROCESS_COVERAGE:
            # For each CoverageData object, we go through all the files and
            # change the filename from one which might be a temporary path
            # to the local filename. We then only keep files that actually
            # exist.
            for filename in cdata.measured_files():
                try:
                    pos = filename.rindex("extension_helpers")
                except ValueError:
                    continue
                short_filename = filename[pos:]
                if os.path.exists(short_filename):
                    lines[os.path.abspath(short_filename)].extend(cdata.lines(filename))

        if HAS_COVERAGE >= 5:
            # Support coverage<5 and >=5; see
            # https://github.com/astropy/extension-helpers/issues/24
            # We create an empty coverage data object
            combined_cdata = CoverageData(suffix="subprocess")
            combined_cdata.add_lines(lines)
            combined_cdata.write()
        else:
            combined_cdata = CoverageData()
            combined_cdata.add_lines(lines)
            combined_cdata.write_file(".coverage.subprocess")
