from flask import Blueprint

# 创建蓝图
index_blue = Blueprint('index', __name__)

# 导入views文件装饰视图函数
# from info.modules.index import views
from . import views
