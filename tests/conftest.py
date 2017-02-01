def pytest_addoption(parser):
    parser.addoption('--db', action='append', default=[])
