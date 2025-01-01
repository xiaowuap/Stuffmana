from flask import Blueprint, request, jsonify
from passlib.hash import bcrypt
from db import create_connection
from auth_utils import get_user_by_username

users_bp = Blueprint("users", __name__)

@users_bp.route("/register", methods=["POST"])
def register():
    """
    注册新用户
    """
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid input"}), 400

    username = data["username"]
    plain_password = data["password"]

    # 1. 先检查用户名是否被占用
    existing_user = get_user_by_username(username)
    if existing_user:
        return jsonify({"error": "Username already taken"}), 400

    # 2. bcrypt哈希
    hashed_password = bcrypt.hash(plain_password)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(sql, (username, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
