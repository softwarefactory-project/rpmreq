import hawkey
import logging

from rpmreq import graph
from rpmreq import query


log = logging.getLogger(__name__)


def build_requires(specs, repos, base_repos=None,
                   out_data=None, out_image=None,
                   cache_ttl=3600):
    dep_graph = graph.build_requires_graph(
        specs=specs, repos=repos, base_repos=base_repos,
        cache_ttl=cache_ttl)
    graph.break_dep_graph_cycles(dep_graph)
    if out_data or out_image:
        graph.dump_dep_graph(dep_graph,
                             out_data=out_data,
                             out_image=out_image)
    return graph.parse_dep_graph(dep_graph)


def last_version(dep, repos):
    """
    Return latest package meeting dep
    or latest version of dep regardless of version range.

    :param dep: dependency to meet
    :param repos: repos to query
    :return: DepQueryResult, see rpmreq.query.query_dep
    """
    sack = query.fetch_repos_sack(repos)
    q = hawkey.Query(sack)
    return query.query_dep(q, dep)
