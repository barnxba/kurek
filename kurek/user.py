from .site import Site


class User:
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._nick = None
        self._token = None

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
        command_json = site.build_command_login_json(self.email,
                                                     self.password,
                                                     ltoken)
        response_json = site.ajax_get_request(command_json)
        self._token = response_json['token']
        self._nick = response_json['loggedUser']['nick']

        print(f'User {self.nick} logged in. [token: {self.token}]')
