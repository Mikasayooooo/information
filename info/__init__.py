from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from config import config_dict


# 工厂方法
def create_app(config_name):
    app = Flask(__name__)

    # 根据传入的配置类名称,取出对应的类
    config = config_dict.get(config_name)

    # 设置配置类
    app.config.from_object(config)

    # 创建数据库对象
    db = SQLAlchemy(app)

    # 创建redis对象
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)  # 转成字节码

    # 创建session对象
    Session(app)

    # 开启csrf保护
    CSRFProtect(app)

    return app
