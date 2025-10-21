from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

DATABASE = os.path.join(os.path.dirname(__file__), "contacts.db")

# ---------- Database ----------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------- Routes ----------
@app.route('/')
def index():
    # Serve the frontend
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/contacts', methods=['GET'])
def get_contacts():
    conn = get_db_connection()
    contacts = conn.execute("SELECT * FROM contacts").fetchall()
    conn.close()
    return jsonify([dict(row) for row in contacts])

@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.get_json()
    name, email, phone = data.get('name'), data.get('email'), data.get('phone')

    if not name or not email or not phone:
        return jsonify({'error': 'All fields required!'}), 400

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        return jsonify({'message': 'Contact added successfully!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists!'}), 409
    finally:
        conn.close()

@app.route('/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    data = request.get_json()
    name, email, phone = data.get('name'), data.get('email'), data.get('phone')

    conn = get_db_connection()
    contact = conn.execute("SELECT * FROM contacts WHERE id=?", (id,)).fetchone()
    if not contact:
        conn.close()
        return jsonify({'error': 'Contact not found!'}), 404

    conn.execute("UPDATE contacts SET name=?, email=?, phone=? WHERE id=?", (name, email, phone, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Contact updated successfully!'})

@app.route('/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    conn = get_db_connection()
    contact = conn.execute("SELECT * FROM contacts WHERE id=?", (id,)).fetchone()
    if not contact:
        conn.close()
        return jsonify({'error': 'Contact not found!'}), 404

    conn.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Contact deleted successfully!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
