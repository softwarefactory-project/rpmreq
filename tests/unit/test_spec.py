from rpmreq.cli import rpmreq
import pytest

import tests.test_common as common


def test_build_requires_base(capsys):
    spec_path = common.get_test_spec_path('foo')
    rpmreq('build-requires', '--no-query', spec_path)
    cap = capsys.readouterr()
    exp = ("foo BuildRequires:\n"
           "  PyYAML\n"
           "  asciidoc >= 0.1\n"
           "  bar == 1.2.3\n"
           "  git\n"
           "  python\n"
           "  python-pbr\n"
           "  python-setuptools\n"
           "  python2-devel\n"
           "  python2-macro-disabled-breq\n"
           "  python2-macro-enabled-breq\n"
           "  python3-PyYAML\n"
           "  python3-devel\n"
           "  python3-pbr\n"
           "  python3-setuptools\n")
    assert cap.out == exp


def test_build_requires_macros_basic(capsys):
    spec_path = common.get_test_spec_path('macros-basic')
    rpmreq('build-requires', '--no-query', spec_path)
    cap = capsys.readouterr()
    exp = ("macros-basic BuildRequires:\n"
           "  build-macros\n"
           "  git\n")
    assert cap.out == exp
