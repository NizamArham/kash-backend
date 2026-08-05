# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    
    # Check if running on Render or using SQLite
    if os.getenv('RENDER') or os.getenv('USE_SQLITE') == 'True':
        # Use SQLite for Render deployment
        SQLALCHEMY_DATABASE_URI = 'sqlite:///ecom_store.db'
        print("✅ Using SQLite database (Render)")
    else:
        # Use MySQL locally (XAMPP)
        DB_SOCKET = os.getenv('DB_SOCKET')
        
        if DB_SOCKET:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
                f"@localhost:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?unix_socket={DB_SOCKET}"
            )
        else:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
                f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
            )
        print("✅ Using MySQL database (Local)")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True if os.getenv('DEBUG') == 'True' else False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
