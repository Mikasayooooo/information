from flask import Blueprint

# 创建蓝图
admin_blue = Blueprint('admin', __name__,url_prefix='/admin')

# 导入views文件装饰视图函数
# from info.module.index import views
from . import views
