import yarl
import requests
from bs4 import BeautifulSoup


class Balancer:
    def __init__(self):
        self._max_requests = 5
        self._urls = None
        servers = ('dzesika', 'brajanek', 'vaneska', 'denisek')
        api_root = 'zbiornik.com/ajax/'
        self._api_urls = tuple((
            yarl.URL.build(scheme='https', host=f'{server}.{api_root}')
            for server in servers
            ))
        self._urls = self._get_url_generator()

    def _get_url_generator(self):
        if self._urls:
            return self._urls
        return self._url_generator()

    def _url_generator(self):
        while True:
            for url in self._api_urls:
                for _ in range (0, self._max_requests):
                    yield url

    def next_url(self):
        return next(self._urls)


class Site:
    def __init__(self):
        self._url = 'https://zbiornik.com'
        self._balancer = Balancer()

    @property
    def _request_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        return headers

    def _get_html_text(self):
        with requests.get(self._url,
                          headers=self._request_headers) as response:
            response.raise_for_status()
        return response.text

    def get_tag_property_by_id(self, tag_id, property='value'):
        soup = BeautifulSoup(self._get_html_text(), 'html.parser')
        return soup.find(id=tag_id)[property]

    def ajax_get_request(self, params):
        url = self._balancer.next_url()
        with requests.get(url,
                          headers=self._request_headers,
                          params=params) as response:
            response.raise_for_status()
        return response.json()

    def build_command_login_json(self, email, password, ltoken):
        return {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
