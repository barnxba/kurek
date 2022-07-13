import os
import asyncio

import aiofiles

from . import config
from .site import Site
from .ajax import Ajax
from .photo import generator as photo_generator


class User:
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._nick = None
        self._token = None
        self._ajax = None
        self._photo_register = dict()
        self._video_register = dict()

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def nick(self):
        return self._nick

    @property
    def token(self):
        return self._token

    async def login(self, session):
        site = Site()
        ltoken = site.get_tag_property_by_id('zbiornik-ltoken')
        ajax = Ajax(session)
        await ajax.login(self.email,
                         self.password,
                         ltoken,
                         self._callback_login)

    async def _callback_login(self, *args):
        caller, json = args
        self._token = json['token']
        self._nick = json['loggedUser']['nick']
        self._ajax = caller
        print(f'User {self.nick} logged in. [token: {self.token}]')

    async def download_media(self, profiles):
        photo_tasks = (
            self._ajax.get_profile_photos(nick,
                                          self._token,
                                          self._callback_get_profile_photos)
            for nick in profiles)
        await asyncio.gather(*photo_tasks)

    async def _callback_get_profile_photos(self, *args):
        caller, json = args
        nick = json['items'][0]['nick']
        count = len(json['items'])
        print(f'Downloaded picture info for: [{nick}]')

        register = photo_generator(
            (item for item in json['items'] if item['access']))
        self._photo_register.update({ photo.url: photo for photo in register})

        photos = photo_generator(
            (item for item in json['items'] if item['access']))
        urls = (photo.url for photo in photos)
        tasks = (
            self._ajax.download(url, self._callback_write_photo)
            for url in urls
        )
        await asyncio.gather(*tasks)
        print(f'Finished downloading {count} pictures for [{nick}]')


    async def _callback_write_photo(self, *args):
        caller, url, data = args
        photo = self._photo_register[url]
        path = os.path.join(config.save_dir, photo.nick, 'photos')
        if not os.path.exists(path):
            os.makedirs(path)

        filename = os.path.join(path, f'{photo.id_hash}.{photo.ext}')
        print(f'Downloaded {self._photo_register[url].title}')
        async with aiofiles.open(filename, 'wb') as file:
            await file.write(data)
        del self._photo_register[url]
        print(f'Saved: {filename}')