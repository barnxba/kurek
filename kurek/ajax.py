# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes for interacting with AJAX endpoints

Used to produce commands and urls that let the user contact the API
servers. Includes a Balancer class for limiting requests to a single server.
"""

from yarl import URL

from kurek import config


class Balancer:
    """Generate new base URL for API requests

    There is a number of API servers to choose from. This class takes care of
    remembering how many requests went to the last used server and switches
    to the next after producing a given number of requests.
    """

    def __init__(self):
        self._urls = None
        self._api_urls = tuple(
            (URL.build(scheme=config.scheme,
                       host=f'{server}.{config.host}{config.api_root}')
             for server in config.api_servers
             ))
        self._urls = self._get_url_generator()

    def _get_url_generator(self):
        if self._urls:
            return self._urls
        return self.url_generator()

    def url_generator(self):
        """Counts requests made and yields next AJAX server URL

        Yields:
            yarl.URL: server URL
        """

        while True:
            for url in self._api_urls:
                for _ in range(0, config.max_server_requests):
                    yield url

    def next_url(self):
        """Pop the next URL in line to be used with a request
        """

        return str(next(self._urls))


class Command:
    """Prepare URL for an AJAX command

    This class takes a base URL and adds parameters used with different
    AJAX commands. Final URL can be used to contact the API server.
    """

    def __init__(self, url):
        """AJAX command URL

        Args:
            url (str): base URL to add parameters to
        """

        self._url = url

    def _get_url(self, params):
        return str(URL(self._url) % params)

    def login(self, email, password, ltoken):
        """Build Login command URL

        Args:
            email (str): user's email
            password (str): user's password
            ltoken (str): login token obtained from main site

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
        return self._get_url(params)

    def get_profile(self, nick, token):
        """Build GetProfile command URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'getProfilePhotos',
            'nick': nick,
            'actPath': f'/{nick}/',
            'token': token
        }
        return self._get_url(params)

    def get_profile_photos(self, nick, token):
        """Build GetProfilePhotos command URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'getProfilePhotos',
            'nick': nick,
            'actPath': f'/{nick}/photos',
            'token': token
        }
        return self._get_url(params)

    def get_profile_videos(self, nick, token):
        """Build GetProfileVideos command URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'getProfileVideos',
            'nick': nick,
            'actPath': f'/{nick}/videos',
            'token': token
        }
        return self._get_url(params)

    def get_video_info(self, data, l_data, token):
        """Build GetItemInfo command URL specifying video as item type

        Args:
            data (str): 'data' item from video's JSON object
            l_data (str): 'lData' item from video's JSON object
            token (str): session token

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/video/{l_data}',
            'token': token
        }
        return self._get_url(params)

    def get_photo_info(self, data, l_data, token):
        """Build GetItemInfo command URL specifying photo as item type

        Args:
            data (str): 'data' item from photo's JSON object
            l_data (str): 'lData' item from photo's JSON object
            token (str): session token

        Returns:
            str: final request URL for command
        """

        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/photo/{l_data}',
            'token': token
        }
        return self._get_url(params)


class Ajax:
    """Create URLs for AJAX requests with the use of a balancer

    Creates request URLs for available commands using a balancer to switch
    after max number request has been made.
    """

    def __init__(self):
        self._balancer = Balancer()

    @property
    def _url(self):
        return self._balancer.next_url()

    def login(self, email, password, ltoken):
        """Dispense login request URL

        Args:
            email (str): user's email
            password (str): user's password
            ltoken (str): login token

        Returns:
            str: request URL
        """

        return Command(self._url).login(email, password, ltoken)

    def get_profile(self, nick, token):
        """Dispense GetProfile request URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            _type_: _description_
        """

        return Command(self._url).get_profile(nick, token)

    def get_profile_photos(self, nick, token):
        """Dispense GetProfilePhotos request URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            _type_: _description_
        """

        return Command(self._url).get_profile_photos(nick, token)

    def get_profile_videos(self, nick, token):
        """Dispense GetProfileVideos command URL

        Args:
            nick (str): profile name
            token (str): session token

        Returns:
            str: final request URL for command
        """

        return Command(self._url).get_profile_videos(nick, token)

    def get_photo_info(self, data, ldata, token):
        """Dispense GetItemInfo command URL specifying photo as item type

        Args:
            data (str): 'data' item from photo's JSON object
            l_data (str): 'lData' item from photo's JSON object
            token (str): session token

        Returns:
            str: final request URL for command
        """

        return Command(self._url).get_photo_info(data, ldata, token)

    def get_video_info(self, data, ldata, token):
        """Dispense GetItemInfo command URL specifying video as item type

        Args:
            data (str): 'data' item from video's JSON object
            l_data (str): 'lData' item from video's JSON object
            token (str): session token

        Returns:
            str: final request URL for command
        """

        return Command(self._url).get_video_info(data, ldata, token)
