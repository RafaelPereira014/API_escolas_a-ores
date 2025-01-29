import pymysql
from config import DB_CONFIG, API_KEY  # Import the API key from the config

# Helper function to connect to the database
def connect_db():
    return pymysql.connect(**DB_CONFIG)

def get_escolas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT escola_id, escola_nome, ilha_id FROM escolas")
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def update_escolas(escola_nome,escola_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE escolas SET escola_nome = %s WHERE escola_id = %s", (escola_nome, escola_id))
    conn.commit()
    conn.close()
    