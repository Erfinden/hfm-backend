import sqlite3
import os
import shutil

DATABASE_FILE = 'users.db'


def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            key TEXT PRIMARY KEY,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()


def load_users():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT key, email FROM users')
    rows = c.fetchall()
    users = {row[0]: row[1] for row in rows}
    conn.close()
    return users


def add_user(key, email=""):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO users (key, email) VALUES (?, ?)', (key, email))
    conn.commit()
    conn.close()


def remove_user(key):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE key = ?', (key,))
    conn.commit()
    conn.close()


def delete_user_folder(key):
    folder_path = f'/home/images/{key}'
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    else:
        print(f"Folder for key '{key}' does not exist.")
        
        
def update_email_in_database(key, email):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('UPDATE users SET email = ? WHERE key = ?', (email, key))
    conn.commit()
    conn.close()
