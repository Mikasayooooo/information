from flask import session, render_template, jsonify, request, g
from sqlalchemy import text

from info.utils.commons import user_login_data
from . import index_blue
import logging
from flask import current_app

from info.models import User, News, Category
from info.utils.response_code import RET


# 首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blue.route('/newslist')
def newslist():
    """
    1. 获取参数
    2. 参数类型转换
    3. 分页查询
    4. 获取到分页对象中的属性,总页数,当前页,当前页的对象列表
    5. 将对象列表转成字典列表
    6. 携带数据,返回响应
    :return:
    """

    #     1. 获取参数
    cid = request.args.get('cid')  # 这获取到的是字符串
    page = request.args.get('page')  # 这获取到的是字符串
    per_page = request.args.get('per_page')  # 这获取到的是字符串
    print(type(cid))
    print(type(page))
    print(type(per_page))
    # <class 'str'>

    #     2. 参数类型转换
    try:
        page = int(page)  # 如果传过来的值不能转成数字型,报错
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10


    #     3. 分页查询
    try:
        #  查询新闻 条件(新闻分类的id=cid),并且通过(新闻的创建时间降序排,最新的数据,时间越大,所以排在最前面),
        # 然后进行分页(self, page=None(哪一页), per_page=None(每页有多少条), error_out=True(查不到不报错), max_per_page=None)

        # 判断新闻的分类是否为1
        # 这里注意: cid 为字符串 !!!
        # 第一种方式:
        # if cid == '1':
        #     paginate = News.query.filter().order_by(News.create_time.desc()).paginate(page, per_page,False)
        # else:
        #     paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page,False)

        # 第二种方式:
        # filters = ''
        # if cid != '1':
        #     filters = (News.category_id == cid)
        # paginate = News.query.filter(text(filters)).order_by(News.create_time.desc()).paginate(page, per_page,False)

        # 第三种方式: (推荐)
        filters = []
        if cid != '1':
            # 以后可以加其他条件,灵活
            filters.append(News.category_id == cid)
            #     再进行拆包  *filters
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    #     4. 获取到分页对象中的属性,总页数,当前页,当前页的对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    #     5. 将对象列表转成字典列表
    news_list = [news.to_dict() for news in items]

    #     6. 携带数据,返回响应
    return jsonify(errno=RET.OK, errmsg='获取新闻成功', totalPage=totalPage, currentPage=currentPage, newsList=news_list)



@index_blue.route('/', methods=["GET", "POST"])
@user_login_data
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

    # 首页右上角信息显示

    # # 1. 获取用户的登录信息
    # user_id = session.get('user_id')
    # print(user_id)
    # # 2. 通过user_id取出用户对象
    # user = None
    # try:
    #     user = User.query.get(user_id)
    # except Exception as e:
    #     current_app.logge.error(e)

    # 3. 查询热门新闻,根据点击量,查询前十条新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4. 将新闻对象列表转成 字典列表
    news_list = [item.to_dict() for item in news]

    # 5.查询所有的分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

    # 6. 将分类对象列表转成 字典列表
    categories_list = [categorie.to_dict() for categorie in categories]

    # 7. 拼接用户数据,渲染页面
    data = {
        # 如果user有值,返回左边的内容,否则返回右边的内容
        'user_info': g.user.to_dict() if g.user else '',
        'news': news_list,
        'categories_list': categories_list
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



# 统一的返回404页面
@index_blue.route('/404')
@user_login_data
def page_not_found():
    data = {
        'user_info': g.user.to_dict() if g.user else ''
    }
    return render_template('news/404.html',data=data)
