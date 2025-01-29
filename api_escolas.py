import pymysql

from flask import Flask, jsonify, render_template, request
from config import DB_CONFIG;

app = Flask(__name__)



# Helper function to connect to the database
def connect_db():
    return pymysql.connect(**DB_CONFIG)

# Route to fetch the full table
@app.route('/escolas', methods=['GET'])
def get_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT escola_id, escola_nome, ilha_id FROM escolas")
    rows = cursor.fetchall()
    conn.close()

    return jsonify({"table": rows})



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port='8081')