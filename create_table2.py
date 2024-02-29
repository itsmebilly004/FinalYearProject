import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE properties (username VARCHAR(35) NOT NULL, email VARCHAR(35) NOT NULL, password VARCHAR(200) NOT NULL, phone VARCHAR NOT NULL)')
print("Created table successfully!")

conn.close()
