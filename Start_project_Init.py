import sqlite3
from cryptography.fernet import Fernet

def signup(username, password):
    connection = sqlite3.connect("PM.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users VALUES(?,?)", (username, password))
    connection.commit()
    connection.close()

def searchUser(key, username, password):
    f = Fernet(key)
    conn = sqlite3.connect("PM.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    items = c.fetchall()
    for item in items:
        decrypted_pass = f.decrypt(item[1])
        original_pass = decrypted_pass.decode()
        if original_pass == password:
            return True
        else:
            return False
    conn.commit()
    conn.close()

def tableCreate():
    connection = sqlite3.connect("PM.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                    username TEXT,
                    password TEXT
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS blacklist (
                    username TEXT
                    )""")
    connection.commit()
    connection.close()

