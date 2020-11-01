from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import config_dict


import logging
from logging.handlers import RotatingFileHandler

from info.utils.commons import hot_news_filter

# 定义redis_store全局变量
redis_store = None

# 定义db全局变量
db = SQLAlchemy()

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
    db.init_app(app)

    global redis_store  # global声明全局变量
    # 创建redis对象
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)  # 转成字节码

    # 创建session对象
    Session(app)

    # 开启csrf保护
    CSRFProtect(app)

    # 解决循环导入的问题
    from info.modules.index import index_blue
    from info.modules.passport import passport_blue

    # 将首页蓝图index_blue,注册到app中
    app.register_blueprint(index_blue)
    # 将认证蓝图password_blue,注册到app中
    app.register_blueprint(passport_blue)

    # 将函数添加到系统默认的过滤器中
    # 参数1: 函数的名字 参数2: 过滤器的名字
    app.add_template_filter(hot_news_filter, 'hot_news_filter')

    # 使用请求钩子拦截所有的请求,通过在cookie中设置csrf_token
    @app.after_request
    def after_request(resp):
        # resp.set_cookie('name', 'lhl')

        # 调用系统方法,获取csrf_token
        csrf_token = generate_csrf()

        # 将csrf_token设置到cookie中
        resp.set_cookie('csrf_token', csrf_token)

        # 返回响应
        return resp

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
