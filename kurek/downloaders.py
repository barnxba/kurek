# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""A variety of downloader classes

Downloader classes take in profile data or top list data and then start
the downloads concurrently.
"""

import asyncio

from kurek import json
from kurek.http import Session


# TODO: use proper interface (virtual class)
class Downloader:
    """Base Downloader class
    """

    async def download(self, session: Session):
        """Download method - override in child

        Args:
            session: http request session
        """

        _ = (session)


class ProfileDownloader(Downloader):
    """Downloads media from a collection of profiles
    """

    def __init__(self, nicks):
        """Create a new downloader

        Args:
            nicks (Iterable): a list of profile names
        """

        self._nicks = nicks

    async def download(self, session: Session, photos=True, videos=True):
        """Start downloading data

        Args:
            session (Session): http session
            photos (bool, optional): download photos. Defaults to True.
            videos (bool, optional): download videos. Defaults to True.
        """

        profiles = (json.Profile(nick) for nick in self._nicks)
        tasks = (self._profile_task(profile, session, photos, videos)
                 for profile in profiles)
        await asyncio.gather(*tasks)

    async def _photo_task(self, photo: json.Photo, session: Session):
        await photo.download(session)

    async def _video_task(self, video: json.Video, session: Session):
        await video.fetch(session)
        await video.download(session)

    async def _profile_task(self,
                            profile: json.Profile,
                            session: Session,
                            photos: bool,
                            videos: bool):
        photo_tasks = []
        video_tasks = []

        if photos:
            await profile.photos.fetch(session)
            photo_tasks = (self._photo_task(photo, session)
                           for photo in profile.photos.items)
        if videos:
            await profile.videos.fetch(session)
            video_tasks = (self._video_task(video, session)
                           for video in profile.videos.items)

        await asyncio.gather(*photo_tasks, *video_tasks)
