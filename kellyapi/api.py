import asyncio
import base64
from io import BytesIO
from typing import List, Union

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError
from dotmap import DotMap

from .errors import *


class KellyAPI:
    def __init__(
        self,
        api_key: str = None,
        api: str = None,
        session: aiohttp.ClientSession = None,
    ):
        self.api = api or "https://api.kellyai.pro/"
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession

    def _parse_result(self, response: dict) -> Union[DotMap, List[BytesIO]]:
        response = DotMap(response)
        if not error:
            response.success = True
        return response

    async def _fetch(self, route, timeout=60, **params):
        try:
            async with self.session() as client:
                resp = await client.get(
                    self.api + route,
                    params=params,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=timeout,
                )
                if resp.status in (401, 403):
                    raise InvalidApiKey(
                        "Invalid API key, Get an api key from @KellyAIBot"
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
        return response

    async def _post_json(self, route, data=None, timeout=60):
        try:
            async with self.session() as client:
                resp = await client.post(
                    self.api + route,
                    json=data,
                    headers={"Kelly-API-KEY": f"Bearer {self.api_key}"},
                    timeout=timeout,
                )
                if resp.status in (401, 403):
                    raise InvalidApiKey(
                        "Invalid API key, Get an api key from @KellyAIBot"
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

    async def sd_models(self):
        content = await self._fetch("sd/models")
        return content

    async def sdxl_models(self):
        content = await self._fetch("sdxl/models")
        return content

    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "canvas frame, cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, nsfw",
        model: str = "PhotoPerfect",
        width: int = 1024,
        height: int = 1024,
    ):
        kwargs = dict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            width=width,
            height=height,
            responseType="base64data",
        )
        content = await self._post_json("image/generate", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data

    async def img2img(
        self,
        prompt: str,
        image_data: str,
        negative_prompt: str = "canvas frame, cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, nsfw",
        width: str = 1024,
        height: str = 1024,
    ):
        kwargs = dict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image_data=image_data,
            width=width,
            height=height,
            responseType="base64data",
        )
        content = await self._post_json("image/edit", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data

    async def img2text(
        self,
        prompt: str,
        image_data: str,
    ):
        kwargs = dict(
            prompt=prompt,
            image_data=image_data,
        )
        content = await self._post_json("image/description", data=kwargs)
        return content.content

    async def llm_models(self):
        content = await self._fetch("chat/models")
        return content

    async def llm(self, prompt: str, model: str = "chatgpt", character: str = "KelyAI"):
        kwargs = dict(prompt=prompt, character=character)
        content = await self._post_json(f"chat/{model}", data=kwargs)
        return content.message

    async def upscale(self, image_data: str):
        kwargs = dict(image_data=image_data, responseType="base64data")
        content = await self._post_json("image/upscale", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data

    async def removebg(self, image_data: str):
        kwargs = dict(image_data=image_data, responseType="base64data")
        content = await self._post_json("image/removebg", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data

    async def voice_models(self):
        content = await self._fetch("voice/models")
        return content

    async def text2voice(self, text: str, model: str = "en-US_LisaExpressive"):
        kwargs = dict(text=text, model=model, responseType="base64data")
        content = await self._post_json("voice/generation", data=kwargs)
        image_data = base64.b64decode(content.voice)
        return image_data

    async def voice2text(self, audio: str):
        kwargs = dict(audio=audio)
        content = await self._post_json("voice/transcribe", data=kwargs)
        return content.result

    async def text2write(self, text: str):
        kwargs = dict(code=text, responseType="base64data")
        content = await self._post_json("write/notes", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data

    async def code2image(self, text: str):
        kwargs = dict(code=text, responseType="base64data")
        content = await self._post_json("write/code", data=kwargs)
        image_data = base64.b64decode(content.image)
        return image_data
