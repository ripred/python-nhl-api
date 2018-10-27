"""
nhl-api package
"""

import ssl
import json
import urllib
import urllib.request

# from nhlapi.team.team import Team
# from nhlapi.people.people import People
# from nhlapi.schedule.schedule import Schedule


def get_json_data(api_url):
    """
    retrieve the json data returned from the specified REST url
    :param api_url: the url to retrieve the data from
    :return: returns the json data as a string
    """

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    # ssl._create_default_https_context = ssl._create_unverified_context
    try:
        with urllib.request.urlopen(api_url, context=ssl_context) as url:
            http_info = url.info()
            raw_data = url.read().decode(http_info.get_content_charset())
            json_data = json.loads(raw_data)
            return json_data
    except urllib.error.HTTPError as e:
        print(e)
        return ''