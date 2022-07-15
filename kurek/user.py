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

    def login(self, json):
        self._token = json['token']
        self._nick = json['loggedUser']['nick']
        print(f'User {self.nick} logged in. [token: {self.token}]')
