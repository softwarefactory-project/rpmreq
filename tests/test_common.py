import os


ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
SPEC_ASSETS_PATH = os.path.join(ASSETS_PATH, 'spec')


def get_test_spec_path(name):
    return os.path.join(SPEC_ASSETS_PATH, name, '%s.spec' % name)
