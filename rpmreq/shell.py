"""
Usage: rpmreq build-requires [-r <repo>]... [-R <repos>]... <spec>...
       rpmreq --help | --version

Traverse RPM Requires and BuildRequires dependency trees.

Commands:
  build-requires  show all packages needed to build specified package(s)

Arguments:
  <spec>       RPM .spec file to operate on.

Options:
  -r, --repo <repo>         look for available packages in <repo> RPM repo
  -R, --repo-file <repos>   TODO: look for available packages in all RPM repos
                            in <repos> file (one per line)
  --version                 TODO: show rpmreq version
  -h, --help                show usage help
"""
# -*- encoding: utf-8 -*-
from __future__ import print_function
from docopt import docopt
from pyrpm.spec import Spec, replace_macros

import logging

log = logging.getLogger(__name__)


def build_requires(specs=[], repos=[], repo_files=[]):
    for spec_fn in specs:
        log.info('Processing .spec file: %s' % spec_fn)
        spec = Spec.from_file(spec_fn)
        brs = spec.build_requires
        for pkg in spec.packages:
            pbrs = getattr(pkg, 'build_requires', [])
            if pbrs:
                brs += pbrs
        print("%s BuildRequires:" % spec.name)
        brs = sorted(brs)
        for br in brs:
            print('  %s' % br)


def run(cargs, version=None):
    code = 1
    args = docopt(__doc__, argv=cargs)
    if args['build-requires']:
        build_requires(specs=args['<spec>'])
        code = 0
    return code
