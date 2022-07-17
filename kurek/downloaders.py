# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""A variety of downloader classes

Downloader classes take in profile data or top list data and then start
the downloads concurrently.
"""

import asyncio
import itertools

from kurek import json
from kurek.http import Session


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
        tasks = (self._download_profile(profile, session, photos, videos)
                 for profile in profiles)
        await asyncio.gather(*tasks)

    async def _download_photo(self, photo: json.Photo, session: Session):
        await photo.download(session)

    async def _download_video(self, video: json.Video, session: Session):
        await video.fetch(session)
        await video.download(session)

    async def _download_profile(self,
                                profile: json.Profile,
                                session: Session,
                                photos: bool,
                                videos: bool):
        if photos:
            await profile.photos.fetch(session)
        if videos:
            await profile.videos.fetch(session)

        photo_tasks = (self._download_photo(photo, session)
                       for photo in profile.photos.items)
        video_tasks = (self._download_video(video, session)
                       for video in profile.videos.items)

        await asyncio.gather(*itertools.chain(photo_tasks, video_tasks))
