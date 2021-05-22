from flask import current_app, abort, request, Blueprint
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# from info import create_app,db
# import sqlalchemy
#0.自定义的项目配置类
from info.models import User
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, session, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf.csrf import CSRFProtect,generate_csrf
from redis import StrictRedis
from config import config_dict
from info.utils.common import set_rank_class, user_login_data

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from info import constants

import pymysql
pymysql.install_as_MySQLdb()





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

app=create_app("development")
manager=Manager(app)
Migrate(app,db)
manager.add_command("db",MigrateCommand)



admin_bp=Blueprint("admin",__name__,url_prefix="/admin")
@admin_bp.route("/news_review")
def user_list(news_review):
    p=request.json.get("p",1)
    keywords=request.args.get("keywords")
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        p=1
    user_list=[]
    current_page=1
    total_page=1
    filter_list=[News.status!=0]
    if keywords:
        filter_list.append(News.title.contains(keywords))
    try:
        paginate=User.query.filter(*filter_list).order_by(User.last_login.desc()).paginate(p,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news_list=paginate.items
        current_page=paginate.page
        total_page=paginate.pages
    except Exception as e:
        current_app.loger.error(e)
        return abort(404)
    news_dict_list=[]
    for news in news_list if news_list else None:
        news_dict_list.append(news.to_review_dict())
    data={
        "news_list":news_dict_list,
        "current_page":current_page,
        "total_page":total_page
    }
    return render_template("admin/news_review.html",data=data)


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


# 用户收藏表，建立用户与其收藏新闻多对多的关系
tb_user_collection = db.Table(
    "info_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("info_user.id"), primary_key=True),  # 新闻编号
    db.Column("news_id", db.Integer, db.ForeignKey("info_news.id"), primary_key=True),  # 分类编号
    db.Column("create_time", db.DateTime, default=datetime.now)  # 收藏创建时间
)

tb_user_follows = db.Table(
    "info_user_fans",
    db.Column('follower_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True),  # 粉丝id
    db.Column('followed_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True)  # 被关注人的id
)


class News(BaseModel, db.Model):
    """新闻"""
    __tablename__ = "info_news"

    id = db.Column(db.Integer, primary_key=True)  # 新闻编号
    title = db.Column(db.String(256), nullable=False)  # 新闻标题
    source = db.Column(db.String(64), nullable=False)  # 新闻来源
    digest = db.Column(db.String(512), nullable=False)  # 新闻摘要
    content = db.Column(db.Text, nullable=False)  # 新闻内容
    clicks = db.Column(db.Integer, default=0)  # 浏览量
    index_image_url = db.Column(db.String(256))  # 新闻列表图片路径
    category_id = db.Column(db.Integer, db.ForeignKey("info_category.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("info_user.id"))  # 当前新闻的作者id
    status = db.Column(db.Integer, default=0)  # 当前新闻状态 如果为0代表审核通过，1代表审核中，-1代表审核不通过
    reason = db.Column(db.String(256))  # 未通过原因，status = -1 的时候使用
    # 当前新闻的所有评论
    comments = db.relationship("Comment", lazy="dynamic")

    def to_review_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "reason": self.reason if self.reason else ""
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_image_url": self.index_image_url,
            "clicks": self.clicks,
        }
        return resp_dict

    def to_dict(self):
        # print(" call success")
        print("类别表内容",self.category)
        print(self.category_id)
        # print(dir(self))
        print(dir(self.category))
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "comments_count": self.comments.count(),
            "clicks": self.clicks,
            "category": self.category.to_dict(),
            # "category": self.category_id,
            "index_image_url": self.index_image_url,
            "author": self.user.to_dict() if self.user else None
        }
        return resp_dict