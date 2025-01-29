import pymysql
from config import DB_CONFIG, API_KEY  # Import the API key from the config


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def get_auth(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, password FROM admin WHERE username = %s", (username,))
    result = cursor.fetchone()
    conn.close()
    
    return result