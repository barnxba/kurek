# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing registered profiles

Contains classes used to represent a profile registered on the site.
"""

import asyncio

from kurek import config
from kurek.session import Session
from kurek.items import Photo, Video


class Profile:
    """Represents a profile
    """

    def __init__(self, nick):
        """Create a new Profile represented by a nick

        Args:
            nick (str): profile name
        """

        self._nick = nick
        self._photos = []
        self._videos = []

    @property
    def nick(self):
        """Profile name

        Returns:
            str: profile name
        """

        return self._nick

    @property
    def photos(self):
        """List of photos

        Returns:
            list: list of Photo objects
        """

        return self._photos

    @property
    def videos(self):
        """List of videos

        Returns:
            list: list of Video objects
        """

        return self._videos

    async def fetch(self, session: Session):
        """Fetch profile JSON data using http request session

        Args:
            session (Session): request session
        """

        tasks = (self.fetch_photos(session), self.fetch_videos(session))
        await asyncio.gather(*tasks)

    async def fetch_photos(self, session: Session):
        """Fetch photo collection JSON data using http request session

        Args:
            session (Session): request session

        Returns:
            list: list of Photo objects
        """

        json = await session.get_profile_photos(self.nick)
        self._photos = list((Photo(item)
                             for item in json['items'] if item['access']))
        return self._photos

    async def fetch_videos(self, session: Session):
        """Fetch video collection JSON data using http request session

        Args:
            session (Session): http request session

        Returns:
            list: list of Video objects
        """

        json = await session.get_profile_videos(self.nick)
        self._videos = list((Video(item)
                             for item in json['items'] if item['access']))
        return self._videos

    async def download(self, session: Session):
        """Download media and save the file

        Args:
            session (Session): http request session
        """

        await self.fetch(session)
        photo_tasks = (photo.download(session) for photo in self._photos)
        video_tasks = (video.download(session) for video in self._videos)
        if config.only_photos:
            await asyncio.gather(*photo_tasks)
        elif config.only_videos:
            await asyncio.gather(*video_tasks)
        else:
            await asyncio.gather(*photo_tasks, *video_tasks)
