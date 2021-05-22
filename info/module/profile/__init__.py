from flask import Blueprint
# 1.创建蓝图
profile_bp = Blueprint("user",__name__,url_prefix="/user")
from .views import *