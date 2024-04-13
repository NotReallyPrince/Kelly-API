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

    def __init__(self, api_key: str = None, api: str = None, session: aiohttp.ClientSession = None):
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
        except asyncio.TimeoutError:
            raise TimeoutError
        except ContentTypeError:
            raise InvalidContent
        except ClientConnectorError:
            raise ConnectionError
        return self._parse_result(response)

    async def _post_json(self, route, data, timeout=60):
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
        except asyncio.TimeoutError:
            raise TimeoutError
        except ContentTypeError:
            raise InvalidContent
        except ClientConnectorError:
            raise ConnectionError
        return response
        
    async def sd_models(self):
        content = await self._fetch("sd-models")
        return content
        
    async def sdxl_models(self):
        content = await self._fetch("sdxl-models")
        return content
        
    async def get_style(self):
        content = await self._fetch("styles")
        return content

    async def generate(self, prompt: str, negative_prompt: str = "auto", model:str = "DreamShaper", style: str = "cinematic", width: str = 1024, height: str = 1024):
        kwargs = dict(prompt=prompt, negative_prompt=negative_prompt, model=model, style=style, width=width, height=height)
        content = await self._post_data("generate", json=kwargs)
        image = BytesIO(content)
        image = "image.png"
        return image

    async def llm_models(self):
        content = await self._fetch("llm-models")
        return content

    async def llm(self, prompt: str, model: str = "ChatGPT", character: str = "KelyAI"):
        kwargs = dict(prompt=prompt, model=model, character=character)
        content = await self._post_json("llm", json=kwargs)
        return content.message
        
    async def upscale(self, image: str):
        kwargs = dict(image=image)
        content = await self._post_data("upscale", json=kwargs)
        image = BytesIO(content)
        image = "image.png"
        return image

    async def voice_models(self):
        content = await self._fetch("voice-models")
        return content

    async def text2voice(self, text: str, model: str = "en-US_LisaExpressive"):
        kwargs = dict(text=text, model=model)
        content = await self._post_data("text2voice", json=kwargs)
        image = BytesIO(content)
        image = "image.png"
        return image
        
    async def voice2text(self, audio: str):
        kwargs = dict(audio=audio)
        content = await self._post_json("voice2text", json=kwargs)
        return content.result
        
