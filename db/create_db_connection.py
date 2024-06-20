import pymysql
import logging
from config_reader import config


def create_db_connection():
    try:
        connection = pymysql.connect(
            host=config.mysql_host.get_secret_value(),
            port=3306,
            user=config.mysql_user.get_secret_value(),
            password=config.mysql_password.get_secret_value(),
            database=config.mysql_db.get_secret_value(),
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Successfully connected to db")

    except Exception as e:
        logging.info(f"Connection to db refused: {e}")

    finally:
        connection.close()
