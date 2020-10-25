from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from config import Config

app = Flask(__name__)

# 设置配置类
app.config.from_object(Config)

# 创建数据库对象
db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True) # 转成字节码

# 创建session对象
Session(app)

# 开启csrf保护
CSRFProtect(app)


# 开发环境配置
class DevelopConfig(Config):
    pass


# 生产环境配置
class ProductConfig(Config):
    DEBUG = False


# 测试环境配置
class TestConfig(Config):
    pass


# 提供统一的访问路口
config_dict = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'test': TestConfig
}
