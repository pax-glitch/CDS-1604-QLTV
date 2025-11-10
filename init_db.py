import sqlite3
import os

# Create database directory if not exists
os.makedirs('database', exist_ok=True)

# Create and connect to database
db_path = 'database/library.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Database created successfully at: {db_path}")
conn.close()

# Now run initdb
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("✓ Database tables created successfully!")
