from __future__ import print_function
from collections import namedtuple
import hawkey
import logging
import os
import re

from rpmreq import exception
from rpmreq import helpers


log = logging.getLogger(__name__)


Package = namedtuple('Package', ['name', 'version', 'release', 'repo_id'])
Repo = namedtuple('Repo', ['id', 'url'])
RepoMeta = namedtuple('RepoMeta', ['primary', 'filelists'])
DepQueryResult = namedtuple('DepQueryReport', ['package', 'latest'])


def parse_repo_str(repo_str):
    parts = repo_str.split(',', 1)
    repo_url = parts[-1]
    if len(parts) > 1:
        repo_id = parts[0]
    else:
        repo_id = None
    return Repo(repo_id, repo_url)


def get_repomd_location(repomd, location):
    # regex abuse to evade xml parser requirement
    m = re.search(r'<location href="repodata/([^"]+-%s.xml[^"]*)"'
                  % location, str(repomd))
    if m:
        return m.group(1)
    return None


def parse_repomd(repomd):
    repometa = RepoMeta(primary=get_repomd_location(repomd, 'primary'),
                        filelists=get_repomd_location(repomd, 'filelists'))
    if not (repometa[0] and repometa[1]):
        raise exception.RepoMDParsingFailed()
    return RepoMeta(primary=get_repomd_location(repomd, 'primary'),
                    filelists=get_repomd_location(repomd, 'filelists'))


def fetch_repo(repo, base_path=None, cache_ttl=3600):
    """
    Fetch remote metadata for a list of Repos into {base_path}/{repo.url hash}/
    and return a hawkey.Repo configured with local repodata.

    :param repo: RPM repository to fetch (Repo named tuple)
    :param base_path: a base path to store local repodata cache in
    :param cache_ttl: time to live for local repodata cache (0 to disable)
    :return: hawkey.Repo pointing to local repodata ready to be loaded
    """
    if not base_path:
        base_path = helpers.get_default_cache_base_path()
    repodata_url = "%s/repodata" % repo.url
    repo_path = os.path.join(base_path, helpers.repo_dir(repo.id, repo.url))
    log.info("Fetching %s into %s", repodata_url, repo_path)
    helpers.ensure_dir(repo_path)
    # fetch remote repodata files
    repomd = helpers.cached_remote_fetch(
        repo_path, repodata_url, 'repomd.xml',
        cache_ttl=cache_ttl, return_data=True)
    primary_fn, filelists_fn = parse_repomd(repomd)
    helpers.cached_remote_fetch(
        repo_path, repodata_url, primary_fn, cache_ttl=cache_ttl)
    helpers.cached_remote_fetch(
        repo_path, repodata_url, filelists_fn, cache_ttl=cache_ttl)
    # consturct hawkey.Repo pointing to local metadata
    hrepo = hawkey.Repo(repo.id)
    hrepo.repomd_fn = os.path.join(repo_path, 'repomd.xml')
    hrepo.primary_fn = os.path.join(repo_path, primary_fn)
    hrepo.filelists_fn = os.path.join(repo_path, filelists_fn)
    return hrepo


def fetch_repos_sack(repos, base_path=None, cache_ttl=3600):
    """
    Fetch all repos using fetch_repo and load them into a hawkey.Sack.

    :param repos: a list of RPM repos to fetch (Repo named tuples)
    :param base_path: a base path to store local repodata cache in
    :param cache_ttl: time to live for local repodata cache (0 to disable)
    :return: a hawkey.Sack instance loaded with supplied repos
    """
    sack = hawkey.Sack(make_cache_dir=True)
    for repo in repos:
        hrepo = fetch_repo(repo, base_path=base_path, cache_ttl=cache_ttl)
        log.info("Loading repository metadata: %s", repo.id)
        sack.load_repo(hrepo, load_filelists=True)
    return sack


def dep_base(dep):
    """
    Strip a dependency of version requirements, for example:

        dep_base('foo >= 1.2.3') == 'foo'

    :param dep: dependency to strip version from
    :return: dep stripped of version requirement (str)
    """
    dep = str(dep)
    m = re.match(r'([^<>!=\s]+)\s*[<>!=]', dep)
    if m:
        return m.group(1)
    return dep


def query_dep(q, dep):
    """
    Query a dependency.

    :param q: hawkey.Query instance
    :param dep: dependency to query
    :return: DepQueryResult double:
             - (package, None) when dep is met
             - (None, latest) when dep isn't met but it's available
               at wrong version - latest version available is returned
             - (None, None) when dep isn't met
    """
    r = q.filter(provides__glob=str(dep), latest_per_arch=True)
    if r:
        return DepQueryResult(r[0], None)
    else:
        # look for any version of the required package
        base = dep_base(dep)
        if base != dep:
            r = q.filter(provides__glob=dep_base(dep),
                         latest_per_arch=True)
            if r:
                # wrong version
                return DepQueryResult(False, r[0])
        return DepQueryResult(False, None)


def query_dep_with_base(q, q_base, dep):
    """
    Query a dependency with a fallback to base repos.

    :param q: hawkey.Query instance
    :param q_base: hawkey.Query instance
    :param dep: dependency to query
    :return: (query_result, base) where base is True when
             match was found in base repos (using q_base)
    """
    r = query_dep(q, dep)
    if r.package or not q_base:
        # found in primary or no base supplied
        return r, False
    br = query_dep(q_base, dep)
    if br.package:
        # found in base repos
        return br, True
    if br.latest and not r.latest:
        # wrong version in base is better than nothing
        return br, True
    # wrong version from primary is preferred to one from base
    return r, False
