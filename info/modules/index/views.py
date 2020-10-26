from flask import session
from . import index_blue
import logging
from flask import current_app


@index_blue.route('/', methods=["GET", "POST"])
def hello_world():
    # 测试redis存取数据
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))

    # 测试session存取
    # session["name"] = "zhangsan"
    # print(session.get("name"))

    # 使用日志记录方法logging进行输出可控
    logging.debug('输入调试信息')
    logging.info('输入详细信息')
    logging.warning('输入警告信息')
    logging.error('输入错误信息')

    # 也可以用current_app输出日志信息输出的时候有分割线,写在文件中完全一样
    # current_app.logger.debug('输入调试信息2')
    # current_app.logger.info('输入详细信息2')
    # current_app.logger.warning('输入警告信息2')
    # current_app.logger.error('输入错误信息2')

    return "helloworld"
