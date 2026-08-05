import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def create_database():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        
        print(f"✅ Database '{os.getenv('DB_NAME')}' created successfully!")
        
        cursor.close()
        connection.close()
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\nMake sure XAMPP MySQL is running!")
        print("To start MySQL:")
        print("  1. Open XAMPP Control Panel")
        print("  2. Click 'Start' on MySQL")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_database()
