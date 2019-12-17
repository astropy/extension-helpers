def pytest_addoption(parser):
    parser.addoption("--openmp-expected", action="store",
                     default=None, help="help")
