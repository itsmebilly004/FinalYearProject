import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE properties (id INTEGER PRIMARY KEY AUTOINCREMENT,location VARCHAR(35) NOT NULL, type VARCHAR(35) NOT NULL, image_path TEXT NOT NULL )')
print("Created table successfully!")

conn.close()
