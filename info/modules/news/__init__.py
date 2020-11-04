from flask import Blueprint

# 创建蓝图
news_blue = Blueprint('news', __name__, url_prefix='/news')

# 导入views文件装饰视图函数
from . import views
