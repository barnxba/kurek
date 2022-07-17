# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing JSON objects

Each item available is represented with a JSON object. These classes make use
of the JSON representation and add different properties and methods to make
downloading them easier.
"""

import os
import asyncio
import itertools

from yarl import URL

from kurek import config
from kurek.session import Session


class Item:
    """"Base JSON item class
    """

    def __init__(self, json=None):
        """Create a JSON item

        Args:
            json (dict, optional): JSON object. Defaults to None.
        """

        self.json = json

    @property
    def owner(self):
        """Owner's profile name
        """

        return self.json['nick']

    async def fetch(self, session: Session):
        """Fetch JSON data from server using http session

        Args:
            session (Session): http request session
        """

        _ = (session)


class Collection(list):
    """Collects JSON items into a list
    """

    async def fetch(self, session: Session):
        """Fetch JSON of all items

        Args:
            session (Session): http request session
        """

        tasks = (item.fetch(session) for item in self)
        await asyncio.gather(*tasks)


class UrlItem(Item):
    """Base class for JSON downloadable items
    """

    def __init__(self, json=None, info_json=None, item_type: str = None):
        """Create a downloadable item representation

        Args:
            json (dict, optional): item JSON. Defaults to None.
            info_json (dict, optional): item info JSON. Defaults to None.
            item_type (str, optional): item type string. Defaults to None.
        """

        super().__init__(json)
        self.info = info_json
        self.type = item_type

    @property
    def url(self):
        """Download URL - override this function
        """

        return None

    @property
    def description(self):
        """Description string
        """

        return self.json['description']

    @property
    def title(self):
        """Title string
        """

        return self.json['title']

    @property
    def uid(self):
        """Unique ID hash
        """

        return self.json['lData']

    @property
    def ext(self):
        """File extension
        """

        return URL(self.url).parts[-1][-3:]

    @property
    def filename(self):
        """File name used for saving the file - based on configured template
        """

        template = config.name_template
        subs = {
            '%t': self.title,
            '%h': self.uid,
            '%e': self.ext,
            '%d': self.description,
            '%o': self.owner
        }
        for key, value in subs.items():
            if not value:
                value = '_'
            template = template.replace(key, value)
        return template

    @property
    def savepath(self):
        """Directory path where the file will be saved
        """

        template = config.path_template
        return template.replace('%d', config.root_dir) \
                       .replace('%t', self.type) \
                       .replace('%p', self.owner)

    async def download(self, session: Session):
        """Download item

        Args:
            session (Session): http request session
        """

        await self.fetch(session)
        path = os.path.join(self.savepath, self.filename)
        if os.path.exists(path):
            print(f'File {path} exists. Skipping.')
            return
        await session.download(self.url, path)
        print(f'Downloaded {self.type}: {path}')


class InfoItem(Item):
    """Base class for info items
    """

    def __init__(self, data, ldata):
        """Base class for info item JSON

        Args:
            data (str): data hash from parent JSON item
            ldata (_type_): lData hash from parent JSON item
        """

        super().__init__()
        self._data = data
        self._ldata = ldata


class PhotoInfo(InfoItem):
    """Detailed info JSON representation for photos
    """

    async def fetch(self, session: Session):
        """Fetch JSON data using http session
        """

        json = await session.get_photo_info(self._data,
                                            self._ldata)
        self.json = json['item']


class Photo(UrlItem):
    """Represents a photo
    """

    def __init__(self, json):
        """Create a new Photo object using JSON representation

        Args:
            json (str): JSON object representing a single photo
        """

        super().__init__(json, None, 'photo')

    @property
    def url(self):
        src_keys = {key: key
                    for key in self.json if key.startswith('src')}
        size2key = {int("".join(c for c in value if c.isdecimal())): key
                    for key, value in src_keys.items()}
        sorted_sizes = sorted(list(size2key.keys()), reverse=True)
        key = size2key[sorted_sizes[0]]
        url = self.json[key]
        return url

    async def fetch(self, session: Session):
        self.info = PhotoInfo(self.json['data'],
                              self.json['lData'])


class VideoInfo(InfoItem):
    """Detailed info JSON representation for videos
    """

    async def fetch(self, session: Session):
        json = await session.get_video_info(self._data,
                                            self._ldata)
        self.json = json['item']


class Video(UrlItem):
    """Represents a downloadable video
    """

    def __init__(self, json):
        """Create a new Video object using JSON representation

        Args:
            json (str): JSON object representing a single video
        """

        super().__init__(json, None, 'video')

    @property
    def url(self):
        if self.info is None:
            return None
        key = 'mp4480' if 'mp4480' in self.info.json else 'mp4'
        url = self.info.json[key]
        return url

    async def fetch(self, session: Session):
        self.info = VideoInfo(self.json['data'],
                              self.json['lData'])
        await self.info.fetch(session)


class Profile(Item):
    """Represents a profile
    """

    def __init__(self, nick):
        """Create a new Profile represented by a nick

        Args:
            nick (str): profile name
        """

        super().__init__()
        self._nick = nick
        self._photos = None
        self._videos = None

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

        self.json = await session.get_profile(self.nick)

    async def fetch_photos(self, session: Session):
        """Fetch photo collection JSON data using http request session

        Args:
            session (Session): request session

        Returns:
            list: list of Photo objects
        """

        json = await session.get_profile_photos(self.nick)
        self._photos = Collection([Photo(item)
                                   for item in json['items']
                                   if item['access']])
        return self._photos

    async def fetch_videos(self, session: Session):
        """Fetch video collection JSON data using http request session

        Args:
            session (Session): http request session

        Returns:
            list: list of Video objects
        """

        json = await session.get_profile_videos(self.nick)
        self._videos = Collection([Video(item)
                                   for item in json['items']
                                   if item['access']])
        return self._videos

    async def download(self, session: Session):
        """Download media and save to file

        Args:
            session (Session): http request session
        """

        tasks = []
        if not config.only_videos:
            tasks.append(self.fetch_photos(session))
        if not config.only_photos:
            tasks.append(self.fetch_videos(session))
        await asyncio.gather(*tasks)

        if config.only_photos:
            tasks = (photo.download(session) for photo in self._photos)
        elif config.only_videos:
            tasks = (video.download(session) for video in self._videos)
        else:
            tasks = itertools.chain(
                (photo.download(session) for photo in self._photos),
                (video.download(session) for video in self._videos))
        await asyncio.gather(*tasks)
