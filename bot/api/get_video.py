from aiohttp import ClientSession

from bot import logger
from bot.config_reader import config


# Функция для запросов к Cobalt api
async def get_video(video_url: str):
    async with ClientSession() as sess:
        request_body = {
            "url": video_url,
            "videoQuality": "720",
            "audioFormat": "mp3",
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        async with sess.post(
            config.api_url.get_secret_value(),
            json=request_body,
            headers=headers,
        ) as response:
            try:
                data = await response.json()
                return data
            except Exception as e:
                logger.error(f"Error in request: {e}")
                raise e
