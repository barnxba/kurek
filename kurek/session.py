import os
import asyncio
import logging

import aiofiles
from yarl import URL
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from . import config
from .ajax import Ajax


log = logging.getLogger('session')
log.setLevel(logging.INFO)


class User:
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._nick = None
        self._token = None
        log.debug(f'created user: {self._email}')

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def nick(self):
        return self._nick

    @property
    def token(self):
        return self._token

    def login(self, json):
        self._token = json['token']
        self._nick = json['loggedUser']['nick']
        log.info(f'User {self.nick} logged in. [token: {self.token}]')


class Site:
    def __init__(self, client):
        self._url = str(URL.build(scheme=config.scheme,
                                  host=config.host))
        self._client = client

    async def _get_html_text(self):
        async with self._client.get(self._url) as response:
            response.raise_for_status()
            html = await response.text()
        return html

    async def get_tag_property_by_id(self, tag_id, property='value'):
        soup = BeautifulSoup(await self._get_html_text(), 'html.parser')
        return soup.find(id=tag_id)[property]


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

        log.debug(f'api_limit: {self._api_limit}')
        log.debug(f'download_limit: {self._download_limit}')

    async def get(self, url):
        async with self._api_limiter:
            log.debug(f'acquired api_limiter')
            async with self._client.get(url) as response:
                response.raise_for_status()
                log.debug(f'get: [{response.status}] {url}')
                json = await response.json(content_type=None)
        log.debug(f'released api_limiter')
        return json

    async def download(self, url, path):
        async with self._download_limiter:
            log.debug(f'acquired download_limiter')
            async with self._client.get(url) as response:
                log.debug(f'download: [{response.status}] {url}')
                response.raise_for_status()
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                    log.debug(f'created dir: {dir}')
                async with aiofiles.open(path, 'wb') as file:
                    async for data, _ in response.content.iter_chunks():
                        await file.write(data)
                log.debug(f'created file: {path}')
        log.debug(f'released download_limiter')

    async def start(self):
        self._client = ClientSession(headers=self._headers)
        self._api_limiter = asyncio.Semaphore(self._api_limit)
        self._download_limiter = asyncio.Semaphore(self._download_limit)
        log.debug(f'session started')

    async def close(self):
        await self._client.close()
        log.debug(f'session closed')

    async def login(self, email, password):
        user = User(email, password)
        site = Site(self._client)
        ltoken = await site.get_tag_property_by_id('zbiornik-ltoken')
        log.debug(f'ltoken for {user.email}: {ltoken}')
        url = self._ajax.login(user.email, user.password, ltoken)
        json = await self.get(url)
        user.login(json)
        self._user = user

    async def get_profile_photos(self, nick):
        log.debug(f'get_profile_photos [{nick}]')
        url = self._ajax.get_profile_photos(nick, self._user.token)
        return await self.get(url)

    async def get_profile_videos(self, nick):
        log.debug(f'get_profile_videos [{nick}]')
        url = self._ajax.get_profile_videos(nick, self._user.token)
        return await self.get(url)

    async def get_photo_info(self, data, ldata):
        log.debug(f'get_photo_info [lData: {ldata}]')
        url = self._ajax.get_photo_info(data, ldata, self._user.token)
        return await self.get(url)

    async def get_video_info(self, data, ldata):
        log.debug(f'get_video_info [lData: {ldata}]')
        url = self._ajax.get_video_info(data, ldata, self._user.token)
        return await self.get(url)
