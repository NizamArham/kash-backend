# run.py
from app import create_app
from app.extensions import db
import os
import sqlite3

print("🔍 Starting application...")

# Find all .sqlite3 files in the project
print("🔍 Searching for database files...")
found_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.sqlite3'):
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            found_files.append(path)
            print(f"📁 Found: {path} ({size} bytes)")

if not found_files:
    print("❌ No .sqlite3 files found in the project!")

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    # Print the actual database URI being used
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"🔗 SQLAlchemy Database URI: {db_uri}")
    
    # Extract the file path from the URI
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"📁 SQLAlchemy file path: {db_path}")
        print(f"📁 Does the file exist? {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            # Check file size
            file_size = os.path.getsize(db_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Direct SQLite check
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # List all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"📋 Tables in database: {[t[0] for t in tables]}")
                
                if 'customers' in [t[0] for t in tables]:
                    cursor.execute("SELECT COUNT(*) FROM customers")
                    count = cursor.fetchone()[0]
                    print(f"📊 Number of customers: {count}")
                else:
                    print("❌ 'customers' table not found!")
                
                conn.close()
            except Exception as e:
                print(f"⚠️ Error reading file: {e}")
        else:
            print("❌ SQLAlchemy file path does not exist!")
    
    # Try a SQLAlchemy query
    try:
        from app.models.customer import Customer
        count = Customer.query.count()
        print(f"📊 SQLAlchemy customer count: {count}")
    except Exception as e:
        print(f"⚠️ SQLAlchemy query error: {e}")
    
    print("✅ Application startup complete")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    