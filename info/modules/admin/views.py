from info.models import User, News,Category
from . import admin_blue
from flask import render_template, request, current_app, session, redirect, g,jsonify

from info.utils.commons import user_login_data

import time
from datetime import datetime,timedelta

from info.utils.response_code import RET

from info.utils.image_storage import image_storage
from info import constants, db


# 新闻分类添加/修改
# 请求路径: /admin/add_category
# 请求方式: POST
# 请求参数: id,name
# 返回值: errno,errmsg
@admin_blue.route('/add_category', methods=['POST'])
def add_category():
    '''
    1.获取参数,id,name
    2.参数校验，为空校验
    3.根据是否有id，来判断是新增还是编辑
    4.返回响应
    :return:
    '''

    # 1.获取参数,id,name
    category_id = request.json.get('id')
    category_name = request.json.get('name')

    # 2.参数校验，为空校验
    if not category_name:
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    # 3.根据是否有id，来判断是新增还是编辑
    if category_id:  # 编辑

        #3.1 通过分类编号取出分类对象，并判断分类对象是否存在
        try:
           category = Category.query.filter(Category.id == category_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

        if not category_id:
            return jsonify(errno=RET.NODATA, errmsg='该分类不存在')

        # 修改分类的名称
        category.name = category_name

    else:  # 新增

        # 3.3 创建分类对象,设置名称
        category = Category(name=category_name)

        # 3.4 添加分类到数据库中
        try:
           db.session.add(category)
           db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='分类新增失败')

    # 4.返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')




# 新闻分类管理
# 请求路径: /admin/news_category
# 请求方式: GET
# 请求参数: GET,无
# 返回值: GET,news_type.html页面，data字典数据
@admin_blue.route('/news_category')
def news_category():
    '''
    1.获取所有的分类对象
    2.直接携带数据渲染页面
    :return:
    '''

    # 1.获取所有的分类对象
    try:
       categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/news_type.html',errmsg='获取分类失败')

    # 2.直接携带数据渲染页面      这里不需要to_dict(),因为没有进行二次转换
    return render_template('admin/news_type.html', categories=categories)




# 获取/设置新闻版式编辑详情
# 请求路径: /admin/news_edit_detail
# 请求方式: GET,POST
# 请求参数: GET,news_id,POST(news_id,title,digest,content,index_image,category_id)
# 返回值: GET,news_edit_detail.html页面，data字典数据,POST(errno,errmsg)
@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    '''
    1.判断请求方式，如果是GET
    2获取新闻编号
    3.获取新闻对象，并判断新闻对象是否存在
    4.携带新闻数据和分类数据,渲染页面
    5.如果是POST请求，获取参数
    6.参数校验，为空校验
    7.根据编号，获取新闻对象，判断新闻对象是否存在
    8.上传新闻图片
    9.设置新闻对象的属性
    10.返回响应
    :return:
    '''

    # 1.判断请求方式，如果是GET
    if request.method == 'GET':

        # 2获取新闻编号
        news_id = request.args.get('news_id')

        # 3.获取新闻对象，并判断新闻对象是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html',errmsg='获取新闻失败')

        if not news:
            return render_template('admin/news_edit_detail.html', errmsg='该新闻不存在')

        # 3.1 获取分类数据
        try:
           categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg='获取分类失败')

        # 3.2 将分类对象列表数据，转换成字典数据
        category_list = [category.to_dict() for category in categories]

        # 4.携带新闻数据和分类数据,渲染页面
        return render_template('admin/news_edit_detail.html', news=news.to_dict(),category_list=category_list)

    # 5.如果是POST请求，获取参数(news_id,title,digest,content,index_image,category_id)
    news_id = request.form.get('news_id')    # form表单提交使用 request.form.get 来获取
    title = request.form.get('title')
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image = request.files.get('index_image')   # 上传二进制数据使用 request.files.get 来获取
    category_id = request.form.get('category_id')

    # 6.参数校验，为空校验
    if not all([news_id,title,digest,content,index_image,category_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    # 7.根据编号，获取新闻对象，判断新闻对象是否存在
    try:
       news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='该新闻不存在')

    # 8.上传新闻图片
    try:
       image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 9.设置新闻对象的属性
    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id

    # 10.返回响应
    return jsonify(errno=RET.OK, errmsg='编辑成功')




# 获取新闻版式编辑列表
# 请求路径: /admin/news_edit
# 请求方式: GET
# 请求参数: p(页数),keywords
# 返回值: 渲染news_edit.html页面，data字典数据
@admin_blue.route('/news_edit')
def news_edit():
    '''
    1.获取参数，p(页数),keywords
    2.参数类型转换
    3.分页查询 所有新闻数据
    4.获取分页对象属性，总页数，当前页，当前页对象列表
    5.将对象列表，转成字典列表
    6.拼接数据，渲染页面
    :return:
    '''

    # 1.获取参数，p
    page = request.args.get('p', '1')  # 传过来的是字符串,如果p没有，默认设置为1
    keywords = request.args.get('keywords','')  # 从前端获取关键字

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1  # 如果p没有，默认设置为1

    # 3.分页查询 所有新闻数据
    try:

        # 3.1 判断是否有填写搜索关键字
        filters = []  # 查询 所有新闻数据，不需要考虑 审核情况
        if keywords:
            filters.append(News.title.contains(keywords))  # 模糊查询

                                    # 拆包*
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/news_edit.html', errmsg='获取新闻失败')

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = [news.to_review_dict() for news in items]

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list
    }
    return render_template('admin/news_edit.html', data=data)




# 获取/设置新闻审核详情
# 请求路径: /admin/news_review_detail
# 请求方式: GET,POST
# 请求参数: GET,news_id,POST,news_id,action
# 返回值: 渲染news_review_detail.html页面，data字典数据
@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
    '''
    1.判断请求方式，如果是GET
    2获取新闻编号
    3.获取新闻对象，并判断新闻对象是否存在
    4.携带新闻对象的数据渲染页面
    5.如果是POST请求，获取参数
    6.校验操作类型
    7.根据编号，获取新闻对象，判断新闻对象是否存在
    8.根据操作类型改变新闻的状态
    9.返回响应
    :return:
    '''

    # 1.判断请求方式，如果是GET
    if request.method == 'GET':
        # 2获取新闻编号
        news_id = request.args.get('news_id')

        # 3.获取新闻对象，并判断新闻对象是否存在
        try:
           news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_review_detail.html',errmsg='新闻获取失败')

        if not news:
            return render_template('admin/news_review_detail.html', errmsg='该新闻不存在')

        # 4.携带新闻对象的数据渲染页面
        return render_template('admin/news_review_detail.html', news=news.to_dict())

    # 5.如果是POST请求，获取参数
    action = request.json.get('action')
    news_id = request.json.get('news_id')

    # 6.校验操作类型
    if not all([action,news_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    if not action in ['accept','reject']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型有误')

    # 7.根据编号，获取新闻对象，判断新闻对象是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='该新闻不存在')

    # 8.根据操作类型改变新闻的状态
    if action == 'accept':
        news.status = 0
    else:
        news.status = -1
        news.reason = request.json.get('reason','')

    # 9.返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')



# 获取/设置新闻审核列表
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: p(页数)
# 返回值: 渲染news_review.html页面，data字典数据
@admin_blue.route('/news_review')
def news_review():
    '''
    1.获取参数，p(页数)
    2.参数类型转换
    3.分页查询 待审核，未通过的新闻数据
    4.获取分页对象属性，总页数，当前页，当前页对象列表
    5.将对象列表，转成字典列表
    6.拼接数据，渲染页面
    :return:
    '''

    # 1.获取参数，p
    page = request.args.get('p', '1')  # 传过来的是字符串,如果p没有，默认设置为1
    keywords = request.args.get('keywords','')  # 从前端获取关键字

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1  # 如果p没有，默认设置为1

    # 3.分页查询 待审核，未通过的新闻数据
    try:

        # 3.1 判断是否有填写搜索关键字
        filters = [News.status != 0]  # 默认条件
        if keywords:
            filters.append(News.title.contains(keywords))  # 模糊查询

                                    # 拆包*
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/news_review.html', errmsg='获取新闻失败')

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = [news.to_review_dict() for news in items]

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list
    }
    return render_template('admin/news_review.html', data=data)




# 用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p(页数)
# 返回值: 渲染user_list.html页面，data字典数据
@admin_blue.route('/user_list')
def user_list():
    '''
    1.获取参数，p(页数)
    2.参数类型转换
    3.分页查询用户数据
    4.获取分页对象属性，总页数，当前页，当前页对象列表
    5.将对象列表，转成字典列表
    6.拼接数据，渲染页面
    :return:
    '''

    # 1.获取参数，p
    page = request.args.get('p','1')  # 传过来的是字符串,如果p没有，默认设置为1

    # 2.参数类型转换
    try:
       page = int(page)
    except Exception as e:
        page = 1  # 如果p没有，默认设置为1

    # 3.分页查询用户数据
    try:
       paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_list.html',errmsg='获取用户失败')

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    user_list = [user.to_admin_dict() for user in items]

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'user_list': user_list
    }
    return render_template('admin/user_list.html',data=data)




# 用户统计
# 请求路径：/admin/user_count
# 请求方式:GET
# 请求参数：无
# 返回值：渲染页面user_count.html,字典数据
@admin_blue.route('/user_count')
def user_count():
    '''
    1.获取用户总数
    2.获取月活人数
    3.获取日活人数
    4.获取活跃时间段内，对应的活跃人数
    5.携带数据渲染页面
    :return:
    '''

    # 1.获取用户总数
    try:
       #  这里要不需要统计管理员的数量,  filter查询不需要加异常，get需要
       total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html',errmsg='获取总人数失败')

    # 2.获取月活人数
    localtime = time.localtime()
    # print('localtime---------->',localtime)
    '''time.struct_time(tm_year=2020, tm_mon=11, tm_mday=12, 
    tm_hour=18, tm_min=35, tm_sec=46, tm_wday=3, tm_yday=317, tm_isdst=0)'''

    try:
        #2.1先获取本月的1号的0点的，字符串数据
        month_start_time_str = '{}-{}-01'.format(localtime.tm_year,localtime.tm_mon)
        # print('month_start_time_str-----------_____>',month_start_time_str)
        '''2020-11-01'''

        #2.2根据字符串，格式化日期对象
        month_start_time_date = datetime.strptime(month_start_time_str,'%Y-%m-%d')
        # print('month_start_time_date-------------->',month_start_time_date)
        '''2020-11-01 00:00:00'''

        #2.3最后一次登陆的时间大于，本月的1号的0点钟的人数
        month_count = User.query.filter(User.last_login >= month_start_time_date,User.is_admin == False).count()
        #  这里要不需要统计管理员的数量,  filter查询不需要加异常，get需要

    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html',errmsg='获取月活人数失败')

    # 3.获取日活人数
    localtime = time.localtime()

    try:
        # 3.1先获取本日的0点的，字符串数据
        day_start_time_str = '{}-{}-{}'.format(localtime.tm_year, localtime.tm_mon,localtime.tm_mday)

        # 3.2根据字符串，格式化日期对象
        day_start_time_date = datetime.strptime(day_start_time_str, '%Y-%m-%d')

        # 3.3最后一次登陆的时间大于，本日的0点钟的人数
        day_count = User.query.filter(User.last_login >= day_start_time_date,User.is_admin == False).count()
        #  这里要不需要统计管理员的数量,  filter查询不需要加异常，get需要

    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html', errmsg='获取日活人数失败')

    # 4.获取活跃时间段内，对应的活跃人数
    active_date = [] # 获取活跃的日期
    active_count = [] # 获取活跃的人数
    for i in range(0,31):

        # 当天开始时间A
        begin_date = day_start_time_date - timedelta(days=i)

        # 当天开始时间，的后一天B
        end_date = day_start_time_date - timedelta(days=i - 1)

        # 添加当天开始时间字符串到活跃日期中    (日期对象转换成字符串)
        active_date.append(begin_date.strftime('%Y-%m-%d'))

        # 查询时间A到B这一天的注册人数
        everyday_active_count = User.query.filter(User.is_admin == False,User.last_login >= begin_date,User.last_login <= end_date).count()

        # 添加当天注册人数到 获取数量中
        active_count.append(everyday_active_count)

    # 为了图表显示方便，将容器反转
    active_date.reverse()
    active_count.reverse()

    # 5.携带数据渲染页面
    data = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count
    }
    return render_template('admin/user_count.html',data=data)




# 首页
# 请求路径：/admin/index
# 请求方式:GET
# 请求参数：无
# 返回值：渲染页面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    data = {
        'user_info':g.user.to_dict() if g.user else ''
    }
    return render_template('admin/index.html',data=data)



# 获取/登录，管理员登录
# 请求路径：/admin/login
# 请求方式:GET,POST
# 请求参数：GET,无，POST，username,password
# 返回值：GET渲染login.html页面,POST,login.html页面,errmsg
@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    '''
    1.判断请求方式，如果是GET，直接渲染页面
    2.如果是POST，获取参数
    3.校验参数，为空校验
    4.根据用户名取出管理员对象，判断管理员是否存在
    5.判断管理员的密码是否正确
    6.管理员的session信息记录
    7.重定向到首页展示
    :return:
    '''

    # 1.判断请求方式，如果是GET，直接渲染页面
    if request.method == 'GET':

        # 判断管理员是否已经登录过了，如果登录过了，直接跳转到首页
        if session.get('is_admin'):
            return redirect('/admin/index')

        return render_template('admin/login.html')

    # 2.如果是POST，获取参数
    username = request.form.get('username')
    password = request.form.get('password')

    # 3.校验参数，为空校验
    if not all([username,password]):
        return render_template('admin/login.html',errmsg='参数不全')

    # 4.根据用户名取出管理员对象，判断管理员是否存在
    try:
       admin = User.query.filter(User.mobile == username,User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html',errmsg='用户查询失败')

    if not admin:
        return render_template('admin/login.html',errmsg='管理员不存在')

    # 5.判断管理员的密码是否正确
    if not admin.check_password(password):
        return render_template('admin/login.html', errmsg='密码错误')

    # 6.管理员的session信息记录
    session['user_id'] = admin.id
    session['is_admin'] = True

    # 7.重定向到首页展

    return redirect('/admin/index')
