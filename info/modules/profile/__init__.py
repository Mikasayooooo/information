from flask import Blueprint
# 创建蓝图
profile_blue = Blueprint('profile', __name__,url_prefix='/user')

# 导入views文件装饰视图函数
# from info.module.index import views
from . import views
