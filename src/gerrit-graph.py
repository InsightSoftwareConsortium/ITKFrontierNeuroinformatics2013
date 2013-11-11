#!/usr/bin/env python

"""Do a graph visualization of the Gerrit reviews."""

import collections
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import networkx as nx
from networkx.readwrite import json_graph
import prettyplotlib

mpl.rcParams['font.size'] = 10

mpl.rcParams['axes.labelsize'] = 'x-large'
mpl.rcParams['xtick.labelsize'] = 'large'
mpl.rcParams['ytick.labelsize'] = 'large'
mpl.rcParams['figure.dpi'] = 900


class hashdict(dict):
    """
    hashable dict implementation, suitable for use as a key into
    other dicts.

        >>> h1 = hashdict({"apples": 1, "bananas":2})
        >>> h2 = hashdict({"bananas": 3, "mangoes": 5})
        >>> h1+h2
        hashdict(apples=1, bananas=3, mangoes=5)
        >>> d1 = {}
        >>> d1[h1] = "salad"
        >>> d1[h1]
        'salad'
        >>> d1[h2]
        Traceback (most recent call last):
        ...
        KeyError: hashdict(bananas=3, mangoes=5)

    based on answers from
       http://stackoverflow.com/questions/1151658/python-hashable-dicts

    """
    def __key(self):
        return tuple(sorted(self.items()))

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
               ", ".join("{0}={1}".format(str(i[0]),
                                          repr(i[1])) for i in self.__key()))

    def __hash__(self):
        return hash(self.__key())

    def __setitem__(self, key, value):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def __delitem__(self, key):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def clear(self):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def pop(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def popitem(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def setdefault(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def update(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                        .format(self.__class__.__name__))

    def __add__(self, right):
        result = hashdict(self)
        dict.update(result, right)
        return result


def reviewer_identifier(reviewer):
    #return hashdict(reviewer)
    return reviewer.get('name', 'Unknown')


def reviewer_graph(changes):
    # Nodes are contributors identified by name and email
    contributors = set()
    for change in changes:
        contributors.add(reviewer_identifier(change['owner']))

    # Node attribute -- number of changes created
    created = collections.Counter({cc: 0 for cc in contributors})
    for change in changes:
        created[reviewer_identifier(change['owner'])] += 1

    # Node attribute -- number of change reviews
    reviewed = collections.Counter({cc: 0 for cc in contributors})
    for change in changes:
        for patch_set in change['patchSets']:
            for approval in patch_set.get('approvals', []):
                reviewed[reviewer_identifier(approval['by'])] += 1

    # Add the nodes to the graph
    graph = nx.DiGraph()
    for contributor in contributors:
        graph.add_node(contributor,
                       weights=created[contributor],
                       created=created[contributor],
                       reviewed=reviewed[contributor])

    # Edges are reviews with weights by count and accumulated_value
    review_counts = collections.Counter()
    review_accumulated_values = collections.Counter()
    for change in changes:
        owner = reviewer_identifier(change['owner'])
        for patch_set in change['patchSets']:
            for approval in patch_set.get('approvals', []):
                reviewer = reviewer_identifier(approval['by'])
                review_counts[(reviewer, owner)] += 1
                review_accumulated_values[(reviewer, owner)] += \
                    int(approval['value'])

    for edge in review_counts.keys():
        graph.add_edge(*edge,
                       count=review_counts[edge],
                       weights=review_counts[edge],
                       accumulated_value=review_accumulated_values[edge])

    return graph


def plot_graph(graph, outputfile=None):
    fig_width = 18.0
    golden_mean = (np.sqrt(5)-1.0)/2.0
    fig_height = fig_width * golden_mean

    fig, ax = plt.subplots(1, num=1, figsize=(fig_width, fig_height))

    pos = nx.spring_layout(graph, iterations=200)

    nodes = graph.nodes(data=True)
    node_weights = np.zeros((len(nodes),))
    for ii in range(len(nodes)):
        node_weights[ii] = nodes[ii][1].get('weights', 0.0)
    max_size = 500
    node_sizes = max_size * node_weights / node_weights.max()
    nx.draw_networkx_nodes(graph, pos, node_color='#A0CBE2', alpha=0.5,
                           node_size=node_sizes, linewidths=0.5)

    edges = graph.edges(data=True)
    edge_weights = np.zeros((len(edges),))
    for ii in range(len(edges)):
        edge_weights[ii] = edges[ii][2].get('weights', 0.0)
    max_width = 10.0
    edge_widths = max_width * edge_weights / edge_weights.max()
    nx.draw_networkx_edges(graph, pos, alpha=0.5, edge_cmap=mpl.cm.Blues,
                           width=edge_widths, edge_color="#0E59A2")

    nx.draw_networkx_labels(graph, pos, fontsize=10)

    plt.axis('off')
    plt.xlim([-0.1, 1.1])
    plt.ylim([-0.1, 1.1])

    if outputfile:
        fig.savefig(outputfile)
    else:
        plt.show()


def plot_closeness(graph, closenessfile=None):
    fig, ax = plt.subplots(1)
    undirected = graph.to_undirected()
    for connected_component in nx.connected_components(undirected):
        created = [graph.node[cc].get('weights', 1) for cc in connected_component]
        closeness = [nx.closeness_centrality(undirected, u=cc) for cc in connected_component]
        prettyplotlib.scatter(ax, created, closeness)
        print(closeness)
    ax.set_xlabel('Changes Authored')
    ax.set_ylabel('Closeness Centrality')
    ax.set_ylim(0.0, 1.0)
    ax.set_xscale('log')
    if closenessfile:
        fig.savefig(closenessfile)
    else:
        plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] +
              ' <gerrit_data.json> [output_render.eps] [gerrit_graph.json] [closeness_centrality.eps]')
        sys.exit(1)

    gerrit_data = sys.argv[1]
    with open(gerrit_data, 'r') as fp:
        data = json.load(fp)
    if len(sys.argv) > 2:
        outputfile = sys.argv[2]
        dirname = os.path.dirname(outputfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    else:
        outputfile = None

    graph = reviewer_graph(data['changes'])

    plot_graph(graph, outputfile)

    if len(sys.argv) > 3:
        gerrit_json_file = sys.argv[3]
        dirname = os.path.dirname(gerrit_json_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        for nn in graph:
            graph.node[nn]['name'] = nn
        data = json_graph.node_link_data(graph)
        with open(gerrit_json_file, 'wb') as fp:
            json.dump(data, fp)

    if len(sys.argv) > 4:
        closenessfile = sys.argv[4]
        dirname = os.path.dirname(closenessfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        plot_closeness(graph, closenessfile)
