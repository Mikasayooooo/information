from datetime import timedelta
import logging

from redis import StrictRedis


class Config(object):
    DEBUG = True
    SECRET_KEY = 'FSFSVVFGFGWEYDCXZVZB'

    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.36.130:3306/info'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session
    SESSION_TYPE = 'redis'  # 设置session存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True  # 设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)  # 设置session过期时间

    # 默认的日志级别
    LEVEL_NAME = logging.DEBUG

# 开发环境配置
class DevelopConfig(Config):
    pass


# 生产环境配置
class ProductConfig(Config):
    DEBUG = False
    LEVEL_NAME = logging.ERROR


# 测试环境配置
class TestConfig(Config):
    pass


# 提供统一的访问路口
config_dict = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'test': TestConfig
}
