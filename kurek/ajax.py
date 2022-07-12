from . import command
from .balancer import Balancer
from .session import Session


class Ajax:
    def __init__(self):
        self._balancer = Balancer()

    def login(self, email, password, ltoken):
        params = command.login(email, password, ltoken)
        return Session().run(self._get, params)

    async def _get(self, session, params):
        url = self._balancer.next_url()
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            json = await response.json(content_type=None)
        return json
