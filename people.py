#!/usr/bin/env python3

"""
    People class for the nhlapi package
"""

import sys
import json
import argparse
from nhlapi import get_json_data


class People:
    """
    People class for the nhlapi package
    """

    STATS = {'yearByYear': 0,
             'yearByYearRank': 1,
             'yearByYearPlayoffs': 2,
             'yearByYearPlayoffsRank': 3,
             'careerRegularSeason': 4,
             'careerPlayoffs': 5,
             'gameLog': 6,
             'playoffGameLog': 7,
             'vsTeam': 8,
             'vsTeamPlayoffs': 9,
             'vsDivision': 10,
             'vsDivisionPlayoffs': 11,
             'vsConference': 12,
             'vsConferencePlayoffs': 13,
             'byMonth': 14,
             'byMonthPlayoffs': 15,
             'byDayOfWeek': 16,
             'byDayOfWeekPlayoffs': 17,
             'homeAndAway': 18,
             'homeAndAwayPlayoffs': 19,
             'winLoss': 20,
             'winLossPlayoffs': 21,
             'onPaceRegularSeason': 22,
             'regularSeasonStatRankings': 23,
             'playoffStatRankings': 24,
             'goalsByGameSituation': 25,
             'goalsByGameSituationPlayoffs': 26,
             'statsSingleSeason': 27,
             'statsSingleSeasonPlayoffs': 28}

    modifiers = {}
    for key, value in STATS.items():
        modifiers[value] = 'stats=' + key

    base_url = 'https://statsapi.web.nhl.com/api/v1/'

    def __init__(self, nhl_id, url=None, content=None):
        """
        initialize this Player object

        :param self: reference to a Player instance
        :param nhl_id: the ID of this player as known to NHL.com
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
            self.url = self.base_url + 'people/{}'.format(nhl_id)
        if content is not None:
            self.content = content
        else:
            self.content = get_json_data(self.url)

        if self.content and 'people' in self.content and 'fullName' in self.content['people'][0]:
            self.name = self.content['people'][0]['fullName']

    def get_ext_url(self, *modifiers, **kwargs):
        """ get extra stats url's """
        sep = '?'
        suffix = ''
        url = self.url + '/stats'
        if kwargs:
            if 'season' in kwargs and kwargs['season']:
                suffix = '&season={}{}'.format(kwargs['season'], kwargs['season'] + 1)
                if 'start_year' in kwargs and kwargs['start_year']:
                    if 'end_year' in kwargs and kwargs['end_year']:
                        suffix = '&startYear={}&endYear={}'.format(
                            kwargs['start_year'], kwargs['end_year'])
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
    description = 'Use the nhlapi/People class to retrieve information about a player in the NHL'
    epilog = 'Example use: people.py 8447400 --winLoss --year=1983'

    # Standard options for each nhlapi interface
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--humanReadable',
                        help='output in easier to read format for users', action='store_true')
    parser.add_argument(
        '--log', default='/dev/null', type=argparse.FileType('a'),
        help='the file where the output should be written')

    # Optional user supplied values
    parser.add_argument('playerId', help='the player ID', type=int)
    parser.add_argument('-y', '--year', metavar='year', help='the year to retrieve', type=int)
    parser.add_argument('-s', '--startYear', metavar='start year',
                        help='the starting year to retrieve', type=int)
    parser.add_argument('-e', '--endYear', metavar='end year',
                        help='the ending year to retrieve', type=int)

    # The data available from this api:
    for stat in People.STATS:
        parser.add_argument('--' + stat, help='retrieve ' + stat + ' data', action='store_true')

    args = parser.parse_args()
    player = People(args.playerId)
    if not player:
        print('player with id: {} not found'.format(args.playerId))
        return args

    args_vars = vars(args)
    for arg in args_vars:
        if arg in People.STATS and args_vars[arg]:
            if args.year:
                player.load_ext_url(People.STATS[arg], season=args.year)
            elif args.startYear and args.endYear:
                player.load_ext_url(People.STATS[arg], start_year=args.startYear,
                                    end_year=args.endYear)
            else:
                player.load_ext_url(People.STATS[arg])

            if args.humanReadable and player.content:
                output = json.dumps(player.content['stats'], indent=1)
            else:
                output = player.content
            print(output)

    result = 'retrieved data for id: {} ({})'.format(args.playerId, player.name)

    args.log.write('%s\n' % result)
    args.log.close()
    return args


if __name__ == '__main__':
    #
    # 8447400 playerPk
    parse_args()
