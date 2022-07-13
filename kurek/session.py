from asyncio import Semaphore

from aiohttp import ClientSession


class Session:
    def __init__(self, api_limit=0, download_limit=0, headers=None):
        self._api_limit = api_limit
        self._download_limit = download_limit
        self._client = None
        self._api_semaphore = None
        self._download_semaphore = None
        self._headers = headers

    @property
    def client(self):
        return self._client

    @property
    def api_limiter(self):
        return self._api_semaphore

    @property
    def download_limiter(self):
        return self._download_semaphore

    async def start(self):
        self._client = ClientSession(headers=self._headers)
        self._api_semaphore = Semaphore(self._api_limit)
        self._download_semaphore = Semaphore(self._download_limit)

    async def close(self):
        await self._client.close()
