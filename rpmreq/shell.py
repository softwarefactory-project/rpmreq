"""
Usage: rpmreq build-requires [-r <repo>]... [-R <repos>]... [-b <repo>]... [-B <repos>]... [-o <data>] [-O <image>] <spec>...
       rpmreq last-version [-r <repo>] [-R <repos>] <dep>
       rpmreq --help | --version

Traverse RPM Requires and BuildRequires dependency trees.

Commands:
  build-requires  show all packages needed to build specified package(s)
  last-version    show latest package from <repos> matching <dep>

Arguments:
  <spec>       RPM .spec file to operate on.

Options:
  -r, --repo <repo>          look for available packages in <repo> RPM repo
                             (repoid,url format)
  -R, --repo-file <repos>    look for available packages in all <repos>
                             (one repo per line in repoid,url format)
  -b, --base-repo <repo>     look for base packages in <repo> RPM repo
                             (repoid,url format)
  -B, --base-repo-file <repos>  look for base packages in all <repos>
                             (one repo per line in repoid,url format)
  -o, --out-data <data>      dump dep graph data into <data> file in GEXF format
  -O, --out-image <image>    render dep graph into <image> file in SVG format
  --version                  TODO: show rpmreq version
  -h, --help                 show usage help
"""  # noqa
# -*- encoding: utf-8 -*-
from __future__ import print_function
from docopt import docopt

from rpmreq import actions
from rpmreq import exception
from rpmreq import query

import logging


log = logging.getLogger(__name__)


def _parse_repo_args(repos=None, repo_files=None):
    r = []
    if repos:
        r += repos
    if repo_files:
        for repo_file in repo_files:
            lines = open(repo_file, 'r').read().splitlines()
            r += lines
    r = list(map(query.parse_repo_str, r))
    return r


def build_requires(specs, repos, base_repos=None,
                   out_data=None, out_image=None,
                   cache_ttl=3600):
    met, wrong_version, missing = actions.build_requires(
        specs=specs, repos=repos, base_repos=base_repos,
        out_data=out_data, out_image=out_image,
        cache_ttl=cache_ttl)
    print("\nMET BUILD REQUIRES:")
    for pkg in met:
        print(str(pkg))
    print("\nBUILD REQUIRES AT WRONG VERSION:")
    for pkg in wrong_version:
        print(str(pkg))
    print("\nMISSING BUILD REQUIRES:")
    for dep in missing:
        print(str(dep))


def last_version(dep, repos):
    if not repos:
        raise exception.InvalidUsage(
            why="No repos selected. Please use -r/-R.")
    met, latest = actions.last_version(dep, repos=repos)
    msg = "%s " % dep
    if met:
        msg += "MET: %s" % met
    elif latest:
        msg += "WRONG VERSION: %s" % latest
    else:
        msg += "MISSING"
    print(msg)


def run(cargs, version=None):
    code = 1
    args = docopt(__doc__, argv=cargs)
    try:
        if args['build-requires']:
            build_requires(specs=args['<spec>'],
                           repos=_parse_repo_args(
                               repos=args['--repo'],
                               repo_files=args['--repo-file']),
                           base_repos=_parse_repo_args(
                               repos=args['--base-repo'],
                               repo_files=args['--base-repo-file']),
                           out_data=args['--out-data'],
                           out_image=args['--out-image'],
                           )
            code = 0
        elif args['last-version']:
            last_version(dep=args['<dep>'],
                         repos=_parse_repo_args(
                             repos=args['--repo'],
                             repo_files=args['--repo-file']))
        code = 0
    except (
            exception.InvalidUsage,
            exception.NotADirectory,
            KeyboardInterrupt,
    ) as ex:
        code = getattr(ex, 'exit_code', code)
        print("")
        print(str(ex) or type(ex).__name__)

    return code
