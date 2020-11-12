from info import create_app, db, models  # 导入models是让整个应用程序知道有这个models的存在
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate

# 调用方法,获取app
app = create_app('develop')

# 创建manager对象,管理app
manager = Manager(app)

# 使用Migrate关联app,db
migrate = Migrate(app, db)

# 给manager添加一条操作命令
manager.add_command('db', MigrateCommand)

from info.models import User
from flask import current_app

from datetime import datetime,timedelta
import random


# 定义方法，创建管理员对象
'''
@manager.option 给 manager 添加一个脚本运行的方法
参数1：在调用方法的时候传递的参数名称
参数2：是对参数1的解释
参数3：目的参数，用来传递给形式参数使用的
'''
@manager.option('-u','--username',dest='username')
@manager.option('-p','--password',dest='password')
def create_supper(username,password):

    # 1.创建用户对象
    admin = User()

    # 2.设置用户属性
    admin.nick_name = username
    admin.mobile = username
    admin.password =  password
    admin.is_admin = True

    # 3.保存到数据库
    try:
       db.session.add(admin)
       db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return '创建失败'
    return '创建成功'



# 为了图表好看，添加测试用户
@manager.option('-t','--test',dest='test')
def add_test_user(test):

    # 1.定义容器
    user_list = []

    # 2.for循环创建1000个用户
    for i in range(0,1000):
        user = User()
        user.nick_name = '老王-{}'.format(i)
        user.mobile = '199%08d' %i
        user.password_hash = 'pbkdf2:sha256:50000$rsZ5svCR$b73f6a510cbd5e535c08f278954ca6beb1449095fb62abf4eba664cb5c6b9c8a'
        # 设置用户的登陆时间为近31天
        user.last_login = datetime.now() - timedelta(seconds=random.randint(0,31*24*3600))

        user_list.append(user)

    # 3.将用户添加到数据库中
    try:
       db.session.add_all(user_list)
       db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return '添加测试用户失败'
    return '添加测试用户成功'



if __name__ == '__main__':
    print(app.url_map)  # 查看所有映射路径
    import sys

    print(sys.path)

    # create_supper()  不能直接在这里创建，会泄露用户名，密码，不安全，从shell中创建

    manager.run()
