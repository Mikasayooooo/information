from flask import render_template, g,redirect,request,jsonify

from info.utils.response_code import RET
from  . import profile_blue
from info.utils.commons import user_login_data



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
    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.携带用户数据，渲染页面
        #  这里不用判断用户是否存在，因为在 获取用户信息首页 时已经校验过了
        return render_template('news/user_base_info.html',user_info=g.user.to_dict())

    # 3.如果是post请求
    # 4.获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    # 5.校验参数，为空校验
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    if not gender in ['MAN','WOMAN']:
        return jsonify(errno=RET.DATAERR, errmsg='性别异常')

    # 6.修改用户的数据
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')



# 获取用户信息首页
# 请求路径: /user/info
# 请求方式: GET
# 请求参数: 无
# 返回值: user,html页面，用户字典data数据
@profile_blue.route('/info',methods=['GET'])
@user_login_data
def user_index():

    # 1. 判断用户是否登录
    if not g.user:
        return redirect('/')

    # 2. 携带数据渲染页面
    data = {
        'user_info':g.user.to_dict()
    }
    return render_template('news/user.html',data=data)