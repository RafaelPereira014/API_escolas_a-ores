from functools import wraps
import bcrypt
import pymysql
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session, url_for
from config import DB_CONFIG, API_KEY  # Import the API key from the config

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

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
@api_key_required  # Apply the decorator here to ensure the API key is checked
def get_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT escola_id, escola_nome, ilha_id FROM escolas")
    rows = cursor.fetchall()
    conn.close()

    return jsonify({"table": rows})
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Convert to bytes

        # Check credentials against the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT admin_id, password FROM admin WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash = result[1].encode('utf-8')  # Convert DB password to bytes
            # Compare the hashed password
            if bcrypt.checkpw(password, stored_hash):
                session['admin_id'] = result[0]  # Store admin_id in the session
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


# Route for main page that lists available tables
@app.route('/')
def index():
    if 'admin_id' not in session:
        return redirect(url_for('login'))  
    
    return render_template('index.html')

@app.route('/tabela_escolas')
def escolas():
    if 'admin_id' not in session:
        return redirect(url_for('login'))  
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT escola_id, escola_nome, ilha_id FROM escolas")
    rows = cursor.fetchall()
    conn.close()
    return render_template('escolas.html', table_data=rows)

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/edit_escola', methods=['POST'])
def edit_escola():
    if 'admin_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json()
    escola_id = data['escola_id']
    escola_nome = data['escola_nome']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE escolas SET escola_nome = %s WHERE escola_id = %s", (escola_nome, escola_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Escola Nome updated"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)