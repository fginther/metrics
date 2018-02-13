#!/usr/bin/env python3
"""Submit metrics for number of bugs assigned to canonical-foundations.

Copyright 2018 Canonical Ltd.
Łukasz 'sil2100' Zemczak <lukasz.zemczak@canonical.com>
"""
import argparse

from datetime import datetime
from metrics.helpers import lp
from metrics.helpers import util


IMPORTANCE_LIST = [
    'Undecided', 'Critical', 'High', 'Medium', 'Low', 'Wishlist']
STATUS_LIST = [
    'New', 'Confirmed', 'Triaged', 'In Progress', 'Fix Committed',
    'Incomplete']


def collect(team_name, dryrun=False):
    """Collect data and push to InfluxDB."""
    team = lp.LP.people[team_name]
    now = datetime.now()

    counts = {i: dict.fromkeys(STATUS_LIST, 0) for i in IMPORTANCE_LIST}
    tasks = lp.LP.bugs.searchTasks(assignee=team, status=STATUS_LIST)
    for task in tasks:
        counts[task.importance][task.status] += 1

    data = []
    for importance, statuses in counts.items():
        for status, count in statuses.items():
            print('{} importance bugs with {} status: {}'.format(
                importance, status, count))
            data.append({
                'measurement': 'foundations_bugs',
                'time': now,
                'tags': {
                    'importance': importance,
                    'status': status,
                },
                'fields': {'count': count}
            })

    if not dryrun:
        print('Pushing data...')
        util.influxdb_insert(data)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--team', help='team name',
                        default='canonical-foundations')
    PARSER.add_argument('--dryrun', action='store_true')
    ARGS = PARSER.parse_args()
    collect(ARGS.team, ARGS.dryrun)
