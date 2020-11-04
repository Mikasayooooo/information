from flask import current_app, jsonify, render_template, abort

from info.models import News
from info.utils.response_code import RET
from . import news_blue


# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数: news_id
# 返回值: detail.html 页面,用户data字典数据
@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    # 1.根据新闻编号,查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 2.如果新闻对象不存在直接抛出异常
    # 第二种方式:(推荐),能通过errhandler捕捉
    if not news:
        abort(404)

    # 3.携带数据,渲染页面
    data = {
        # 从数据库中通过 get 获取,如果不存在,就会报错,需要进行判断
        # 第一种方式:
        # 'news_info':news.to_dict() if news else ''
        'news_info': news.to_dict() if news else ''
    }

    return render_template('news/detail.html', data=data)
