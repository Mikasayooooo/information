from datetime import timedelta

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)


class Config(object):

    DEBUG = True
    SECRET_KEY = 'FSFSVVFGFGWEYDCXZVZB'

    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.36.129:3306/info'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session
    SESSION_TYPE = 'redis' # 设置session存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT) # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True  # 设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)  # 设置session过期时间




app.config.from_object(Config)

db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True) # 转成字节码

# 创建session对象
Session(app)

# 开启csrf保护
CSRFProtect(app)

@app.route('/')
def hello_world():
    # 测试redis
    redis_store.set('name','lhl')
    print(redis_store.get('name'))

    # 测试session
    session['name'] = 'wzy'
    print(session.get('name'))
    return 'ok'


if __name__ == '__main__':
    app.run()

