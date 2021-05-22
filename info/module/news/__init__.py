from flask import Blueprint
# 1.创建蓝图
new_detail_bp = Blueprint("new_detail_bp",__name__,url_prefix="/news")
from .views import *