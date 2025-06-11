from aiohttp import ClientSession

from bot import logger


# Функция для запросов к Cobalt api
async def get_video(video_url: str):
    async with ClientSession() as sess:
        url = "https://api.cobalt.tools/api/json"

        request_body = {
            "url": video_url,
            "vCodec": "h264",
            "vQuality": "720",
            "aFormat": "mp3",
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        async with sess.post(
            url,
            json=request_body,
            headers=headers,
        ) as response:
            try:
                data = await response.json()
                logger.info("User get video")
                return data["url"]
            except Exception as e:
                logger.info(f"Error in request: {e}")
                raise e
