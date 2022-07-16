# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md

import os

from yarl import URL

from kurek import config
from kurek.session import Session


class _UserItemJson:
    def __init__(self, entry, details):
        self.entry = entry
        self.details = details


class UserItem:
    def __init__(self, type, entry, details):
        self.type = type
        self.json = _UserItemJson(entry, details)

    @property
    def url(self):
        return str()

    @property
    def owner(self):
        return self.json.entry['nick']

    @property
    def description(self):
        return self.json.entry['description']

    @property
    def title(self):
        return self.json.entry['title']

    @property
    def uid(self):
        return self.json.entry['lData']

    @property
    def ext(self):
        return URL(self.url).parts[-1][-3:]

    @property
    def filename(self):
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
        template = config.save_template
        return template.replace('%d', config.save_dir) \
                       .replace('%t', self.type) \
                       .replace('%p', self.owner)

    async def _fetch_json(self, session: Session):
        return dict()

    async def fetch(self, session: Session):
        json = await self._fetch_json(session)
        self.json.details = json['item']

    async def download(self, session: Session):
        path = os.path.join(self.savepath, self.filename)
        if os.path.exists(path):
            print(f'File {path} exists. Skipping.')
            return
        await session.download(self.url, path)
        print(f'Downloaded {self.type}: {path}')


class Photo(UserItem):
    def __init__(self, json):
        super(Photo, self).__init__('photo', json, None)

    @property
    def url(self):
        src_keys = {key: key
                    for key in self.json.entry if key.startswith('src')}
        size2key = {int("".join(c for c in value if c.isdecimal())): key
                    for key, value in src_keys.items()}
        sorted_sizes = sorted(list(size2key.keys()), reverse=True)
        key = size2key[sorted_sizes[0]]
        url = self.json.entry[key]
        return url

    async def _fetch_json(self, session: Session):
        return await session.get_photo_info(self.json.entry['data'],
                                            self.json.entry['lData'])


class Video(UserItem):
    def __init__(self, json):
        super(Video, self).__init__('video', json, None)

    @property
    def url(self):
        if self.json.details is None:
            return None
        key = 'mp4480' if 'mp4480' in self.json.details else 'mp4'
        url = self.json.details[key]
        return url

    async def _fetch_json(self, session: Session):
        return await session.get_video_info(self.json.entry['data'],
                                            self.json.entry['lData'])

    async def download(self, session: Session):
        await self.fetch(session)
        await super().download(session)
