from __future__ import print_function
from collections import namedtuple
import sh


def parse_repo_str(repo_str):
    parts = repo_str.split(',', 1)
    repo_url = parts[-1]
    if len(parts) > 1:
        repo_id = parts[0]
    else:
        repo_id = None
    return repo_id, repo_url


Package = namedtuple('Package', 'name version release repoid')


def last_version(package, repos=None, provides=True):
    cmd = ['repoquery', '--latest-limit', '1',
           '--qf', '%{name},%{version},%{release},%{repoid}']
    if repos:
        for repo in repos:
            repo_id, repo_url = parse_repo_str(repo)
            cmd += ["--repofrompath=%s,%s" % (repo_id, repo_url),
                    "--repoid=%s" % repo_id]
    if provides:
        # take virtual packages into consideration
        cmd.append('--whatprovides')
    cmd.append(package)
    o = sh.dnf(*cmd)
    if o.exit_code != 0:
        return Package(None, None, None, None)
    out = o.strip().split("\n")[0]
    try:
        name, version, release, repoid = out.rsplit(',')
    except ValueError:
        return Package(None, None, None, None)
    return Package(name=name, version=version, release=release, repoid=repoid)
