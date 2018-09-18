"""
Usage: rpmreq build-requires [-Q] [-r <repo>]... [-R <repos>]... <spec>...
       rpmreq last-version [-r <repo>]... [-R <repos>]... <package>
       rpmreq --help | --version

Traverse RPM Requires and BuildRequires dependency trees.

Commands:
  build-requires  show all packages needed to build specified package(s)

Arguments:
  <spec>       RPM .spec file to operate on.

Options:
  -r, --repo <repo>         look for available packages in <repo> RPM repo
                            (repoid,url format)
  -R, --repo-file <repos>   look for available packages in all RPM repos
                            in <repos> file (one per line in repoid,url format)
  -Q, --no-query            don't query any package versions
  --version                 TODO: show rpmreq version
  -h, --help                show usage help
"""
# -*- encoding: utf-8 -*-
from __future__ import print_function
from docopt import docopt
from pyrpm.spec import Spec, replace_macros

from rpmreq import query

import logging


log = logging.getLogger(__name__)


def _parse_repo_args(repos=None, repo_files=None):
    if repos:
        r = repos
    else:
        r = []
    if repo_files:
        for repo_file in repo_files:
            lines = open(repo_file, 'r').readlines()
            r += lines
    return r


def version_str(package, version, release, source=None):
    if not package:
        return 'N/A'
    s = '%s-%s-%s' % (package, version, release)
    if source:
        s += ' @%s' % source
    return s


def build_requires(specs, repos=None, query_versions=True):
    if isinstance(specs, str):
        # support both a single spec and a list
        specs = [specs]
    if query_versions:
        if repos:
            print("Using following repos to query package versions:")
            for repo in repos:
                print("* %s" % repo)
        else:
            print("Using default system repos to query package versions.")
    for spec_fn in specs:
        log.info('Processing .spec file: %s' % spec_fn)
        spec = Spec.from_file(spec_fn)
        brs = spec.build_requires
        for pkg in spec.packages:
            pbrs = getattr(pkg, 'build_requires', [])
            if pbrs:
                brs += pbrs

        def _replace_macros(s):
            return replace_macros(s, spec=spec)

        brs = sorted(map(_replace_macros, brs))
        print("%s BuildRequires:" % _replace_macros(spec.name))
        if query_versions:
            for br in brs:
                version = query.last_version(br, repos=repos)
                print('  %s: %s' % (br, version_str(*version)))
        else:
            for br in brs:
                print('  %s' % br)


def last_version(package, repos=None):
    version = query.last_version(package, repos=repos)
    print("%s: %s" % (package, version_str(*version)))


def run(cargs, version=None):
    code = 1
    args = docopt(__doc__, argv=cargs)
    if args['build-requires']:
        build_requires(specs=args['<spec>'],
                       repos=_parse_repo_args(
                           repos=args['--repo'],
                           repo_files=args['--repo-file']),
                       query_versions=not args['--no-query'])
        code = 0
    elif args['last-version']:
        last_version(package=args['<package>'],
                     repos=_parse_repo_args(
                         repos=args['--repo'],
                         repo_files=args['--repo-file']))
        code = 0

    return code
