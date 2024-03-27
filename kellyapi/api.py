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
                response = await resp.read()
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
                response = await resp.read()
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
