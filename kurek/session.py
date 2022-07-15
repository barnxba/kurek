import os
import asyncio

import aiofiles
from aiohttp import ClientSession

from .ajax import Ajax
from .user import User
from .site import Site


class Session:
    def __init__(self, api_limit=0, download_limit=0, headers=None):
        self._client: ClientSession = None
        self._ajax: Ajax = Ajax()
        self._user: User = None
        self._api_limit = api_limit
        self._download_limit = download_limit
        self._api_limiter = None
        self._download_limiter = None
        self._headers = headers

    async def get(self, url):
        async with self._api_limiter:
            async with self._client.get(url) as response:
                response.raise_for_status()
                json = await response.json(content_type=None)
        return json

    async def download(self, url, path):
        async with self._download_limiter:
            async with self._client.get(url) as response:
                response.raise_for_status()
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                async with aiofiles.open(path, 'wb') as file:
                    async for data, _ in response.content.iter_chunks():
                        await file.write(data)

    async def start(self):
        self._client = ClientSession(headers=self._headers)
        self._api_limiter = asyncio.Semaphore(self._api_limit)
        self._download_limiter = asyncio.Semaphore(self._download_limit)

    async def close(self):
        await self._client.close()

    async def login(self, user: User):
        site = Site()
        ltoken = site.get_tag_property_by_id('zbiornik-ltoken')
        url = self._ajax.login(user.email, user.password, ltoken)
        json = await self.get(url)
        user.login(json)
        self._user = user

    async def get_profile_photos(self, nick):
        url = self._ajax.get_profile_photos(nick, self._user.token)
        return await self.get(url)

    async def get_profile_videos(self, nick):
        url = self._ajax.get_profile_videos(nick, self._user.token)
        return await self.get(url)

    async def get_photo_info(self, data, ldata):
        url = self._ajax.get_photo_info(data, ldata, self._user.token)
        return await self.get(url)

    async def get_video_info(self, data, ldata):
        url = self._ajax.get_video_info(data, ldata, self._user.token)
        return await self.get(url)
