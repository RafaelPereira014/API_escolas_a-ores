from functools import wraps
import bcrypt
import pymysql
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session, url_for
from config import DB_CONFIG, API_KEY, SECRET_KEY  
from db_operations.escolas.escolas import *
from db_operations.admin import *


app = Flask(__name__)
app.secret_key = SECRET_KEY 


def connect_db():
    return pymysql.connect(**DB_CONFIG)



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
@api_key_required  
def get_table():
    rows = get_escolas()

    return jsonify({"table": rows})

@app.route('/colocados', methods=['POST'])
def add_colocado():
    try:
        data = request.get_json()

        # Validate required fields
        nif = data.get('NIF')
        bolsa_id = data.get('Bolsa_id')
        escola_nome = data.get('Escola_nome')
        data_colocacao = data.get('Data_colocacao')
        estado = data.get('Estado')

        if not all([nif, bolsa_id, escola_nome, data_colocacao, estado]):
            return jsonify({"error": "Missing required fields"}), 400

        # Insert data into the database
        connection = connect_db()
        with connection.cursor() as cursor:
            sql = '''
                INSERT INTO colocados (NIF, Bolsa_id, Escola_nome, Data_colocacao, Estado)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, (nif, bolsa_id, escola_nome, data_colocacao, estado))
        connection.commit()
        connection.close()

        return jsonify({"message": "Data successfully inserted"}), 200

    except pymysql.MySQLError as e:
        print(f"Database Error: {e}")
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/colocados_<int:bolsa_id>_<string:escola_nome>', methods=['GET'])
def get_colocados(bolsa_id, escola_nome):
    try:
        # Fetch filtered data from the database
        connection = connect_db()
        with connection.cursor() as cursor:
            sql = '''
                SELECT NIF, Bolsa_id, Escola_nome, Data_colocacao, Estado
                FROM colocados
                WHERE Bolsa_id = %s AND Escola_nome = %s
            '''
            cursor.execute(sql, (bolsa_id, escola_nome))
            rows = cursor.fetchall()
        connection.close()

        # Return the filtered data
        return jsonify(rows), 200

    except pymysql.MySQLError as e:
        print(f"Database Error: {e}")
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  

        result = get_auth(username)

        if result:
            stored_hash = result[1].encode('utf-8')  
            
            if bcrypt.checkpw(password, stored_hash):
                session['admin_id'] = result[0]  
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/')
def index():
    if 'admin_id' not in session:
        return redirect(url_for('login'))  
    
    return render_template('index.html')

@app.route('/tabela_escolas')
def escolas():
    if 'admin_id' not in session:
        return redirect(url_for('login'))  
    
    rows = get_escolas()
    
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

    update_escolas(escola_nome,escola_id)

    return jsonify({"success": True, "message": "Escola Nome updated"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)