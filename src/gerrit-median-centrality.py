#!/usr/bin/env python

"""Compute the median closeness centrality of the Gerrit review graph."""

import json
import sys
import os

import numpy as np
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
gerrit_graph = __import__("gerrit-graph")


def median_centrality(graph):
    """Print the median closeness centrality to stdout."""
    undirected = graph.to_undirected()
    connected_components = nx.connected_components(undirected)
    closeness = [nx.closeness_centrality(undirected, u=cc)
                 for cc in connected_components[0]]
    median = np.median(closeness)
    print('{0:.2f}'.format(median))
    return median

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] +
              ' <gerrit_data.json>')
        sys.exit(1)

    gerrit_data = sys.argv[1]
    with open(gerrit_data, 'r') as fp:
        data = json.load(fp)
    graph = gerrit_graph.reviewer_graph(data['changes'])
    median_centrality(graph)
