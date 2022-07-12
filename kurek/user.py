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

    def login(self):
        site = Site()
        ltoken = site.get_tag_property_by_id('zbiornik-ltoken')
        ajax = Ajax()
        command_json = ajax.build_command_login_json(self.email,
                                                     self.password,
                                                     ltoken)
        response_json = ajax.get_request(command_json)
        self._token = response_json['token']
        self._nick = response_json['loggedUser']['nick']

        self._ajax = ajax
        print(f'User {self.nick} logged in. [token: {self.token}]')
