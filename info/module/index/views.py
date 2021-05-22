# from info.module.index import index_bp
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_bp
from info import redis_store,constants
from flask import session, current_app, render_template, jsonify, request, g
import logging
@index_bp.route("/test/")
def helloworld():
    session["name3"]="curry"
    redis_store.set("name", 'dengyu')
    # current_app.logger.debug("debug")
    # current_app.logger.info("debug")
    # current_app.logger.warning("debug")
    # current_app.logger.error("debug")
    # current_app.logger.critical("debug")
    logging.debug(current_app.url_map)
    return "hello world"
@index_bp.route("/")
@user_login_data
def index():
    user=g.user
    # return "hello"
    # user_id=session.get("user_id")
    # user=None
    # if user_id:
    #     try:
    #         user=User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(errno=RET.DBERR,errmsg="数据库错误")
        # if user:
        #     user_dict=user.to_dict()
    try :
        rank_news_list=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻数据异常")
    news_dict_list=[]
    if rank_news_list:
        for news_obj in rank_news_list:
            print(news_obj,type(news_obj))
            news_dict=news_obj.to_dict()
            news_dict_list.append(news_dict)
    try:
        categories=Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询分类数据异常")
    categories_dict_list=[]
    for category in categories if categories else []:
        category_dict = category.to_dict()
        categories_dict_list.append(category_dict)

    data={
        "user_info":user.to_dict() if user else None,
        # "news_dict":news_dict_list,
        "news_rank_list":rank_news_list,
        "categories":categories_dict_list
    }
    return render_template("news/index.html",data=data)
#     """
#         <html>
#             <body>
#                 <h1>Hello,user</h1>
#             </body>
#         </html>
# """
@index_bp.route("/favicon.ico")
def get_favicon():
    return current_app.send_static_file("news/favicon.ico")


@index_bp.route("/news_list")
def news_list():
    param_dict=request.args
    cid=param_dict.get("cid")
    page=param_dict.get("page",1)
    per_page=param_dict.get("per_page",10)
    if not cid:
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    try:
        cid=int(cid)
        page=int(page)
        per_page=int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERROR,errmsg="参数格式错误")
    # filter_list=[]
    # if cid !=1:
    #     print(News.category_id)
    #     print(cid)
    #     filter_list.append(News.category_id==cid)
    # print("condition")
    # print(filter_list)
    # filter_list=[]
    # try:
    #     if cid !=1:
    #
    #         paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()) \
    #             .paginate(page, per_page, False)
    #         print(paginate, type(paginate))
    #         news_list = paginate.items
    #         current_page = paginate.page
    #         total_page = paginate.pages
    #     else:
    #         paginate = News.query.filter().order_by(News.create_time.desc()) \
    #             .paginate(page, per_page, False)
    #         print(paginate, type(paginate))
    #         news_list = paginate.items
    #         current_page = paginate.page
    #         total_page = paginate.pages
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR,errmsg="查询新闻列表数据异常")
    # try:
    #     paginate=News.query.filter(News.category_id==cid).order_by(News.create_time.desc())\
    #         .paginate(page,per_page,False)
    #     print(paginate,type(paginate))
    #     news_list=paginate.items
    #     current_page=paginate.page
    #     total_page=paginate.pages
    #     print(paginate, type(paginate))
    #     print(news_list, type(news_list))
    #     print(current_page, type(current_page))
    #     print(total_page, type(total_page))
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR,errmsg="查询新闻列表数据异常")
    # filter_list = []
    filter_list = [News.status==0]
    # 不是最新分类
    if cid != 1:
        # 底层sqlalchemy会重新 == 符号返回一个`查询条件`而不是`Bool值`
        # 将查询条件添加到列表
        filter_list.append(News.category_id == cid)

    # *filter_list 解包将里面内容一个拿出来
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()) \
            .paginate(page, per_page, False)

        # 获取当前页码所有新闻对象列表数据
        news_list = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象列表异常")

    # 3.2 将新闻对象列表转换成新闻字典列表
    news_dict_list = []
    for news in news_list if news_list else []:
        # 新闻对象转换成字典对象并添加到新闻字典列表
        news_dict_list.append(news.to_dict())

    # 3.3 构建返回数据
    data = {
        "news_dict_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }

    # 4.返回值
    return jsonify(errno=RET.OK, errmsg="新闻列表数据查询成功", data=data)
