import sqlite3
import os

# Create notes.sqlite

db = \
"""
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Notes (
    id integer PRIMARY KEY,
    content text NOT NULL,
    user varchar(20) NOT NULL
);
CREATE TABLE CurrentUser (
	currentuser varchar(20) PRIMARY KEY	
);
"""

if os.path.exists('notes.sqlite'):
	print('notes.sqlite already exists')
else:
	conn = sqlite3.connect('notes.sqlite')
	conn.cursor().executescript(db)
	conn.commit()
	conn.close()