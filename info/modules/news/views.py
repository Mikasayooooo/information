from flask import current_app, jsonify, render_template, abort, session, g, request

from info import db
from info.models import News, User, Comment, CommentLike
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


# 评论点赞
# 请求路径: /news/comment_like
# 请求方式: POST
# 请求参数: news_id(可以不传),comment_id,g.user,action
# 返回值: errno,errmsg
@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    '''
    1.判断用户是否登陆
    2.获取请求参数
    3.校验参数,为空校验
    4.操作类型进行校验
    5.通过评论编号查询评论对象，并判断是否存在
    6.根据操作类型点赞取消点赞
    7.返回响应
    :return:
    '''

    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2.获取请求参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 3.校验参数,为空校验
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4.操作类型进行校验
    if not action in ['add', 'remove']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型 有误')

    # 5.通过评论编号查询评论对象，并判断是否存在
    try:
        # comment = Comment.query.filter(Comment.id == comment_id)  错误
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论获取失败')

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论不存在')

    # 6.根据操作类型点赞取消点赞
    try:

        if action == 'add':
            # 6.1 判断用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment_id).first()
            if not comment_like:
                # 创建点赞对象
                comment_like = CommentLike()
                comment_like.user_id = g.user.id
                comment_like.comment_id = comment_id

                # 添加到数据库中
                db.session.add(comment_like)

                # 将该评论数量 加1
                comment.like_count += 1

                # 数据库自动提交有一定的延时性，加入用户暴力点击，就会出现问题
                db.session.commit()

        else:
            # 6.1 判断用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment_id).first()
            if comment_like:
                # 删除点赞对象
                db.session.delete(comment_like)

                # 将该评论数量 减1
                if comment.like_count > 0:
                    comment.like_count -= 1

                # 数据库自动提交有一定的延时性，加入用户暴力点击，就会出现问题
                db.session.commit()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='操作失败')

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')


# 新闻评论后端
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数: news_id,comment,g.user,parent_id
# 返回值: errno,errmsg,评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    '''
    1.判断用户是否登陆
    2.获取请求参数
    3.校验参数,为空校验
    4.根据新闻编号取出新闻对象,判断新闻是否存在
    5.创建评论对象,设置属性
    6.保存评论对象到数据库中
    7.返回响应,携带评论的数据
    :return:
    '''

    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2.获取请求参数
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3.校验参数,为空校验
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4.根据新闻编号取出新闻对象,判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻获取失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 5.创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    # 父评论可能没有
    if parent_id:
        comment.parent_id = parent_id

    # 6.保存评论对象到数据库中
    try:
        db.session.add(comment)
        db.session.commit()
        # 因为前面已经设置过了数据库自动提交,所以这句话可以不写
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论失败')

    # 7.返回响应,携带评论的数据
    return jsonify(errno=RET.OK, errmsg='评论成功', data=comment.to_dict())


# 收藏功能接口
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数: news_id,action,g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
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
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2.获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3.参数校验,为空校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4.操作类型校验
    if not action in ['collect', 'cancel_collect']:
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
        return jsonify(errno=RET.DBERR, errmsg='获取热门新闻失败')

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

    # 6.查询数据库中,该新闻的所有评论内容
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取评论失败')

    # 6.1 用户点赞过的评论编号
    try:
        # 因为 获取  该用户点过的所有赞  查询语句时,使用到了g.user 这个属性, 所以需要提前判断是否存在;
        # 但由于  commentlikes 放在了if语句里面,变成了局部变量,如果 g.user不存在
        #  查询  获取用户所有点赞过的评论编号  里面用到的  commentlikes 就会变成 None ,会报错,
        # 所有需要将  commentlikes  定义成全局变量
        commentlikes = []
        if g.user:
            # 6.1.1 该用户点过的所有赞
            commentlikes = CommentLike.query.filter(CommentLike.user_id == g.user.id).all()

        # 6.1.2 获取用户所有点赞过的评论编号
        mylike_comment_ids = [commentLike.comment_id for commentLike in commentlikes]

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取点赞失败')

    # 7.将评论对象列表转换成字典列表
    # comments_list = [comment.to_dict() for comment in comments]
    comments_list = []
    for comment in comments:
        # 将评论对象,转字典
        comm_dict = comment.to_dict()

        # 添加is_like记录点赞
        comm_dict['is_like'] = False

        # 判断用户是否有对评论点过赞
        # 首先判断用户是否存在，然后在判断 评论编号 是否 在 用户点赞过的评论列表里
        if g.user and comment.id in mylike_comment_ids:
            comm_dict['is_like'] = True

        comments_list.append(comm_dict)

    # 8.携带数据,渲染页面
    data = {
        # 从数据库中通过 get 获取,如果不存在,就会报错,需要进行判断
        # 第一种方式:
        # 'news_info':news.to_dict() if news else ''
        'news_info': news.to_dict() if news else '',
        'user_info': g.user.to_dict() if g.user else '',
        'news': click_news_list,
        #     user_info  和 news  必须和 base.html一一对应
        'is_collected': is_collected,
        'comments_list': comments_list
    }

    return render_template('news/detail.html', data=data)
