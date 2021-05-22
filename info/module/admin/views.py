import time

from datetime import datetime, timedelta

from info import constants, db
from info.models import User, News, Category
from info.utils.pic_storage import pic_storage
from info.utils.response_code import RET
from . import admin_bp
from flask import render_template, request, current_app, session, redirect, url_for, abort, jsonify


@admin_bp.route("/login",methods=["GET","POST"])
def admin_login():
    if request.method=="GET":
        user_id=session.get("user_id")
        admin=session.get("is_admin",False)
        if user_id and admin:
            return redirect(url_for("admin.admin_index"))
        else:
            return render_template("admin/login.html")
    param_dict=request.form
    user_name=param_dict.get("username")
    password=param_dict.get("password")
    print(user_name)
    print(password)
    if not all ([user_name,password]):
        return render_template("admin/login.html",errmsg="参数不足")
    try:
        admin_user=User.query.filter(User.mobile==user_name,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html",errmsg="查询管理员用户对象异常")
    if not admin_user:
        return render_template("admin/login.html",errmsg="管理员用户不存在")
    print(admin_user.to_dict())
    if not admin_user.check_passowrd(password):
        return render_template("admin/login.html",errmsg="密码填写错误")
    session["user_id"]=admin_user.id
    session["nick_name"]=user_name
    session["mobile"]=user_name
    session["is_admin"]=True

    return redirect(url_for("admin.admin_index"))

@admin_bp.route("/index")
def admin_index():
    return render_template("admin/index.html")

@admin_bp.route("/user_count")
def user_count():
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    try:
        now = time.localtime()
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    try:
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图表信息
    # 获取到当天00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    # 依次添加数据，再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        # end_date=begin_date+datetime.timedelta(days=1)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {"total_count": total_count, "mon_count": mon_count, "day_count": day_count, "active_date": active_date,
            "active_count": active_count}

    return render_template('admin/user_count.html', data=data)


@admin_bp.route("/user_list")
def user_list():
    # p=request.json.get("p",1)
    # print(p)
    p = request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        p=1
    user_list=[]
    current_page=1
    total_page=1
    try:
        paginate=User.query.filter(User.is_admin==False).order_by(User.last_login.desc()).paginate(p,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        print(paginate.items)
        user_list=paginate.items
        current_page=paginate.page
        total_page=paginate.pages
    except Exception as e:
        print("test operation flow")
        return abort(404)
    user_dict_list=[]
    for user in user_list if user_list else []:
        user_dict_list.append(user.to_admin_dict())
    data={
        "users":user_dict_list,
        "current_page":current_page,
        "total_page":total_page
    }
    # print(data["users"][0].nick_name)
    return render_template("admin/user_list.html",data=data)

@admin_bp.route("/news_review")
def news_review():
    print(request.args.to_dict().get("p"),"args") #imutable dict
    print(request.data,"data") #bytes
    print(request.files.to_dict(), "file") ##imutable dict
    print(request.json,type(request.json),"json") #None
    print(request.values,type(request.values),"values")#一个包含 form 和 args 全部内容的 CombinedMultiDict


    # for news in request.json if request.json else []:
    #     print(request.json,news,"json")
    for news in request.args :
        print(request.args,news,"args")
    # for news in request.files if request.files else []:
    #     print(request.files,news,"files")


    p=request.args.get("p",1)
    keywords=request.args.get("keywords", "")
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
        paginate=News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news_list=paginate.items
        current_page=paginate.page
        total_page=paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    news_dict_list=[]
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_review_dict())
    data={
        "news_list":news_dict_list,
        "current_page":current_page,
        "total_page":total_page
    }
    return render_template("admin/news_review.html",data=data)

@admin_bp.route("/news_review_detail",methods=["GET","POST"])
def news_review_detail():
    print(request.method)
    # request.method = "POST"
    if request.method=="GET":
        news_id=request.args.get("news_id")
        news=None
        if news_id:
            try:
                # news = News.query.get(news_id)
                news=News.query.filter(News.id==news_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return abort(404)
        news_dict=None
        if news:
            news_dict=news.to_dict()
        data={
            "news":news_dict
        }
        return render_template("admin/news_review_detail.html",data=data)
    param_dict=request.json
    # param_dict = request.args
    print("post ok")
    # param_dict = request.data

    news_id=param_dict.get("news_id")
    action=param_dict.get("action")
    print(action,news_id)
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if action not in ["reject","accept"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻对象异常")
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不存在")
    if action=="accept":
        print("accept ok")
        news.status=0
    if action=="reject":
        reason=request.json.get("reason")
        if reason:
            news.status=-1
            news.reason=reason
        else:
            return jsonify(errno=RET.PARAMERR,errmsg="")
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存新闻对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")


@admin_bp.route("/news_edit",methods=["GET","POST"])
def news_edit():
    p = request.args.get("p", 1)
    keywords = request.args.get("keywords", "")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1
    user_list = []
    current_page = 1
    total_page = 1
    filter_list = []
    if keywords:
        filter_list.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p,
                                                                                              constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                              False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_basic_dict())
    data = {
        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("admin/news_edit.html", data=data)

@admin_bp.route("/news_edit_detail",methods=["GET","POST"])
def news_edit_detail():
    if request.method=="GET":
        news_id =request.args.get("news_id")
        news=None
        if news_id:
            try:
                news=News.query.get(news_id)
            except Exception as e:
                current_app.logger.errror(e)
                return abort(404)

        news_dict=None
        if news:
            news_dict=news.to_dict()
        print(news_id,news)
        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询分类数据异常")
        category_dict_list=[]
        for category in categories if categories else []:
            category_dict=category.to_dict()
            category_dict["is_selected"]=False
            if category.id == news.category_id:
                category_dict["is_selected"]=True
            category_dict_list.append(category_dict)
        category_dict_list.pop(0)
        data={
            "news":news_dict,
            "categories":category_dict_list
        }
        return render_template("admin/news_edit_detail.html",data=data)
    param_dict=request.form
    news_id=param_dict.get("news_id")
    title=param_dict.get("title")
    category_id=param_dict.get("category_id")
    digest=param_dict.get("digest")
    content=param_dict.get("content")
    index_image=request.files.get("index_image")
    if not all([news_id,title,category_id,digest,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    image_name=None
    if image_name:
        print("iamge_name is True")
    if index_image:
        try:
            image_name=pic_storage(index_image.read())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR,errmsg="上传图片到七牛云失败")

    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻出现异常")
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不存在")
    news.title=title
    news.category_id=category_id
    news.digest=digest
    news.content=content
    if image_name:
        news.index_image_url=constants.QINIU_DOMIN_PREFIX+image_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存新闻对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")

@admin_bp.route("/news_category")
def news_category():
    try:
        categories=Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询分类对象异常")
    categories_dict_list=[]
    for category in categories if categories else []:
        categories_dict=category.to_dict()
        categories_dict_list.append(categories_dict)
    categories_dict_list.pop(0)
    data={
        "categories":categories_dict_list
    }
    return render_template("admin/news_type.html",data=data)


@admin_bp.route("/add_category",methods=["POST"])
def add_category():
    id=request.json.get("id")
    name=request.json.get("name")
    if not name:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if id:
        try:
            category=Category.query.get(id)
        except Exception as e:
            current_app.loggger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询分类对象异常")
        if not category:
            return jsonify(errno=RET.NODATA,errmsg="分类不存在")
        else:
            category.name=name
    else:
        category=Category()
        category.name=name
        db.session.add(category)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存分类对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")


