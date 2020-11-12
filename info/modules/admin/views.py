from info.models import User
from . import admin_blue
from flask import render_template, request, current_app, session, redirect, g

from info.utils.commons import user_login_data

import time
from datetime import datetime,timedelta



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
