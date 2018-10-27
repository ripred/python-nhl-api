#!/usr/bin/env python3

"""
    Schedule class for the nhlapi package
"""

import sys
import json
import argparse
import nhlapi
from nhlapi import get_json_data


class Schedule:
    """
    Schedule class for the nhlapi package
    """

    STATS = {'scheduleBroadcasts': 0,
             'scheduleLinescore': 1,
             'scheduleTicket': 2,
             'teamId': 3,
             'date': 4,
             'startDate': 5,
             'endDate': 6}

    modifiers = {STATS['scheduleBroadcasts']: 'expand=schedule.broadcasts',
                 STATS['scheduleLinescore']: 'expand=schedule.linescore',
                 STATS['scheduleTicket']: 'expand=schedule.ticket',
                 STATS['teamId']: 'teamId={}',
                 STATS['date']: 'date={}',
                 STATS['startDate']: 'startDate={}',
                 STATS['endDate']: 'endDate={}'}

    base_url = 'https://statsapi.web.nhl.com/api/v1/'

    def __init__(self, url=None, content=None):
        """
        initialize this Schedule object

        :param self: reference to a Schedule instance
        :param url: (optional) url to use to get the data for this object
        :param content: (optional) content for this object instance
        """
        self.url = ''
        self.content = {}
        if url is not None:
            self.url = url
        else:
            self.url = self.base_url + 'schedule'
        if content is not None:
            self.content = content
        else:
            self.content = get_json_data(self.url)

    def get_ext_url(self, *modifiers, season=None):
        """ get extra stats url's """
        sep = '?'
        suffix = ''
        url = self.url
        if season is not None:
            suffix = '&season={}{}'.format(season, season + 1)
        if isinstance(modifiers, int):
            return url + sep + self.modifiers[modifiers] + suffix
        for elem in modifiers:
            if isinstance(elem, (int, str, float)):
                url += sep + self.modifiers[int(elem)]
            elif isinstance(elem, dict):
                for key, value in elem.items():
                    if isinstance(value, (int, str, float)):
                        url += sep + self.modifiers[key].format(value)
                    else:
                        url += sep + self.modifiers[key].format(*value)
            sep = '&'
        return url + suffix

    def load_ext_url(self, *modifiers, year=None):
        """ load the values from the extra data specified """
        url = self.get_ext_url(*modifiers, season=year)
        self.content = get_json_data(url)


def parse_args():
    """
    Parse the options from the command line

    :return: The options as a dictionary
    """
    description = 'use the nhlapi/Schedule class to retrieve' +\
                  'information about a scheduled games in the NHL.'
    epilog = 'Example use: schedule.py --log schedule.log' +\
             '--humanReadable --scheduleBroadcasts --date=2018-10-26'
    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('--scheduleBroadcasts',
                        help='retrieve scheduleBroadcasts data', action='store_true')
    parser.add_argument('--scheduleLinescore', help='retrieve scheduleLinescore data',
                        action='store_true')
    parser.add_argument('--scheduleTicket', help='retrieve scheduleTicket data',
                        action='store_true')
    parser.add_argument('--teamId', help='set a specific team to retrieve', type=str)
    parser.add_argument('--date', help='set a specific date to retrieve', type=str)
    parser.add_argument('--startDate', help='set a specific starting date to retrieve', type=str)
    parser.add_argument('--endDate', help='set a specific ending date to retrieve', type=str)

    parser.add_argument('--humanReadable', help='output in easier to read format for users',
                        action='store_true')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('a'),
        help='the file where the output should be written')

    args = parser.parse_args()
    schedule = Schedule()
    if not schedule:
        print('unable to create Schedule object')
        return args

    # args_vars = vars(args)
    params = []
    if args.scheduleBroadcasts:
        params.append(Schedule.STATS['scheduleBroadcasts'])
    if args.scheduleLinescore:
        params.append(Schedule.STATS['scheduleLinescore'])
    if args.scheduleTicket:
        params.append(Schedule.STATS['scheduleTicket'])
    if args.teamId:
        params.append({Schedule.STATS['teamId']: args.teamId})
    if args.date:
        params.append({Schedule.STATS['date']: args.date})
    if args.startDate:
        params.append({Schedule.STATS['startDate']: args.startDate})
    if args.endDate:
        params.append({Schedule.STATS['endDate']: args.endDate})

    if params:
        schedule.load_ext_url(*params)

        if args.humanReadable:
            output = json.dumps(schedule.content, indent=1)
        else:
            output = schedule.content

        print(output)

    result = 'retrieved schedule'

    args.log.write('%s\n' % result)
    args.log.close()
    return args


if __name__ == '__main__':
    #
    parse_args()

#   def run_self():
#       """ test code """
#       year = 1981
#       team_id = 22                  # Edmonton Oilers

#       schedule = Schedule()

#       print(schedule.get_ext_url(Schedule.scheduleBroadcasts))

#       print(schedule.get_ext_url(Schedule.scheduleBroadcasts, season=year))
#       print(schedule.get_ext_url(Schedule.scheduleLinescore, season=year))
#       print(schedule.get_ext_url(Schedule.scheduleTicket, season=year))
#       print(schedule.get_ext_url({Schedule.teamId: team_id}, season=year))
#       print(schedule.get_ext_url({Schedule.date: (year, 1, 1)}, season=year))
#       print(schedule.get_ext_url({Schedule.startDate: (year, 1, 1)}, season=year))
#       print(schedule.get_ext_url({Schedule.endDate: (year, 1, 1)}, season=year))

#   exit(run_self())
