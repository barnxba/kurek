# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md

import asyncio

from kurek import config
from kurek.session import Session
from kurek.items import Photo, Video


class Profile:
    def __init__(self, nick):
        self._nick = nick
        self._photos = list()
        self._videos = list()

    @property
    def nick(self):
        return self._nick

    @property
    def photos(self):
        return self._photos

    @property
    def videos(self):
        return self._videos

    async def fetch(self, session: Session):
        tasks = (self.fetch_photos(session), self.fetch_videos(session))
        await asyncio.gather(*tasks)

    async def fetch_photos(self, session: Session):
        json = await session.get_profile_photos(self.nick)
        self._photos = list((Photo(item)
                             for item in json['items'] if item['access']))
        return self._photos

    async def fetch_videos(self, session: Session):
        json = await session.get_profile_videos(self.nick)
        self._videos = list((Video(item)
                             for item in json['items'] if item['access']))
        return self._videos

    async def download(self, session: Session):
        await self.fetch(session)
        photo_tasks = (photo.download(session) for photo in self._photos)
        video_tasks = (video.download(session) for video in self._videos)
        if config.only_photos:
            await asyncio.gather(*photo_tasks)
        elif config.only_videos:
            await asyncio.gather(*video_tasks)
        else:
            await asyncio.gather(*photo_tasks, *video_tasks)
