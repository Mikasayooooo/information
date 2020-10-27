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


if __name__ == '__main__':
    print(app.url_map)  # 查看所有映射路径
    manager.run()
