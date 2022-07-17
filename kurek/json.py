# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing JSON objects

Each item available is represented with a JSON object. These classes make use
of the JSON representation and add different properties and methods to make
downloading them easier.
"""

import os

from yarl import URL

from kurek import config
from kurek.http import Session


class Fetchable:
    """"Base class for fetchable JSON objects
    """

    def __init__(self, json=None):
        """Create a JSON item

        Args:
            json (dict, optional): JSON object. Defaults to None.
        """

        self.json = json

    async def fetch(self, session: Session):
        """Fetch JSON data from server using http session - override in child

        Args:
            session (Session): http request session
        """

        _ = (session)


class Info(Fetchable):
    """Base class for info items
    """

    def __init__(self, itype, data, ldata):
        """Base class for info item JSON

        Args:
            itype (str): type of item (photo/video)
            data (str): data hash from parent JSON item
            ldata (_type_): lData hash from parent JSON item
        """

        super().__init__()
        self._data = data
        self._ldata = ldata
        self._type = itype

    async def fetch(self, session: Session):
        """Fetch JSON data using http session

        Args:
            session (Session): http request session
        """

        json = await session.get_item_info(self._type,
                                           self._data,
                                           self._ldata)
        self.json = json['item']


class Item(Fetchable):
    """Base class for JSON downloadable items
    """

    def __init__(self, item_type, json):
        """Create a new item with additional info

        Args:
            item_type (str): item type string (photo/video)
            json (dict): JSON object representing basic item summary
        """

        super().__init__(json)
        self.type = item_type
        data, ldata = json['data'], json['lData']
        self.info = Info(self.type, data, ldata)

    @property
    def owner(self):
        """Item owner's nick
        """

        return self.json['nick']

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

    # TODO: Remove filename, savepath, download and move to separate class
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


class Photo(Item):
    """Represents a photo
    """

    def __init__(self, json):
        """Create a new Photo object using JSON representation

        Args:
            json (str): JSON object representing a single photo
        """

        super().__init__('photo', json)

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
        await self.info.fetch(session)


class Video(Item):
    """Represents a downloadable video
    """

    def __init__(self, json):
        """Create a new Video object using JSON representation

        Args:
            json (str): JSON object representing a single video
        """

        super().__init__('video', json)

    @property
    def url(self):
        if self.info is None:
            return None
        key = 'mp4480' if 'mp4480' in self.info.json else 'mp4'
        url = self.info.json[key]
        return url

    async def fetch(self, session: Session):
        await self.info.fetch(session)


class ProfilePhotos(Fetchable):
    """Collection of profile photos
    """

    def __init__(self, owner):
        """Create collection of profile photos

        Args:
            owner (str): profile name
        """

        super().__init__()
        self.owner = owner
        self.items = None

    async def fetch(self, session: Session):
        """Fetch collection JSON info

        Args:
            session (Session): http request session
        """

        json = await session.get_profile_photos(self.owner)
        self.json = json['items']
        self.items = [Photo(item) for item in json['items'] if item['access']]


class ProfileVideos(Fetchable):
    """Collection of profile videos
    """

    def __init__(self, owner):
        """Create collection of profile videos

        Args:
            owner (str): profile name
        """

        super().__init__()
        self.owner = owner
        self.items = None

    async def fetch(self, session: Session):
        """Fetch collection JSON info

        Args:
            session (Session): http request session
        """

        json = await session.get_profile_videos(self.owner)
        self.json = json['items']
        self.items = [Video(item) for item in json['items'] if item['access']]


class Profile(Fetchable):
    """JSON object of a profile
    """

    def __init__(self, nick):
        """Create new profile representation

        Args:
            nick (str): profile name
        """

        super().__init__()
        self._nick = nick
        self._photos = ProfilePhotos(self.nick)
        self._videos = ProfileVideos(self.nick)

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
        """Fetch JSON data using http session

        Args:
            session (Session): request session
        """

        json = await session.get_profile(self._nick)
        self.json = json['profile']
