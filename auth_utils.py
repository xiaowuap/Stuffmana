import base64
from flask import request, jsonify, current_app
from functools import wraps
from passlib.hash import bcrypt
from db import create_connection

from config import ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_auth_header():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "basic":
        return None

    try:
        decoded = base64.b64decode(parts[1]).decode('utf-8')
        user_pass = decoded.split(":", 1)
        if len(user_pass) != 2:
            return None
        return user_pass[0], user_pass[1]
    except Exception:
        return None

def get_user_by_username(username):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM users WHERE username=%s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    except:
        return None

def verify_user(username, plain_password):
    user = get_user_by_username(username)
    if not user:
        return False
    hashed_password = user["password"]
    return bcrypt.verify(plain_password, hashed_password)

def basic_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        creds = parse_auth_header()
        if not creds:
            return jsonify({"error": "Unauthorized"}), 401
        username, password = creds
        if not verify_user(username, password):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
