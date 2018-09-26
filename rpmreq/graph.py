from collections import namedtuple, defaultdict
import logging
import math

import hawkey
import networkx as nx
from pyrpm.spec import Spec, replace_macros

from rpmreq import query
import rpmreq.spec


log = logging.getLogger(__name__)


DepReport = namedtuple('DepReport', ['met', 'wrong_version', 'missing'])


class DepNode(object):
    def __init__(self, pkg=None, dep=None, node_type=None, special=None):
        self.pkg = pkg
        self.dep = dep
        self.node_type = node_type
        self.special = special

    def __hash__(self):
        return hash("%s%s%s" % (self.pkg or self.dep,
                                self.node_type,
                                self.special))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.pkg == other.pkg
                    and self.dep == other.dep
                    and self.node_type == other.node_type
                    and self.special == other.special)
        return NotImplemented

    def __repr__(self):
        s = ''
        if self.special:
            s += '[%s] ' % self.special
        if self.node_type:
            s += '%s: ' % self.node_type
        if self.pkg:
            s += str(self.pkg)
        elif self.dep:
            s += str(self.dep)
        return s


ROOT_NODE = DepNode('rpmreq', special='ROOT')


def dep_query_result2node(result, dep=None):
    child, wrong_version = result
    if child:
        node = DepNode(pkg=child)
    elif wrong_version:
        node = DepNode(pkg=wrong_version, node_type='WRONG VERSION')
    else:
        node = DepNode(dep=dep, node_type='MISSING')
    return node


def _build_dep_graph(dep_graph, processed, parent, deps, q, base_q=None):
    """
    A recursive function to build a dependency graph.

    :param dep_graph: networkx.DiGraph to build
    :param processed: dict of already processed deps
    :param parent: parent package
    :param deps: list of packages parent depends on
    :param q: hawkey.Query to query available packages
    :param base_q: hawkey.Query to query base repos
    """
    for dep in deps:
        # support hawkey.Reldel
        dep_str = str(dep)
        process_children = False
        if dep_str in processed:
            target_node = processed[dep_str]
        else:
            result, base = query.query_dep_with_base(q, base_q, dep)
            target_node = dep_query_result2node(result, dep)
            if base:
                target_node.special = 'BASE'
            else:
                if result.package:
                    # only recurse on met packages not in base
                    process_children = True
            processed[dep_str] = target_node

        log.info("New edge: %s ---( %s )---> %s",
                 parent, dep_str, target_node)
        # NOTE: write_dot stuck with labeled edges, w00t?!
        dep_graph.add_edge(parent, target_node, label=dep_str)

        if process_children:
            log.info("Processing: %s", target_node)
            _build_dep_graph(dep_graph, processed,
                             target_node, target_node.pkg.requires,
                             q=q, base_q=base_q)


def build_requires_graph(specs, repos, base_repos=None, cache_ttl=3600):
    if isinstance(specs, str):
        # support both a single spec and a list
        specs = [specs]

    # get hawkey.Sack of repos to query
    sack = query.fetch_repos_sack(repos)
    q = hawkey.Query(sack)
    log.info("Loaded %d packages from %d repos." % (len(sack), len(repos)))
    if base_repos:
        base_sack = query.fetch_repos_sack(base_repos)
        base_q = hawkey.Query(base_sack)
        log.info("Loaded %d packages from %d base repos." % (
            len(base_sack), len(base_repos)))
    else:
        base_q = None

    dep_graph = nx.DiGraph()
    processed = {}
    for spec_fn in specs:
        log.info("Processing .spec file: %s", spec_fn)
        spec = Spec.from_file(spec_fn)
        brs = rpmreq.spec.build_requires(spec)
        spec_node = DepNode(spec_fn, special='SPEC')
        dep_graph.add_edge(ROOT_NODE, spec_node)
        # build a dependency graph recursively
        _build_dep_graph(dep_graph, processed, spec_node, brs,
                         q=q, base_q=base_q)

    return dep_graph


def break_dep_graph_cycles(dep_graph):
    """
    Remove cycles in dependency graph by using special
    "CIRCULAR:" reference nodes.
    """
    while True:
        cycles = nx.simple_cycles(dep_graph)
        cycle = next(cycles, None)
        if not cycle:
            break
        n1 = cycle[-1]
        n2 = cycle[0]
        log.info('Breaking circular dep: %s --> %s', n1, n2)
        dep_graph.remove_edge(n1, n2)
        n2_ref = DepNode(pkg=n2.pkg,
                         node_type=n2.node_type,
                         special='CIRCULAR')
        dep_graph.add_edge(n1, n2_ref)
    return dep_graph


def parse_dep_graph(dep_graph):
    """
    Parse dependency graph into DepReport lists.

    :param graph: dependency graph to parse as returned by build_dep_graph
    :return: DepReport
    """
    nodes_dict = defaultdict(list)
    for node in nx.dfs_postorder_nodes(dep_graph, source=ROOT_NODE):
        if node.special in ['BASE', 'SPEC', 'ROOT']:
            continue
        node_type = node.node_type or 'MET'
        nodes_dict[node_type].append(node.pkg or node.dep)
    return DepReport(nodes_dict['MET'],
                     nodes_dict['WRONG VERSION'],
                     nodes_dict['MISSING'])


NODE_COLOR_MAP = {
    'MET': 'lightgreen',
    'WRONG VERSION': 'yellow',
    'MISSING': 'red',
}


def dump_dep_graph(dep_graph,
                   out_data=None,
                   out_image=None,
                   title='Dependency Graph'):
    if not (out_data or out_image):
        log.warn("Ignoring request to dump graph with no output specified.")
        return False
    log.info("Dumping dep graph with %d edges between %d nodes...",
             dep_graph.number_of_edges(), dep_graph.number_of_nodes())
    if out_data:
        log.info("Writing graph as GEXF file: %s" % out_data)
        nx.write_gexf(dep_graph, out_data)
    if not out_image:
        return True
    try:
        # not a hard requirement
        import matplotlib.pyplot as plt
        from networkx.drawing.nx_agraph import graphviz_layout
    except ImportError as ex:
        log.warn("Can't render graph due to missing modules: %s" % ex)
        return False
    # try to figure out correct output size
    k = math.sqrt(dep_graph.number_of_nodes())
    plt.figure(figsize=(10 * k, 3 * k))
    plt.title(title)
    log.info("Computing graph layout...")
    pos = graphviz_layout(dep_graph, prog='dot')
    # draw nodes
    nodes_dict = defaultdict(list)
    for node in dep_graph.nodes():
        node_type = node.node_type or 'MET'
        nodes_dict[node_type].append(node)
    for node_type, nodes in nodes_dict.items():
        nx.draw_networkx_nodes(
            dep_graph, pos, nodelist=nodes,
            node_shape="h", node_size=600,
            node_color=NODE_COLOR_MAP.get(node_type, 'blue'))
    # draw edges
    nx.draw_networkx_edges(dep_graph, pos, alpha=0.3, font_size=8)
    # draw labels
    nx.draw_networkx_labels(dep_graph, pos)

    log.info("Writing graph as an image: %s" % out_image)
    plt.savefig(out_image, bbox_inches='tight')
    return True
