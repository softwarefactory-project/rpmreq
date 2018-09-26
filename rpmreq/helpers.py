import contextlib
import hashlib
import logging
import os
import requests
import time

from rpmreq import exception


log = logging.getLogger(__name__)


@contextlib.contextmanager
def cdir(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def ensure_dir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise exception.NotADirectory(path=path)
    else:
        os.makedirs(path)


def get_default_cache_base_path():
    return os.path.expanduser("~/.rpmreq/cache")


def short_hash(s):
    return hashlib.sha1(s.encode()).hexdigest()[:6]


def repo_dir(repo_id, repo_url):
    return "%s_%s" % (repo_id, short_hash(repo_url))


def get_file_age(path):
    t_mod = os.path.getctime(path)
    t_now = time.time()
    return t_now - t_mod


def cached_remote_fetch(cache_path, base_url, fn,
                        cache_ttl=3600, return_data=False):
    ensure_dir(cache_path)
    url = "%s/%s" % (base_url, fn)
    path = os.path.join(cache_path, fn)
    fetch = True
    if cache_ttl and os.path.exists(path):
        # look for cache first
        age = get_file_age(path)
        if age <= cache_ttl:
            # use cached version
            fetch = False
    if fetch:
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise exception.RemoteFileFetchFailed(code=r.status_code, url=url)
        open(path, 'wb').write(r.content)
        if return_data:
            return r.content
        else:
            return True
    else:
        log.info('Using %d s old cached version of %s' % (age, fn))
        if return_data:
            return open(path, 'rt').read()
        else:
            return False
