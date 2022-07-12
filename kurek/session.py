import asyncio

from aiohttp import ClientSession

from . import config


class Session:
    def __init__(self):
        self._api_sem = asyncio.Semaphore(config.max_api_requests)
        self._download_sem = asyncio.Semaphore(config.max_download_requests)

    def run(self, coroutine, params):
        async def _run():
            async with ClientSession(
                    headers=config.request_headers
                ) as session:
                response = await coroutine(session, params)
            return response
        return asyncio.run(_run())
