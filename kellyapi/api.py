import asyncio
import aiohttp
from dotmap import DotMap
from aiohttp.client_exceptions import (
    ContentTypeError,
    ClientConnectorError,
)
from io import BytesIO
from typing import Union, List
from .errors import *

class KellyAPI:
    """
    PrinceAPI class to access all the endpoints
    Documentation: https://api.kellyai.pro/docs
    Support Group: https://t.me/KellyAIChat
    Updates Channel: https://t.me/KellyAINews
    """

    def __init__(self, api: str = None, api_key: str, session: aiohttp.ClientSession = None):
        self.api = api or "https://api.kellyai.pro/"
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession

    def _parse_result(self, response: dict) -> Union[DotMap, List[BytesIO]]:
        type = response.get("type")
        error = response.get("error")
        response = DotMap(response)
        if not error:
            response.success = True
        return response
        
    async def _fetch(self, route, timeout=60, **params):
        try:
            async with self.session() as client:
                resp = await client.get(self.api + route, params=params, headers={"X-Kelly-KEY": self.api_key}, timeout=timeout)
                if resp.status in (401, 403):
                    raise InvalidApiKey(
                        "Invalid API key, Get an api key from @ARQRobot"
                    )
                if resp.status == 502:
                    raise ConnectionError()
                response = await resp.json()
                if resp.status == 400:
                    raise InvalidRequest(response.get("docs"))
                if resp.status == 422:
                    raise GenericApiError(response.get("error"))
        except asyncio.TimeoutError:
            raise TimeoutError
        except ContentTypeError:
            raise InvalidContent
        except ClientConnectorError:
            raise ConnectionError
        return self._parse_result(response)

    async def _post_data(self, route, data, timeout=60):
        try:
            async with self.session() as client:
                resp = await client.post(self.api + route, data=data, headers={"X-Kelly-KEY": self.api_key}, timeout=timeout)
                if resp.status in (401, 403):
                    raise InvalidApiKey(
                        "Invalid API key, Get an api key from @ARQRobot"
                    )
                if resp.status == 502:
                    raise ConnectionError()
                response = await resp.json()
                if resp.status == 400:
                    raise InvalidRequest(response.get("docs"))
                if resp.status == 422:
                    raise GenericApiError(response.get("error"))
        except asyncio.TimeoutError:
            raise TimeoutError
        except ContentTypeError:
            raise InvalidContent
        except ClientConnectorError:
            raise ConnectionError
        return self._parse_result(response)


    async def generate(self, prompt: str, **kwargs):
        """
        Returns An Object.
                Parameters:
                        code (str): Code to make carbon
                        kwagrs (dict): Extra args for styling
                Returns:
                        Result object (BytesIO): Results which you can access with filename
        """
        if "prompt" not in kwargs:
            kwargs["prompt"] = prompt

        return await self._post_json("generate", json=kwargs)

    async def svlyrics(self, svid: str):
        """
        Returns An Object.
                Parameters:
                        svid (str): id of song on saavn
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('svlyrics', svid=svid)

    async def splyrics(self, trackid: str):
        """
        Returns An Object.
                Parameters:
                        trackid (str): Track id of the song on spotify
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('splyrics', trackid=trackid)

    async def lyrics(self, query: str, telegraph: bool = False, botname: str = 'MerissaRobot'):
        """
        Returns An Object.
                Parameters:
                        query (str): Query to search
                        telegraph (bool): If true, it will give a telegraph link for lyrics
                        botname (str): Username of telegram bot to put in telegraph link
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        route = 'lyrics'
        if telegraph:
            return await self._fetch(route, query=query, botname=botname)
        route += "/text"
        return await self._fetch(route, query=query)

    async def ytlyrics(self, videoid: str):
        """
        Returns An Object.
                Parameters:
                        videoid (str): Video id of the video on YouTube
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytlyrics', videoid=videoid)

    async def ytmsearch(self, query: str):
        """
        Returns An Object.
                Parameters:
                        query (str): Query to search
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytmsearch', query=query)

    async def ytmlyrics(self, videoid: str):
        """
        Returns An Object.
                Parameters:
                        videoid (str): Video id of the video on YouTube Music
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytmlyrics', videoid=videoid)

    async def ytmtrack(self, videoid: str):
        """
        Returns An Object.
                Parameters:
                        videoid (str): Video id of the video on YouTube Music
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytmtrack', videoid=videoid)

    async def ytmalbum(self, browseid: str):
        """
        Returns An Object.
                Parameters:
                        browseid (str): Browse id of the album on YouTube Music
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytmalbum', browseid=browseid)

    async def ytthumb(self, videoid: str):
        """
        Returns An Object.
                Parameters:
                        videoid (str): Video id of the video on YouTube
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytthumb', videoid=videoid)
    
    async def ytinfo(self, link: str):
        """
        Returns An Object.
                Parameters:
                        link (str): Link of the video on YouTube
                Returns:
                        Result object (str): Results which you can access with dot notation
        """
        return await self._fetch('ytinfo', link=link)
