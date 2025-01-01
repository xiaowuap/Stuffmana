from flask import Blueprint, request, jsonify
import qrcode
from db import create_connection
from auth_utils import basic_auth_required

devices_bp = Blueprint("devices", __name__)

@devices_bp.route("/devices", methods=["GET"])
@basic_auth_required
def list_devices():
    """
    列出所有设备 (受保护)
    """
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices")
        devices = cursor.fetchall()
        conn.close()
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@devices_bp.route("/devices", methods=["POST"])
@basic_auth_required
def add_device():
    """
    添加新设备 (受保护)
    """
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO devices (name, category, location, status)
                 VALUES (%s, %s, %s, %s)"""
        vals = (
            data.get("name"),
            data.get("category", ""),
            data.get("location", ""),
            data.get("status", "")
        )
        cursor.execute(sql, vals)
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({"message": "Device added", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@devices_bp.route("/devices/<int:device_id>", methods=["DELETE"])
@basic_auth_required
def delete_device(device_id):
    """
    根据设备ID删除设备 (受保护)
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM devices WHERE id = %s"
        val = (device_id,)
        cursor.execute(sql, val)
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows == 0:
            return jsonify({"error": "Device not found"}), 404
        else:
            return jsonify({"message": "Device deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@devices_bp.route("/devices/<int:device_id>/label", methods=["GET"])
@basic_auth_required
def generate_label(device_id):
    """
    根据设备ID生成二维码 (受保护)
    """
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM devices WHERE id = %s"
        val = (device_id,)
        cursor.execute(sql, val)
        device = cursor.fetchone()
        conn.close()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # 生成二维码内容
        qr_content = f"Device ID: {device['id']}\nName: {device['name']}"
        img = qrcode.make(qr_content)

        # 保存
        filename = f"label_{device['id']}.png"
        img.save(filename)

        return jsonify({
            "message": "Label generated",
            "file": filename
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
