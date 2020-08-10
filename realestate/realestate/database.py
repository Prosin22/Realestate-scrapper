import sqlite3

conn = sqlite3.connect("houses.db")
curr = conn.cursor()