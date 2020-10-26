from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from config import config_dict

from info.modules.index import index_blue

import logging
from logging.handlers import RotatingFileHandler

# 定义redis_store全局变量
redis_store = None

# 工厂方法
def create_app(config_name):

    app = Flask(__name__)

    # 根据传入的配置类名称,取出对应的类
    config = config_dict.get(config_name)

    # 调用日志方法,记录程序运行信息
    log_file(LEVEL_NAME=config.LEVEL_NAME)

    # 设置配置类
    app.config.from_object(config)

    # 创建数据库对象
    db = SQLAlchemy(app)

    global redis_store  # global声明全局变量
    # 创建redis对象
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)  # 转成字节码

    # 创建session对象
    Session(app)

    # 开启csrf保护
    CSRFProtect(app)

    # 将首页蓝图index_blue注册到app中
    app.register_blueprint(index_blue)

    return app


def log_file(LEVEL_NAME):
    # 设置日志的记录等级,常见的有四种,大小关系如下:ERROR > WARNING > INFO > DEBUG
    logging.basicConfig(level=LEVEL_NAME)  # 调试debug级,一旦设置级别大于等于该级别的信息全部都会输出
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
