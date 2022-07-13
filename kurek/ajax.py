from yarl import URL

from .balancer import Balancer


class AjaxCommand:
    def __init__(self, url):
        self._url = url

    def _get_request(self, params):
        return str(URL(self._url) % params)

    def login(self, email, password, ltoken):
        params = {
            'command': 'login',
            'email': email,
            'password': password,
            'ltoken': ltoken
        }
        return self._get_request(params)

    def get_profile_photos(self, nick, token):
        params = {
            'command': 'getProfilePhotos',
            'nick': nick,
            'actPath': f'/{nick}/photos',
            'token': token
        }
        return self._get_request(params)

    def get_profile_videos(self, nick, token):
        params = {
            'command': 'getProfileVideos',
            'nick': nick,
            'actPath': f'/{nick}/videos',
            'token': token
        }
        return self._get_request(params)

    def get_video_info(self, data, l_data, token):
        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/video/{l_data}',
            'token': token
        }
        return self._get_request(params)

    def get_photo_info(self, data, l_data, token):
        params = {
            'command': 'getItemInfo',
            'data': data,
            'actPath': f'/photo/{l_data}',
            'token': token
        }
        return self._get_request(params)


class Ajax:
    def __init__(self, session):
        self._balancer = Balancer()
        self._session = session

    @property
    def url(self):
        return self._balancer.next_url()

    async def login(self, email, password, ltoken, callback):
        url = AjaxCommand(self.url).login(email, password, ltoken)
        json = await self.get(url, callback)

    async def get_profile_photos(self, nick, token, callback):
        url = AjaxCommand(self.url).get_profile_photos(nick, token)
        await self.get(url, callback)

    async def get_profile_videos(self, nick, token, callback):
        url = AjaxCommand(self.url).get_profile_videos(nick, token)
        await self.get(url, callback)

    async def get_video_info(self, data, ldata, token, callback):
        url = AjaxCommand(self.url).get_video_info(data, ldata, token)
        await self.get(url, callback)

    async def get(self, url, callback=None):
        async with self._session.api_limiter:
            async with self._session.client.get(url) as response:
                response.raise_for_status()
                json = await response.json(content_type=None)
        if callback is not None:
            await callback(self, json)
        return json

    async def download(self, url, callback=None):
        async with self._session.download_limiter:
            async with self._session.client.get(url) as response:
                response.raise_for_status()
                data = await response.read()
        if callback is not None:
            await callback(self, url, data)
        return data
