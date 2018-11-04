#!/usr/bin/env python3

"""
    Team class for the nhlapi package
"""

# import sys
import json
import argparse
import logging
# from logging import debug
from logging import info
# from logging import warning
# from logging import error
# from logging import critical
from nhlapi import get_json_data


class Team:
    """
    Team class for the nhlapi package
    """

    STATS = {'teamRoster': 0,
             'personNames': 1,
             'teamScheduleNext': 2,
             'teamSchedulePrev': 3,
             'teamStats': 4,
             'teams': 5}

    modifiers = {STATS['teamRoster']: 'expand=team.roster',
                 STATS['personNames']: 'expand=person.names',
                 STATS['teamScheduleNext']: 'expand=team.schedule.next',
                 STATS['teamSchedulePrev']: 'expand=team.schedule.previous',
                 STATS['teamStats']: 'expand=team.stats',
                 STATS['teams']: ''}

    base_url = 'https://statsapi.web.nhl.com/api/v1/'

    def __init__(self, nhl_id, url=None, content=None):
        """
        initialize this Team object

        :param self: reference to a Team instance
        :param nhl_id: the ID of this team as known to NHL.com
        :param url: (optional) url to use to get the data for this object
        :param content: (optional) content for this object instance
        """
        self.url = ''
        self.name = ''
        self.content = {}
        self.nhl_id = nhl_id
        if url is not None:
            self.url = url
        else:
            if self.nhl_id:
                self.url = self.base_url + 'teams/{}'.format(self.nhl_id)
            else:
                self.url = self.base_url + 'teams'
        if content is not None:
            self.content = content
        else:
            self.content = get_json_data(self.url)

        if self.nhl_id and self.content and 'teams' in self.content:
            if 'name' in self.content['teams'][0]:
                self.name = self.content['teams'][0]['name']

    def get_ext_url(self, *modifiers, **kwargs):
        """ get extra stats url's """
        sep = '?'
        suffix = ''
        url = self.url + '/'
        if kwargs and 'season' in kwargs and kwargs['season']:
            suffix = '&season={}{}'.format(kwargs['season'], kwargs['season'] + 1)
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

    def load_ext_url(self, *modifiers, **kwargs):
        """ load the values from the extra data specified """
        url = self.get_ext_url(*modifiers, **kwargs)
        self.content = get_json_data(url)


def parse_args():
    """
    Parse the options from the command line

    :return: The options as a dictionary
    """
    description = 'Use the nhlapi/Team class to retrieve information about a team in the NHL.'
    epilog = 'Example use: team.py 22 --log team.log --humanReadable --teamStats --year=1980'

    # Standard options for each nhlapi interface
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--humanReadable', help='output in easier to read format for users',
                        action='store_true')
    parser.add_argument(
        '--log', default='/dev/null', type=str,
        help='the file where the output should be written')

    # Optional user supplied values
    parser.add_argument('--teamId', help='get data for a specific team ID', type=int)
    parser.add_argument('--year', help='the year to retrieve data for', type=int)

    # The data available from this api:
    for stat in Team.STATS:
        parser.add_argument('--' + stat, help='retrieve ' + stat + ' data', action='store_true')

    args = parser.parse_args()

    if args.log:
        log_format = '%(asctime)s %(levelname)s: %(message)s'
        logging.basicConfig(filename=args.log,
                            format=log_format,
                            level=logging.DEBUG)

    team = Team(args.teamId)
    if not team:
        print('team with id: {} not found'.format(args.teamId))
        return args

    args_vars = vars(args)
    for arg in args_vars:
        if arg in Team.STATS and args_vars[arg]:
            if args.year:
                team.load_ext_url(Team.STATS[arg], season=args.year)
            else:
                team.load_ext_url(Team.STATS[arg])

            if args.humanReadable:
                output = json.dumps(team.content, indent=1)
            else:
                output = team.content
            print(output)

    result = 'retrieved data for id: {}'.format(args.teamId)

    info(result)

    return args


if __name__ == '__main__':
    #
    # year = 1981
    # team_id = 22                  # Edmonton Oilers
    parse_args()
