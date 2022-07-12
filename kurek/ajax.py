import yarl
import requests

from . import config


class Balancer:
    def __init__(self):
        self._urls = None
        self._api_urls = tuple((
            yarl.URL.build(scheme=config.scheme,
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
                for _ in range (0, config.max_api_requests):
                    yield url

    def next_url(self):
        return next(self._urls)


class Ajax:
    def __init__(self):
        self._balancer = Balancer()

    def get_request(self, params):
        url = self._balancer.next_url()
        with requests.get(url,
                          headers=config.request_headers,
                          params=params) as response:
            response.raise_for_status()
        return response.json()

    @staticmethod
    def build_command_login_json(email, password, ltoken):
        return {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
