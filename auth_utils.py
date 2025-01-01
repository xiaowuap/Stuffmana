import base64
from flask import request, jsonify
from functools import wraps
from passlib.hash import bcrypt
from db import create_connection

def parse_auth_header():
    """
    从请求头中解析出用户名和密码 (Basic Auth)
    返回 (username, password) 或 None
    """
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

def verify_user(username, plain_password):
    """
    验证用户名+明文密码是否正确
    """
    # 这里的 get_user_by_username 同样可以放在这里，或者另外一个 users 模块
    user = get_user_by_username(username)
    if not user:
        return False
    hashed_password = user["password"]  
    return bcrypt.verify(plain_password, hashed_password)

def get_user_by_username(username):
    """
    根据用户名获取用户记录，返回 dict 或 None
    """
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

def basic_auth_required(f):
    """
    装饰器：在需要鉴权的接口上使用
    """
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
