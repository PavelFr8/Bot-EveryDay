# Bot Helper
<a href="https://t.me/DailyHelper8_bot"><img src="https://img.shields.io/badge/Telegram_bot-🐸%20@DailyHelper8-blue"></a>  

Bot Helper - Telegram bot, which gets you the opportunity create plans for a day, notifications and download video.

![screenshot](img.png)

## Used technology
* Python 3.9;
* aiogram 3.x (Telegram Bot framework);
* PostgreSQL (database);
* SQLAlchemy (working with database from Python);
* [Cobalt API](https://github.com/cobalthq/cobalt-api-docs) (downloading video) 

## How to start bot

```ubuntu
git clone https://github.com/PavelFr8/Bot-EveryDay
```

Write your **Telegram bot token** and **database url** to **.env**

```ubuntu
pip install -r requirements.txt
```

Create tables in database

```ubuntu
python3 main.py create_tables
```

Run ngrok server
```ubuntu
ngrok http 8080
```

Run bot
```ubuntu
python3 main.py <ngrok_url>
```
