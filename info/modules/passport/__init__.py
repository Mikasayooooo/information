from flask import Blueprint

# 创建蓝图对象
passport_blue = Blueprint('passport', __name__, url_prefix='/passport')

# 导入views装饰视图函数
from . import views
