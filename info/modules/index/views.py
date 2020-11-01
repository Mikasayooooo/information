from flask import session, render_template, jsonify
from . import index_blue
import logging
from flask import current_app

from info.models import User, News
from info.utils.response_code import RET


@index_blue.route('/', methods=["GET", "POST"])
def show_index():
    # 测试redis存取数据
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))

    # 测试session存取
    # session["name"] = "zhangsan"
    # print(session.get("name"))

    # 使用日志记录方法logging进行输出可控
    # logging.debug('输入调试信息')
    # logging.info('输入详细信息')
    # logging.warning('输入警告信息')
    # logging.error('输入错误信息')

    # 也可以用current_app输出日志信息输出的时候有分割线,写在文件中完全一样
    # current_app.logger.debug('输入调试信息2')
    # current_app.logger.info('输入详细信息2')
    # current_app.logger.warning('输入警告信息2')
    # current_app.logger.error('输入错误信息2')

    # 的\右上角信息显示

    # 1. 获取用户的登录信息
    user_id = session.get('user_id')
    print(user_id)
    # 2. 通过user_id取出用户对象
    user = None
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logge.error(e)

    # 3. 查询热门新闻,根据点击量,查询前十条新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4. 将新闻对象列表转成 字典列表
    news_list = [item.to_dict() for item in news]

    # 5. 拼接用户数据,渲染页面
    data = {
        # 如果user有值,返回左边的内容,否则返回右边的内容
        'user_info': user.to_dict() if user else '',
        'news': news_list
    }
    print(data)
    # data2 = [
    #     {'user_info2': user.to_dict() if user else ''}
    # ]
    # print(data2)

    return render_template('news/index.html', data=data)


# 网站logo展示,路径 必须是/favicon.ico,自动加载的
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')
# current_app.send_static_file  默认是在静态文件夹下自动加载的
