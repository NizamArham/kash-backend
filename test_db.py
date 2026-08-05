from app.config import DevelopmentConfig
from sqlalchemy import create_engine, text

try:
    engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful!')
        print('URI:', DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
except Exception as e:
    print(f'❌ Connection failed: {e}')
