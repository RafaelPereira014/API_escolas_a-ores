import pymysql
from flask import Flask, json, jsonify, request
from config import DB_CONFIG, API_KEY  # Import the API key from the config

app = Flask(__name__)

# Helper function to connect to the database
def connect_db():
    return pymysql.connect(**DB_CONFIG)

# Decorator to check the API key
def api_key_required(f):
    def decorator(*args, **kwargs):
        # Get the API key from the request headers
        api_key = request.headers.get('X-API-KEY')
        
        if api_key != API_KEY:
            return jsonify({"error": "Forbidden, invalid API key"}), 403
        
        return f(*args, **kwargs)
    return decorator

# Route to fetch the full table with API key authentication
@app.route('/escolas', methods=['GET'])
def get_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT escola_id, escola_nome, ilha_id FROM escolas")
    rows = cursor.fetchall()
    conn.close()

    # Decode special characters in the escola_nome field
    for row in rows:
        row['escola_nome'] = json.loads(f'"{row["escola_nome"]}"')
        print(row['escola_nome'])

    return jsonify({"table": rows})

@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)