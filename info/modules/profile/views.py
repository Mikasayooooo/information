
from flask import render_template, g, redirect, request, jsonify, current_app

from info.models import News,Category
from info.utils.response_code import RET
from . import profile_blue
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info import constants, db



# 获取用户新闻列表
# 请求路径: /user/news_list
# 请求方式: GET
# 请求参数: p(页数)
# 返回值: user_news_list.html页面
@profile_blue.route('/news_list')
@user_login_data
def news_list():
    '''
    1.获取参数，p(页数)
    2.参数类型转换
    3.分页查询用户发布的新闻
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

    # 3.分页查询收藏的新闻
    try:
       paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取新闻失败')

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
    return render_template('news/user_news_list.html',data=data)





# 获取/设置新闻发布
# 请求路径: /user/news_release
# 请求方式: GET,POST
# 请求参数: GET无，POST请求有参数，title,category_id,digest,index_image,content
# 返回值: GET请求，user_news_release.html页面，data分类列表字段数据，POST，errno,errmsg
@profile_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    '''
    1.判断请求方式，如果是GET
    2.携带分类数据渲染页面
    3.如果是POST，获取参数
    4.校验参数，为空校验
    5.上传图片，判断是否上传成功
    6.创建新闻对象，设置属性
    7.保存到数据库
    8.返回响应
    :return:
    '''

    # 1.判断请求方式，如果是GET
    if request.method == 'GET':
        # 2.查询所有的分类数据
        try:
           categories = Category.query.all()  # 这是对象数组需要转换成字典数组
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='获取分类失败')

        # 这是对象数组需要转换成字典数组
        category_list = [category.to_dict() for category in categories]

        # 2.1携带分类数据渲染页面
        return render_template('news/user_news_release.html',category_list=category_list)

    # 3.如果是POST，获取参数
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')

    '''
    request.args    获取get请求传递的参数
    request.data    获取json参数
    request.form    获取表单参数
    request.files   获取二进制数据
    '''
    print(title)
    print(category_id)
    print(digest)
    print(index_image)
    print(content)

    # 4.校验参数，为空校验
    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 5.上传图片，判断是否上传成功
    try:
       #  读取图片为二进制数据，上传
       image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 6.创建新闻对象，设置属性
    news = News()
    news.title = title  #新闻标题
    news.source = g.user.nick_name #新闻来源
    news.digest = digest  # 新闻摘要
    news.content = content  # 新闻内容
    news.content = content  # 新闻内容
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name  # 新闻列表图片路径
    news.category_id = category_id
    news.user_id = g.user.id  # 当前新闻的作者id
    news.status = 1     # 当前新闻状态,如果为0代表审核通过，1代表审核中，-1代表审核不通过

    # 7.保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻发布失败')

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg='上传成功')




# 获取新闻收藏列表
# 请求路径: /user/collection
# 请求方式: GET
# 请求参数: p(页数)
# 返回值: user_collection.html页面
@profile_blue.route('/collection')
@user_login_data
def collection():
    '''
    1.获取参数，p(页数)
    2.参数类型转换
    3.分页查询收藏的新闻
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

    # 3.分页查询收藏的新闻
    try:
       paginate = g.user.collection_news.order_by(News.create_time.desc()).paginate(page,2,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取新闻失败')

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = [news.to_dict() for news in items]

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list
    }
    return render_template('news/user_collection.html',data=data)





# 获取/设置用户密码
# 请求路径: /user/pass_info
# 请求方式: GET,POST
# 请求参数: GET无，POST请求有参数，old_password,new_password
# 返回值: GET请求：user_pass_info.html页面， POST请求： errno,errmsg
@profile_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    '''
    1.判断请求方式，如果是get请求
    2.直接渲染页面
    3.如果是post请求，获取参数
    4.校验参数，为空校验
    5.判断老密码是否正确
    6.设置新密码
    7.返回响应
    :return:
    '''

    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.直接渲染页面
        return render_template('news/user_pass_info.html')

    # 3.如果是post请求，获取参数
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    # 4.校验参数，为空校验
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 5.判断老密码是否正确
    if not g.user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg='老密码错误')

    # 7.设置新密码
    g.user.password = new_password

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')


# 获取/设置用户头像上传
# 请求路径: /user/pic_info
# 请求方式: GET,POST
# 请求参数: GET无，POST请求有参数，avatar
# 返回值: GET请求：user_pic_info.html页面，data字典数据 ， POST请求： errno,errmsg，avatar_url
@profile_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    '''
    1.判断请求方式，如果是get请求
    2.携带用户数据，渲染页面
    3.如果是post请求
    4.获取参数
    5.校验参数，为空校验
    6.上传图像，判断图片是否上传成功
    7.将图片设置到用户对象
    8.返回响应
    :return:
    '''

    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.携带用户数据，渲染页面
        return render_template('news/user_pic_info.html', user_info=g.user.to_dict())

    # 3.如果是post请求
    # 4.获取参数
    print(request)
    # return 'ok'
    avatar = request.files.get('avatar')

    # 5.校验参数，为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='图片不能为空')

    # 6.上传图像，判断图片是否上传成功
    try:
        # print('avatar-------------->',avatar)
        # print('avatar.read-------------->',avatar.read())
        # 读取图片为二进制文件，上传图片
        image_name = image_storage(avatar.read())
        # print('image_name-------------->',image_name)
    except Exception as e:
        current_app.logger.error(e)
        # THIRDERR 第三方错误
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 7.将图片设置到用户对象
    g.user.avatar_url = image_name

    # 8.返回响应
    data = {
        # 头像路径拼接，七牛云外链
        'avatar_url': constants.QINIU_DOMIN_PREFIX + image_name
    }
    # 前端需要data参数
    return jsonify(errno=RET.OK, errmsg='上传成功', data=data)


# 获取/设置用户基本信息
# 请求路径: /user/base_info
# 请求方式: GET,POST
# 请求参数: POST请求有参数，nick_name,signature,gender
# 返回值: errno,errmsg
@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    '''
    1.判断请求方式，如果是get请求
    2.携带用户数据，渲染页面
    3.如果是post请求
    4.获取参数
    5.校验参数，为空校验
    6.修改用户的数据
    7.返回响应
    :return:
    '''
    # 1. 判断请求方式,如果是get请求
    if request.method == "GET":
        # 2. 携带用户数据,渲染页面
        return render_template("news/user_base_info.html", user_info=g.user.to_dict())

    # 3. 如果是post请求
    # 4. 获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 5. 校验参数,为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")

    # 6. 修改用户的数据
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 获取用户信息首页
# 请求路径: /user/info
# 请求方式: GET
# 请求参数: 无
# 返回值: user,html页面，用户字典data数据
@profile_blue.route('/info', methods=['GET'])
@user_login_data
def user_index():
    # 1. 判断用户是否登录
    if not g.user:
        return redirect('/')

    # 2. 携带数据渲染页面
    data = {
        'user_info': g.user.to_dict()
    }
    return render_template('news/user.html', data=data)
