from app import create_app
from app.extensions import db
import os
import sqlite3

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    db_path = os.path.abspath('data.sqlite3')
    print(f"📁 Database file path: {db_path}")
    print(f"📁 Does the file exist? {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            print(f"📊 Number of customers: {count}")
            conn.close()
        except Exception as e:
            print(f"⚠️ Error reading file: {e}")
    
    # db.create_all()
    print("✅ Using existing database file")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)