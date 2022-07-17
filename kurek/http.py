# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing session, connection and user information

Main focus should be put on Session class. The rest of them are basically
helper classes to deal with session parameters.
"""

import os
import asyncio

import aiofiles
from yarl import URL
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from kurek import config
from kurek.ajax import Ajax


class User:
    """User information and login status
    """

    def __init__(self, email, password):
        """Create a new User with credentials

        Args:
            email (str): user's email
            password (str): user's password
        """

        self._email = email
        self._password = password
        self._nick = None
        self._token = None

    @property
    def email(self):
        """Email address

        Returns:
            str: account email address
        """

        return self._email

    @property
    def password(self):
        """Login password

        Returns:
            str: account password
        """

        return self._password

    @property
    def nick(self):
        """User's profile name

        Returns:
            str: profile name
        """

        return self._nick

    @property
    def token(self):
        """Session token

        Returns:
            str: session token
        """

        return self._token

    def login(self, json):
        """Use Login command JSON response to login user

        Args:
            json (dict): JSON response to Login AJAX request
        """

        self._token = json['token']
        self._nick = json['loggedUser']['nick']
        print(f'User {self.nick} logged in. [token: {self.token}]')


class Site:
    """Main site operations

    Used mainly to parse html and obtain the login token.
    """

    def __init__(self, client: ClientSession):
        """Create a new Site handler object

        Args:
            client (ClientSession): client for async http requests
        """

        self._url = str(URL.build(scheme=config.scheme,
                                  host=config.host))
        self._client = client

    async def _get_html_text(self):
        async with self._client.get(self._url) as response:
            response.raise_for_status()
            html = await response.text()
        return html

    async def get_tag_property_by_id(self, tag_id, field='value'):
        """Get value of a field from a tag represented by id

        Args:
            tag_id (str): html id of the tag
            field (str, optional): field name. Defaults to 'value'.

        Returns:
            str: tag field value
        """

        soup = BeautifulSoup(await self._get_html_text(), 'html.parser')
        return soup.find(id=tag_id)[field]


class Session:
    """Session information and http request handler / limiter
    """

    def __init__(self, api_limit=0, download_limit=0, headers=None):
        """Create a new Session with API and download limits

        Args:
            api_limit (int, optional): max API requests/session. Defaults to 0.
            download_limit (int, optional): max downloads. Defaults to 0.
            headers (dict, optional): dict with HTML headers. Defaults to None.
        """

        self._client: ClientSession = None
        self._ajax: Ajax = Ajax()
        self._user: User = None
        self._api_limit = api_limit
        self._download_limit = download_limit
        self._api_limiter = None
        self._download_limiter = None
        self._headers = headers

    async def get(self, url):
        """Make GET request

        Args:
            url (str): request URL

        Returns:
            dict: response JSON object
        """

        async with self._api_limiter:
            async with self._client.get(url) as response:
                response.raise_for_status()
                json = await response.json(content_type=None)
        return json

    async def download(self, url, path):
        """Download data and save to file

        Args:
            url (str): request URL
            path (path): file to save to
        """

        async with self._download_limiter:
            async with self._client.get(url) as response:
                response.raise_for_status()
                save_dir = os.path.dirname(path)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                async with aiofiles.open(path, 'wb') as file:
                    async for data, _ in response.content.iter_chunks():
                        await file.write(data)

    async def start(self):
        """Start the session and initialize synchronization primitives
        """

        self._client = ClientSession(headers=self._headers)
        self._api_limiter = asyncio.Semaphore(self._api_limit)
        self._download_limiter = asyncio.Semaphore(self._download_limit)

    async def close(self):
        """Close the session and do cleanup
        """

        await self._client.close()

    async def login(self, email, password):
        """Log the user in using credentials

        Args:
            email (str): account email
            password (str): account password
        """

        user = User(email, password)
        site = Site(self._client)
        ltoken = await site.get_tag_property_by_id('zbiornik-ltoken')
        url = self._ajax.login(user.email, user.password, ltoken)
        json = await self.get(url)
        user.login(json)
        self._user = user

    async def get_profile(self, nick):
        """Get JSON object representing a profile

        Args:
            nick (str): profile name

        Returns:
            dict: JSON object
        """

        url = self._ajax.get_profile(nick, self._user.token)
        return await self.get(url)

    async def get_profile_photos(self, nick):
        """Get JSON object representing profile's photo collection

        Args:
            nick (str): profile name

        Returns:
            dict: JSON object
        """

        url = self._ajax.get_profile_photos(nick, self._user.token)
        return await self.get(url)

    async def get_profile_videos(self, nick):
        """Get JSON object representing profile's video collection

        Args:
            nick (str): profile name

        Returns:
            dict: JSON object
        """

        url = self._ajax.get_profile_videos(nick, self._user.token)
        return await self.get(url)

    async def get_item_info(self, itype, data, ldata):
        """Get JSON object representing a single photo

        Args:
            itype (str): string representation of type ('photo'/'video')
            data (str): photo's data hash obtained from JSON
            ldata (str): photo's lData hash obtained from JSON

        Returns:
            dict: JSON object
        """

        url = self._ajax.get_item_info(itype, data, ldata, self._user.token)
        return await self.get(url)
