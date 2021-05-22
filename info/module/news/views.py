from info import constants, db
from info.models import User, News, Category, Comment, CommentLike
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import new_detail_bp
from flask import render_template, session, current_app, jsonify, g, request


@new_detail_bp.route("/<int:news_id>")
@user_login_data
def get_news_detail(news_id):
    user=g.user
        # if user:
        #     user_dict=user.to_dict()
    try:
        rank_news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻数据异常")
    news_dict_list = []
    if rank_news_list:
        for news_obj in rank_news_list:
            print(news_obj, type(news_obj))
            news_dict = news_obj.to_dict()
            news_dict_list.append(news_dict)

    print("news_id",news_id)
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻对象异常")
    print("news",dir(news))
    if news:
        news_dict=news.to_dict()
    is_collected=False
    is_followed=False
    print("user",dir(user))
    print(type(user))
    if user:
        if news in user.collection_news:
            is_collected=True
    print("final",is_collected)
    try:
        author=User.query.filter(News.user_id==User.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询用户对象异常")

    if user and author:
        # if user in author.followers:
        if author in user.followed:
            is_followed=True
    try:
        news_comment_list=Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询评论对象异常")
    commentLike_id_list=[]
    if user:
        comment_id_list=[comment.id for comment in news_comment_list]
        try:

            comment_obj_list=CommentLike.query.filter(CommentLike.comment_id.in_(comment_id_list),CommentLike.user_id==user.id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询评论列表对象异常")
        commentLike_id_list=[comment_like_obj.comment_id for comment_like_obj in comment_obj_list]
    comment_dict_list=[]
    for comment_obj in  news_comment_list if news_comment_list else []:
        comment_dict=comment_obj.to_dict()
        print("comment_dict",comment_dict)
        comment_dict["is_like"]= False
        if comment_obj.id in commentLike_id_list:
            comment_dict["is_like"]=True
        comment_dict_list.append(comment_dict)
    data = {
        "user_info": user.to_dict() if user else None,
        # "news_dict": news_dict_list,
        "news":news_dict,
        "news_rank_list":rank_news_list,
        "is_collected":is_collected,
        "comments":comment_dict_list,
        "is_followed":is_followed
    }
    return render_template("news/detail.html",data=data)


@new_detail_bp.route("/news_collect",methods=["POST"])
@user_login_data
def news_collect():
    user=g.user
    if not user:
        current_app.logger.error("用户未登陆")
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    params_dict=request.json
    news_id = params_dict.get("news_id")
    action = params_dict.get("action")
    if not all([news_id,action]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if action not in ["collect","cancel_collect"]:
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻对象异常")
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不存在")
    if action=="collect":
        user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")

@new_detail_bp.route('/news_comment',methods=["POST"])
@user_login_data
def news_comment():
    user=g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    param_dict=request.json
    news_id=param_dict.get("news_id")
    comment_str=param_dict.get("comment")
    parent_id=param_dict.get("parent_id")
    if not all([news_id,comment_str]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.loggger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻对象错误")
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不存在，不能发表评论")
    comment=Comment()
    comment.user_id=user.id
    comment.news_id=news_id
    comment.content=comment_str
    if parent_id:
        comment.parent_id=parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存评论对象异常")
    return jsonify(errno=RET.OK,errmsg="OK", data=comment.to_dict())


@new_detail_bp.route('/comment_like',methods=["POST"])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    param_dict=request.json
    # news_id=param_dict.get("new_id")
    comment_id=param_dict.get("comment_id")
    action=param_dict.get("action")
    if not all([comment_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if action not in ["add","remove"]:
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    try:
        comment=Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询评论对象异常")
    if not comment:
        return jsonify(errno=RET.NODATA,errmsg="评论不存在，不允许点赞")
    if action=="add":
        comment_like=None
        try:
            comment_like=CommentLike.query.filter(CommentLike.comment_id==comment_id,CommentLike.user_id==user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询评论点赞对象异常")
        if not comment_like:
            comment_like_obj=CommentLike()
            comment_like_obj.user_id = user.id
            comment_like_obj.comment_id=comment_id
            comment.like_count+=1
            db.session.add(comment_like_obj)
            db.session.commit()
    else:
        comment_like=None
        try:
            comment_like=CommentLike.query.filter(CommentLike.comment_id==comment_id,CommentLike.user_id==user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询评论点赞对象异常")
        if comment_like:
            db.session.delete(comment_like)
            comment.like_count-=1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存评论对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")

@new_detail_bp.route("/followed_user",methods=["POST"])
@user_login_data
def followed_user():
    user=g.user

    user_id=request.json.get("user_id")
    action=request.json.get("action")
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    if not all([user_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if action not in ["follow","unfollow"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    try:
        author=User.query.get("user_id")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询用户对象异常")
    if not author:
        return jsonify(errno=RET.NODATA,errmsg="作者不存在")
    if action=="follow":
        if user in author.followers:
            author.followers.remove(user)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存用户对象异常")
    return jsonify(errno=RET.OK,errmsg="OK")






