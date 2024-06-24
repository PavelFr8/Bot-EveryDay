import requests
import logging


# Функция для запросов к Cobalt api
def get_video(url: str):
    request_body = {
        "url": url,
        "vCodec": "h264",
        "vQuality": "720",
        "aFormat": "mp3"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.cobalt.tools/api/json", json=request_body, headers=headers)

    try:
        data = response.json()
        logging.info('User get video')
        return data['url']
    except Exception as e:
        logging.info(f"Error in request: {e}")
        raise e
