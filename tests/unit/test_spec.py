import rpmreq.cli
import rpmreq.spec
from pyrpm.spec import Spec

import tests.test_common as common


def test_spec_build_requires():
    spec_path = common.get_test_spec_path('foo')
    spec = Spec.from_file(spec_path)
    brs = map(str, rpmreq.spec.build_requires(spec))
    exp = [
        "PyYAML",
        "asciidoc >= 0.1",
        "bar == 1.2.3",
        "git",
        "python",
        "python-pbr",
        "python-setuptools",
        "python2-devel",
        "python2-macro-disabled-breq",
        "python2-macro-enabled-breq",
        "python3-PyYAML",
        "python3-devel",
        "python3-pbr",
        "python3-setuptools",
    ]
    assert sorted(brs) == exp
