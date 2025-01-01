import os

# 现有配置...
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_NAME = os.getenv("DB_NAME", "device_manager_db")

# 新增配置
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # 或指定其他路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
