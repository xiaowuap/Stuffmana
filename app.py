from flask import Flask
from db import init_db
from users import users_bp
from devices import devices_bp

app = Flask(__name__)

# 在应用启动时初始化数据库
init_db()

# 注册蓝图
app.register_blueprint(users_bp)
app.register_blueprint(devices_bp)

if __name__ == "__main__":
    # 直接启动
    app.run(host="0.0.0.0", port=5000, debug=True)
