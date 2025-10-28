import pymysql
from config import Config
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self):
        self.config = Config()

    def get_connection(self):
        try:
            connection = pymysql.connect(
                host=self.config.DB_HOST,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME,
                port=self.config.DB_PORT,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            raise


# Instancia global
db = DatabaseConnection()