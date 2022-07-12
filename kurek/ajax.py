from .requests import RequestUrl
from .balancer import Balancer
from .session import Session


class Ajax:
    def __init__(self):
        self._balancer = Balancer()

    def url(self):
        return self._balancer.next_url()

    def login(self, email, password, ltoken):
        url = RequestUrl(self.url()).login(email, password, ltoken)
        return Session().run(self._get, url)

    def get_profile_photos(self, token, nick):
        url = RequestUrl(self.url()).get_profile_photos(token, nick)
        return Session().run(self._get, url)

    def get_profile_videos(self, token, nick):
        url = RequestUrl(self.url()).get_profile_videos(token, nick)
        return Session().run(self._get, url)

    async def _get(self, session, url):
        async with session.get(url) as response:
            response.raise_for_status()
            json = await response.json(content_type=None)
        return json
