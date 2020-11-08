from flask import render_template, g,redirect
from  . import profile_blue
from info.utils.commons import user_login_data


@profile_blue.route('/info')
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