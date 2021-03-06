#!/usr/bin/env python3
"""
    Game class for the nhlapi package
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


class Game:
    """
    Game class for the nhlapi package
    """

    STATS = {'live': 0,
             'liveDiffTime': 1,
             'boxScore': 2,
             'lineScore': 3,
             'content': 4}

    modifiers = {STATS['live']: 'feed/live',
                 STATS['liveDiffTime']: '/feed/live/diffPatch',
                 STATS['boxScore']: 'boxscore',
                 STATS['lineScore']: 'linescore',
                 STATS['content']: 'content'}

    base_url = 'https://statsapi.web.nhl.com/api/v1/'

    def __init__(self, nhl_id, url=None, content=None):
        """
        initialize this Game object

        :param self: reference to a Game instance
        :param nhl_id: the ID of this game as known to NHL.com
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
            self.url = self.base_url + 'game/{}/linescore'.format(self.nhl_id)
        if content is not None:
            self.content = content
        else:
            self.content = get_json_data(self.url)

        if self.content and 'teams' in self.content:
            team_name1 = self.content['teams']['away']['team']['name']
            team_name2 = self.content['teams']['home']['team']['name']
            self.name = team_name1 + ' at ' + team_name2

    def get_ext_url(self, *modifiers, **kwargs):
        """ get extra stats url's """
        sep = '?'
        suffix = ''
        url = self.url + '/'
        if kwargs and 'diff_time' in kwargs and kwargs['diff_time']:
            suffix = '?startTimecode={}'.format(kwargs['diff_time'])
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
        url = self.get_ext_url(modifiers, **kwargs)
        self.content = get_json_data(url)


def parse_args():
    """
    Parse the options from the command line

    :return: The options as a dictionary
    """
    description = 'Use the nhlapi/Game class to retrieve information about a game in the NHL.'
    epilog = 'Example use: game.py 2018020131 --boxScore'

    # Standard options for each nhlapi interface
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--humanReadable', help='output in easier to read format for users',
                        action='store_true')
    parser.add_argument(
        '--log', default='/dev/null', type=str,
        help='the file where the output should be written')

    # Optional user supplied values
    parser.add_argument('gameId', help='the game ID', type=int)

    # The data available from this api:
    for stat in Game.STATS:
        parser.add_argument('--' + stat, help='retrieve ' + stat + ' data', action='store_true')

    args = parser.parse_args()

    if args.log:
        log_format = '%(asctime)s %(levelname)s: %(message)s'
        logging.basicConfig(filename=args.log,
                            format=log_format,
                            level=logging.DEBUG)

    game = Game(args.gameId)
    if not game:
        print('game with id: {} not found'.format(args.gameId))
        return args

    args_vars = vars(args)
    for arg in args_vars:
        if arg in Game.STATS and args_vars[arg]:
            if args.liveDiffTime:
                game.load_ext_url(Game.STATS[arg], diff_time=args.liveDiffTime)
            else:
                game.load_ext_url(Game.STATS[arg])

            if args.humanReadable:
                output = json.dumps(game.content, indent=1)
            else:
                output = game.content
            print(output)

    result = 'retrieved data for id: {}'.format(args.gameId)
    info(result)

    return args


if __name__ == '__main__':
    #
    # 2018020131 gamePk
    parse_args()
