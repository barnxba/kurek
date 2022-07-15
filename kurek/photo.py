import os
from yarl import URL

from . import config
from .session import Session


class Photo:
    def __init__(self, json):
        self.entry = json
        self.json = None

    @property
    def url(self):
        src_keys = {key: key
                    for key in self.entry if key.startswith('src')}
        size2key = {int("".join(c for c in value if c.isdecimal())): key
                    for key, value in src_keys.items()}
        sorted_sizes = sorted(list(size2key.keys()), reverse=True)
        key = size2key[sorted_sizes[0]]
        url = self.entry[key]
        return url

    @property
    def owner(self):
        return self.entry['nick']

    @property
    def title(self):
        return self.entry['title']

    @property
    def uid(self):
        return self.entry['lData']

    @property
    def filename(self):
        prefix = f'{self.title}_' if self.title else ''
        return f'{prefix}{self.uid}.{self.ext}'

    @property
    def ext(self):
        return URL(self.url).parts[-1][-3:]

    async def fetch(self, session: Session):
        json = await session.get_photo_info(self.entry['data'],
                                            self.entry['lData'])
        self.json = json['item']

    async def download(self, session: Session):
        path = f'{config.save_dir}/{self.owner}/photo/{self.filename}'
        if os.path.exists(path):
            print(f'File {path} exists. Skipping.')
            return
        await session.download(self.url, path)
        print(f'Downloaded photo: {path}')
