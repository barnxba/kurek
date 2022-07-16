# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md

from yarl import URL

from . import config


class Balancer:
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
        return self._url_generator()

    def _url_generator(self):
        while True:
            for url in self._api_urls:
                for _ in range (0, config.max_server_requests):
                    yield url

    def next_url(self):
        return str(next(self._urls))


class Command:
    def __init__(self, url):
        self._url = url

    def _get_url(self, params):
        return str(URL(self._url) % params)

    def login(self, email, password, ltoken):
        params = {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
        return self._get_url(params)

    def get_profile_photos(self, nick, token):
        params = {
            'command': 'getProfilePhotos',
            'nick': nick,
            'actPath': f'/{nick}/photos',
            'token': token
        }
        return self._get_url(params)

    def get_profile_videos(self, nick, token):
        params = {
            'command': 'getProfileVideos',
            'nick': nick,
            'actPath': f'/{nick}/videos',
            'token': token
        }
        return self._get_url(params)

    def get_video_info(self, data, l_data, token):
        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/video/{l_data}',
            'token': token
        }
        return self._get_url(params)

    def get_photo_info(self, data, l_data, token):
        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/photo/{l_data}',
            'token': token
        }
        return self._get_url(params)


class Ajax:
    def __init__(self):
        self._balancer = Balancer()

    @property
    def _url(self):
        return self._balancer.next_url()

    def login(self, email, password, ltoken):
        return Command(self._url).login(email, password, ltoken)

    def get_profile_photos(self, nick, token):
        return Command(self._url).get_profile_photos(nick, token)

    def get_profile_videos(self, nick, token):
        return Command(self._url).get_profile_videos(nick, token)

    def get_photo_info(self, data, ldata, token):
        return Command(self._url).get_photo_info(data, ldata, token)

    def get_video_info(self, data, ldata, token):
        return Command(self._url).get_video_info(data, ldata, token)
