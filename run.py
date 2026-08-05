from app import create_app
from app.extensions import db
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

# Debug: Check if database file exists
with app.app_context():
    db_path = os.path.abspath('data.sqlite3.db')
    print(f"📁 Database file path: {db_path}")
    print(f"📁 Does the file exist? {os.path.exists(db_path)}")
    
    # Force create tables if they don't exist
    db.create_all()
    print("✅ Tables verified/created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
