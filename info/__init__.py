import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, session, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf.csrf import CSRFProtect,generate_csrf
from redis import StrictRedis
from config import config_dict
from info.utils.common import set_rank_class, user_login_data

# 创建app对象
db=SQLAlchemy()
#None+#type:声明属性类型
redis_store=None # type: StrictRedis
def set_log(config_class):
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
def create_app(config_dev_mode):
    app=Flask(__name__)
    config_class=config_dict[config_dev_mode]
    set_log(config_class.LOG_LEVEL)
    app.config.from_object(config_class)
    db.init_app(app)
    global redis_store
    redis_store=StrictRedis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT,decode_responses=True)
    CSRFProtect(app)
    @app.after_request
    def set_csrf_token(response):
        csrf_token=generate_csrf()
        response.set_cookie("csrf_token",csrf_token)
        return response
    Session(app)
    app.add_template_filter(set_rank_class,"set_rank_class")
    @app.errorhandler(404)
    @user_login_data
    def handler_404(e):
        data={
            "user_info":g.user.to_dict()if g.user else None
        }
        return render_template("news/404.html",data=data)
    #延迟导入解决循环导入问题
    from info.module.index import index_bp
    app.register_blueprint(index_bp)
    from info.module.passport import passport_bp
    app.register_blueprint(passport_bp)
    from info.module.news import new_detail_bp
    app.register_blueprint(new_detail_bp)
    from info.module.profile import profile_bp
    app.register_blueprint(profile_bp)
    from info.module.admin import admin_bp
    app.register_blueprint(admin_bp)
    return app