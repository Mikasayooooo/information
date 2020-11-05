from flask import current_app, jsonify, render_template, abort, session, g,request

from info.models import News, User
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


# 收藏功能接口
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数: news_id,action,g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    '''
    1.判断用户是否登录
    2.获取参数
    3.参数校验,为空校验
    4.操作类型校验
    5.根据新闻的编号取出新闻对象
    6.判断新闻对象是否存在
    7.根据操作类型,进行收藏&取消收藏操作
    8.返回响应
    :return:
    '''

    # 1.判断用户是否登录
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg='用户为登录')

    # 2.获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3.参数校验,为空校验
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4.操作类型校验
    if not action in ['collect','cancel_collect']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型有误')

    # 5.根据新闻的编号取出新闻对象
    try:
       news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻获取失败')

    # 6.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 7.根据操作类型,进行收藏&取消收藏操作
    if action == 'collect':
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        if news in g.user.collection_news:
            g.user.collection_news.remove(news)

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')


# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数: news_id
# 返回值: detail.html 页面,用户data字典数据
@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # # 0. 从session中取出用户的user_id
    # user_id = session.get('user_id')
    #
    # # 0.1 通过user_id取出用户对象
    # user = None
    # try:
    #     # 通过get从数据库获取的需要判断是否为空
    #     user = User.query.get(user_id)
    # except Exception as e:
    #     current_app.logger.error(e)


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

    # 3.获取前6条热门新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 4.将热门新闻的对象列表,转换为字典列表(列表生成式),这里的news和上面的新闻对象重复,
    # 但是,因为是通过列表生成式,所以news的作用域仅限[]
    click_news_list = [news.to_dict() for news in click_news]
    # click_news_list = []
    # for news in click_news_list:
    #     click_news_list.append(news.to_dict())


    # 5.判断用户是否收藏过该新闻
    is_collected = False
    # 用户需要登陆,并且该新闻在用户收藏过的新闻列表中
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 6.携带数据,渲染页面
    data = {
        # 从数据库中通过 get 获取,如果不存在,就会报错,需要进行判断
        # 第一种方式:
        # 'news_info':news.to_dict() if news else ''
        'news_info': news.to_dict() if news else '',
        'user_info': g.user.to_dict() if g.user else '',
        'news': click_news_list,
        #     user_info  和 news  必须和 base.html一一对应
        'is_collected':is_collected
    }

    return render_template('news/detail.html', data=data)
