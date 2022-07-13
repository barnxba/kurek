from .site import Site
from .ajax import Ajax


class User:
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._nick = None
        self._token = None
        self._ajax = None

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

    def _callback_login(self, caller, json):
        self._token = json['token']
        self._nick = json['loggedUser']['nick']
        self._ajax = caller
        print(f'User {self.nick} logged in. [token: {self.token}]')

    async def download_media(self, profiles):
        await self._ajax.get_profile_photos(profiles,
                                            self._token,
                                            self._callback_get_profile_photos)

    def _callback_get_profile_photos(self, caller, json):
        print(f"Downloaded pictures of: {json['items'][0]['nick']}")
