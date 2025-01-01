from flask import Blueprint, request, jsonify, current_app, send_from_directory
import qrcode
import os
from werkzeug.utils import secure_filename
from db import create_connection
from auth_utils import basic_auth_required, allowed_file
import uuid

devices_bp = Blueprint("devices", __name__)

@devices_bp.route("/devices", methods=["GET"])
@basic_auth_required
def list_devices():
    """
    列出所有设备信息，包含图片URL
    """
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices")
        devices = cursor.fetchall()
        conn.close()

        # 构建图片URL
        for device in devices:
            if device.get("image"):
                device["image_url"] = f"/uploads/{device['image']}"
            else:
                device["image_url"] = None

        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@devices_bp.route("/devices", methods=["POST"])
@basic_auth_required
def add_device():
    """
    添加新设备，支持图片上传
    """
    name = request.form.get("name")
    category = request.form.get("category", "")
    location = request.form.get("location", "")
    status = request.form.get("status", "")
    image = request.files.get("image", None)

    if not name:
        return jsonify({"error": "Invalid input: 'name' is required"}), 400

    image_filename = None
    if image:
        if image.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if image and allowed_file(image.filename):
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(image_path)
            image_filename = unique_filename
        else:
            return jsonify({"error": "File type not allowed"}), 400

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO devices (name, category, location, status, image)
                 VALUES (%s, %s, %s, %s, %s)"""
        vals = (name, category, location, status, image_filename)
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
    根据设备ID删除设备及其图片
    """
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT image FROM devices WHERE id = %s"
        cursor.execute(sql, (device_id,))
        device = cursor.fetchone()

        if not device:
            conn.close()
            return jsonify({"error": "Device not found"}), 404

        # 删除数据库记录
        sql_delete = "DELETE FROM devices WHERE id = %s"
        cursor.execute(sql_delete, (device_id,))
        conn.commit()
        conn.close()

        # 删除图片文件
        if device.get("image"):
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], device['image'])
            if os.path.exists(image_path):
                os.remove(image_path)

        return jsonify({"message": "Device deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@devices_bp.route("/devices/<int:device_id>/label", methods=["GET"])
@basic_auth_required
def generate_label(device_id):
    """
    根据设备ID生成二维码，包含设备信息和图片URL
    """
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM devices WHERE id = %s"
        cursor.execute(sql, (device_id,))
        device = cursor.fetchone()
        conn.close()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # 生成二维码内容，包含图片URL
        qr_content = f"Device ID: {device['id']}\nName: {device['name']}"
        if device.get("image"):
            qr_content += f"\nImage URL: {request.host_url}uploads/{device['image']}"

        img = qrcode.make(qr_content)

        # 生成二维码文件名
        label_filename = f"label_{device['id']}.png"
        label_path = os.path.join(current_app.config['UPLOAD_FOLDER'], label_filename)
        img.save(label_path)

        return jsonify({
            "message": "Label generated",
            "file": f"/uploads/{label_filename}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
