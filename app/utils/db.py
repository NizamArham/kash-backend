import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from config import Config

class Database:
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'port': Config.DB_PORT,
            'cursorclass': DictCursor,
            'autocommit': False,
            'charset': 'utf8mb4'
        }
    
    @contextmanager
    def get_connection(self):
        connection = pymysql.connect(**self.config)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @contextmanager
    def get_cursor(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                yield cursor

# Singleton instance
db = Database()