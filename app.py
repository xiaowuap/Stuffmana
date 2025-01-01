from flask import Flask, send_from_directory
from config import UPLOAD_FOLDER
from db import init_db
from users import users_bp
from devices import devices_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 注册蓝图
app.register_blueprint(users_bp)
app.register_blueprint(devices_bp)

# 配置静态路由用于访问上传的图片
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
