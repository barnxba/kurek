# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing downloadable items

Each item available is represented with a JSON object. These classes make use
of the JSON representation and add different properties and methods to make
downloading them easier.
"""

import os

from yarl import URL

from kurek import config
from kurek.session import Session


class UserItem:
    """Base class for downloadable items
    """

    def __init__(self, item_type, json, info):
        self.type = item_type
        self.json = json
        self.info = info

    @property
    def url(self):
        """Download URL
        """

        return str()

    @property
    def owner(self):
        """Owner's profile name
        """

        return self.json['nick']

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

        template = config.save_template
        return template.replace('%d', config.save_dir) \
                       .replace('%t', self.type) \
                       .replace('%p', self.owner)

    async def _fetch_json(self, session: Session):
        _ = (session)
        return {}

    async def fetch(self, session: Session):
        """Fetch JSON data

        Args:
            session (Session): http request session
        """

        json = await self._fetch_json(session)
        self.info = json['item']

    async def download(self, session: Session):
        """Download item

        Args:
            session (Session): http request session
        """

        path = os.path.join(self.savepath, self.filename)
        if os.path.exists(path):
            print(f'File {path} exists. Skipping.')
            return
        await session.download(self.url, path)
        print(f'Downloaded {self.type}: {path}')


class Photo(UserItem):
    """Represents a downloadable photo
    """

    def __init__(self, json):
        """Create a new Photo object using JSON representation

        Args:
            json (str): JSON object representing a single photo
        """

        super().__init__('photo', json, None)

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

    async def _fetch_json(self, session: Session):
        return await session.get_photo_info(self.json['data'],
                                            self.json['lData'])


class Video(UserItem):
    """Represents a downloadable video
    """

    def __init__(self, json):
        """Create a new Video object using JSON representation

        Args:
            json (str): JSON object representing a single video
        """

        super().__init__('video', json, None)

    @property
    def url(self):
        if self.info is None:
            return None
        key = 'mp4480' if 'mp4480' in self.info else 'mp4'
        url = self.info[key]
        return url

    async def _fetch_json(self, session: Session):
        return await session.get_video_info(self.json['data'],
                                            self.json['lData'])

    async def download(self, session: Session):
        await self.fetch(session)
        await super().download(session)
