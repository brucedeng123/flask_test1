from info import db, constants
from info.models import User, Category, News
from info.utils.pic_storage import pic_storage
from info.utils.response_code import RET
from . import profile_bp
from flask import render_template, g, request, jsonify, session, current_app
from info.utils.common import user_login_data
@profile_bp.route("/base_info",methods=["POST","GET"])
@user_login_data
def base_info():
    user = g.user
    data = {"user_info": user.to_dict() if user else None}
    if request.method == "GET":
        return render_template("profile/user_base_info.html",data=data)
    param_dict=request.json
    signature=param_dict.get("signature")
    nick_name=param_dict.get("nick_name")
    gender=param_dict.get("gender")
    if not all([signature,gender,nick_name]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if gender not in ["MAN","WOMAN"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登陆")
    user_list=User.query.filter(User.nick_name==nick_name).all()
    if user_list:
        return jsonify(errno=RET.DATAEXIST,errmsg="用户昵称已经存在")
    user.signature=signature
    user.gender=gender
    user.nick_name=nick_name
    session["nick_name"]=nick_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="修改用户对象异常")
    return jsonify(errno=RET.OK,errmsg="修改用户对象成功")

@profile_bp.route("/user_info")
@user_login_data
def user_info():
    user=g.user
    data={"user_info":user.to_dict()if user else None}
    return render_template("profile/user.html",data=data)
@profile_bp.route("/pic_info",methods=["POST","GET"])
@user_login_data
def pic_info():
    user=g.user
    if request.method=="GET":
        return render_template("profile/user_pic_info.html")
    pic_data=request.files.get("avatar").read()
    if not pic_data:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    try:
        pic_name=pic_storage(pic_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片错误")
    user.avatar_url=pic_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存用户图片数据异常")
    full_url=constants.QINIU_DOMIN_PREFIX+pic_name
    data={
        "avatar_url":full_url
    }
    return jsonify(errno=RET.OK,errmsg="OK",data=data)

@profile_bp.route("/pass_info",methods=["POST","GET"])
@user_login_data
def pass_info():
    user=g.user

    if request.method=="GET":
        return render_template("profile/user_pass_info.html")
    print("start post")
    param_dict=request.json
    old_password=param_dict.get("old_password")
    new_password=param_dict.get("new_password")
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="旧密码填写错误")
    user.password=new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="查询用户对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")


@profile_bp.route("/news_collection")
@user_login_data
def news_collection():
    user=g.user
    p=request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnp=RET.PARAMERR,errmsg="参数错误")
    collection_news_list={}
    current_page = 1
    total_page = 1
    if user:
        try:
            paginate=user.collection_news.paginate(p,constants.USER_COLLECTION_MAX_NEWS,False)
            collection_news_list=paginate.items
            current_page=paginate.page
            total_page=paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询用户对象异常")
    news_dict_list=[]
    for news in collection_news_list if collection_news_list else []:
        news_dict_list.append(news.to_review_dict())
    data={
        "collections":news_dict_list,
        "current_page":current_page,
        "total_page":total_page
    }

    return render_template("profile/user_collection.html",data=data)


@profile_bp.route("/news_release",methods=["GET","POST"])
@user_login_data
def news_release():
    if request.method=="GET":

        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.loggger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询分类数据异常")
        category_dict_list=[]
        for category in categories if categories else []:
            category_dict_list.append(category.to_dict())
        category_dict_list.pop(0)
        data={
            "categories":category_dict_list
        }
        return render_template("profile/user_news_release.html",data=data)
    param_dict=request.form
    title=param_dict.get("title")
    cid=param_dict.get("category_id")
    digest=param_dict.get("digest")
    index_image=request.files.get("index_image")
    content=param_dict.get("content")
    user=g.user
    source="个人发布"
    if not all([title,cid,digest,index_image,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    image_data=index_image.read()
    try:
        image_name=pic_storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片到七牛云异常")
    news=News()
    news.title=title
    news.category_id=cid
    news.digest=digest
    news.index_image_url=constants.QINIU_DOMIN_PREFIX+image_name
    news.content=content
    news.user_id=user.id
    news.status=1
    news.source=source
    try:
        db.session.add(news)
        db.session.commit()
        print("try ok")
    except Exception as e:
        print("log ok")
        current_app.loggger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存新闻对象异常")
    return jsonify(errno=RET.OK,errmsg="发布新闻成功")


@profile_bp.route("/news_list")
@user_login_data
def news_list():
    user=g.user
    p=request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    news_list=[]
    current_page=1
    total_page=1
    if user:
        try:
            paginate=News.query.filter(News.user_id==user.id).paginate(p,constants.USER_COLLECTION_MAX_NEWS,False)
            # paginate = user.news_list.filter(user.news_list.user_id == user.id).paginate(p, constants.USER_COLLECTION_MAX_NEWS,
            #                                                                    False)
            # paginate=user.news_list.filter(News.user_id==user.id).paginate(p,constants.USER_COLLECTION_MAX_NEWS,False)
            news_list=paginate.items
            current_page=paginate.page
            total_page=paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询新闻对象异常")
        news_dict_list=[]
        for news in news_list if news_list else []:
            news_dict_list.append(news.to_review_dict())
        data={
            "news_list":news_list,
            "current_page":current_page,
            "total_page":total_page
        }
        return render_template("profile/user_news_list.html",data=data)

@profile_bp.route("/user_follow")
@user_login_data
def user_follow():
    user=g.user
    p=request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    user_list=[]
    current_page=1
    total_page=1
    if user:
        try:
            paginate=user.followed.paginate(p,constants.USER_FOLLOWED_MAX_COUNT,False)
            user_list=paginate.items
            current_page=paginate.page
            total_page=paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询用户对象异常")
    user_dict_list=[]
    for user in user_list if user_list else[]:
        user_dict_list.append(user.to_dict())
    data={
        "users":user_dict_list,
        "current_page":current_page,
        "total_page":total_page
    }
    return render_template("profile/user_follow.html",data=data)