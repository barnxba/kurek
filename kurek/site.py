import yarl
import requests
from bs4 import BeautifulSoup

from . import config


class Site:
    def __init__(self):
        self._url = yarl.URL.build(scheme=config.scheme,
                                   host=config.host)

    def _get_html_text(self):
        with requests.get(self._url,
                          headers=config.request_headers) as response:
            response.raise_for_status()
        return response.text

    def get_tag_property_by_id(self, tag_id, property='value'):
        soup = BeautifulSoup(self._get_html_text(), 'html.parser')
        return soup.find(id=tag_id)[property]
