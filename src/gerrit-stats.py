#!/usr/bin/env python

"""Analyze submissions and reviews made with Gerrit Code Review.

Example::

    gerrit-stats.py --port 22 alice@review.source.kitware.com 'project:ITK limit:100'

Dependencies:

* matplotlib
* ssh

"""

__author__ = "Matt McCormick"
__email__ = "matt.mccormick@kitware.com"
__license__ = "Apache 2.0"

import argparse
import json
import os
import subprocess

import numpy as np
from matplotlib import pylab as plt

def get_changes(host, port, query):
    """Download the changes from the Gerrit server and return the JSON data
    structure."""
    json_changes = '{"changes":['
    retrieved_changes = None
    changes_to_skip = 0

    while retrieved_changes is None or retrieved_changes == 500:
        ssh_call = ['ssh', '-p', str(port), host, 'gerrit', 'query',
                '--format=JSON', '--all-approvals',
                '--start', str(changes_to_skip)]
        ssh_call.extend(query.split())
        query_results = subprocess.check_output(ssh_call)
        query_results = query_results.split('\n')
        retrieval_stats = json.loads(query_results[-2])
        retrieved_changes = int(retrieval_stats['rowCount'])
        changes_to_skip += retrieved_changes
        print('Number of changes retrieved: ' + str(retrieval_stats['rowCount']))
        print('Time for retrieval [msec]:   ' + str(retrieval_stats['runTimeMilliseconds']))
        query_results = query_results[:-2]
        query_results = ','.join(query_results)
        json_changes += query_results
        json_changes += ','

    json_changes = json_changes[:-1]
    json_changes += ']}'
    json_changes = json.loads(json_changes)
    return json_changes


def reviewers_histogram(changes):
    """Get a dictionary of "reviewer_name: (reviewer_email, review_count)"."""
    reviews = []
    for change in changes:
        patch_sets = change['patchSets']
        for patch_set in patch_sets:
            if patch_set.has_key('approvals'):
                for approval in patch_set['approvals']:
                    reviews.append(approval['by'])

    histogram = {}
    for review in reviews:
        if review.has_key('name') and review.has_key('email'):
            name = review['name']
            if histogram.has_key(name):
                current_count = histogram[name][1]
                histogram[name] = (review['email'], current_count+1)
            else:
                histogram[name] = (review['email'], 1)

    return histogram


def reviewer_bar_chart(reviewers, max_reviewers, output_dir):
    """Bar chart of sorted number of reviews per reviewer."""
    reviewer_names = [(key, value[1]) for key, value in reviewers.iteritems()]
    reviewer_names.sort(key=lambda x: x[1])
    reviewer_names.reverse()
    print(reviewer_names)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if max_reviewers > len(reviewer_names):
        max_reviewers = len(reviewer_names)
    position = np.arange(max_reviewers, 0, -1)
    review_count = [x[1] for x in reviewer_names][:max_reviewers]
    names = [x[0] for x in reviewer_names][:max_reviewers]
    ax.barh(position - 0.4, review_count)
    ax.set_yticks(position)
    ax.set_yticklabels(names)
    ax.set_xlabel('Review Count')
    fig.savefig(os.path.join(output_dir, 'reviewer_bar_chart.png'))


def domain_bar_chart(reviewers, max_domains, output_dir):
    """Bar chart of sorted number of reviews per email domain."""
    reviewer_emails = [(value[0], value[1]) for key, value in reviewers.iteritems()]
    domain_histogram = {}
    for reviewer in reviewer_emails:
        email = reviewer[0]
        domain = email.split('@')[1]
        if domain_histogram.has_key(domain):
            current_count = domain_histogram[domain][1]
            domain_histogram[domain] = (domain, current_count+reviewer[1])
        else:
            domain_histogram[domain] = (domain, reviewer[1])

    domain_counts = [(key, value[1]) for key, value in domain_histogram.iteritems()]
    domain_counts.sort(key=lambda x: x[1])
    domain_counts.reverse()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if max_domains > len(domain_counts):
        max_domains = len(domain_counts)
    position = np.arange(5, max_domains + 5)
    review_count = [x[1] for x in domain_counts][:max_domains]
    domains = [x[0] for x in domain_counts][:max_domains]
    ax.bar(position - 0.4, review_count)
    ax.set_xticks(position)
    ax.set_xticklabels(domains, rotation=65)
    ax.set_ylabel('Review Count')
    fig.savefig(os.path.join(output_dir, 'domain_bar_chart.png'),
            bbox_inches='tight')


def main(args):
    changes = get_changes(args.host, args.port, args.query)
    #print(json.dumps(changes, indent=2))

    changes = changes['changes']
    reviewers = reviewers_histogram(changes)
    print(reviewers)

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    reviewer_bar_chart(reviewers, 15, output_dir)
    domain_bar_chart(reviewers, 10, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', '-p', type=int, default=29418)
    parser.add_argument('host', help='Host for the Gerrit Code Review instance.')
    parser.add_argument('query',
        help='Gerrit query to select changes.  See http://gerrit.googlecode.com/svn/documentation/2.2.1/user-search.html')
    parser.add_argument('output_dir',
        help='Directory to write output analysis files')
    args = parser.parse_args()
    main(args)
