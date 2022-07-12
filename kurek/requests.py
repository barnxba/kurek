from yarl import URL

class RequestUrl:
    def __init__(self, url):
        self._url = url

    def _build_url(self, params):
        return str(URL(self._url) % params)

    def login(self, email, password, ltoken):
        params = {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
        return self._build_url(params)

    def get_profile_photos(self, token, nick):
        params = {
            'command': 'getProfilePhotos',
            'nick': nick,
            'actPath': f'/{nick}/photos',
            'token': token
        }
        return self._build_url(params)

    def get_profile_videos(self, token, nick):
        params = {
            'command': 'getProfileVideos',
            'nick': nick,
            'actPath': f'/{nick}/videos',
            'token': token
        }
        return self._build_url(params)

    def get_item_info(self, token, data, l_data):
        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/video/{l_data}',
            'token': token
        }
        return self._build_url(params)