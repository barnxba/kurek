import os
from yarl import URL

from . import config
from .session import Session


class Video:
    def __init__(self, json):
        self.entry = json
        self.json = None

    @property
    def url(self):
        if self.json is None:
            return None
        key = 'mp4480' if 'mp4480' in self.json else 'mp4'
        url = self.json[key]
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
        json = await session.get_video_info(self.entry['data'],
                                            self.entry['lData'])
        self.json = json['item']

    async def download(self, session: Session):
        await self.fetch(session)
        path = f'{config.save_dir}/{self.owner}/video/{self.filename}'
        if os.path.exists(path):
            print(f'File {path} exists. Skipping.')
            return
        await session.download(self.url, path)
        print(f'Downloaded video: {path}')
