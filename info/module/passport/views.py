from datetime import datetime

from info.models import User
from info.module.passport import passport_bp
from flask import request, current_app, abort, make_response, jsonify, session
from info.utils.captcha.captcha import captcha
from info import redis_store,constants
from info.utils.response_code import RET
from info.lib.yuntongxun.sms import CCP
import re
from info import db
@passport_bp.route('/image_code')
def get_image_code():
    code_id = request.args.get("code_id")
    if not code_id:
        current_app.logger.error("参数不足")
        abort(403)
    img_name,img_code,img_data=captcha.generate_captcha()
    try:
        redis_store.setex("imagecode_%s".format(code_id),constants.IMAGE_CODE_REDIS_EXPIRES,img_code)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    response=make_response(img_data)
    # response.headers["Content-Type"] = "image/JPEG"
    return response

@passport_bp.route('/sms_code',methods=["POST"])
def send_smscode():
    # import json
    # json.loads(request.data)
    param_dict=request.json
    mobile=param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id= param_dict.get("image_code_id")
    if not all([mobile,image_code,image_code_id]):
        current_app.logger.error("参数错误")
        # return jsonify({"errno":RET.PARAMERR,"errmsg":"参数错误"})
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    # current_app.logger.error("mobile", mobile)

    if not re.match("1[35789][0-9]{9}",mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR,errmsg="手机格式错误")
    # "imagecode_%s".format(code_id)
    try:
        real_image_code=redis_store.get("imagecode_%s".format(image_code_id))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询验证码真实值异常")
    if real_image_code:
        try:
            redis_store.delete("imagecode_%s".format(image_code_id))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="删除验证码真实值异常")
    else:
        current_app.logger.error("图片验证码真实值过期了")
        return jsonify(errno=RET.NODATA,errmsg="图片验证码真实值过期了")
    if real_image_code.lower()!=image_code.lower():
        current_app.logger.error("填写图片验证码错误")
        return jsonify(errno=RET.DATAERR,errmsg="填写图片验证码错误")
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户查询数据异常")
    if user:
        return jsonify(errno=RET.DBERR,errmsg="用户已经注册")
    import random
    sms_code=random.randint(0, 999999)
    sms_code="%06d"%sms_code
    try:
        result=CCP().send_template_sms(mobile,{sms_code,constants.IMAGE_CODE_REDIS_EXPIRES/60},1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="短信验证码发送失败")
    if result==-1:
        current_app.logger.error("短信验证码发送失败")
        return jsonify(RET.THIRDERR,errmsg="短信验证码发送失败")
    try:
        redis_store.setex("SMS_%s"%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存短信验证码异常")
    return jsonify(errno=RET.OK,errmsg="发送短信验证码成功")

@passport_bp.route('/register',methods=["POST"])
def register():
    param_dict=request.json
    mobile = param_dict.get("mobile")
    sms_code = param_dict.get("sms_code")
    password = param_dict.get("password")
    if not all([mobile,sms_code,password]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if not re.match("1[35789][0-9]{9}",mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR,errmsg="手机格式错误")
    try:
        real_sms_code=redis_store.get("SMS_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询短信验证码数据异常")
    if real_sms_code:
        redis_store.delete("SMS_%s"%mobile)
    else:
        current_app.logger.error("短信验证码过期了")
        return jsonify(errno=RET.NODATA,errmsg="短信验证码过期")
    if real_sms_code != sms_code:
        current_app.logger.error("短信验证码填写错误")
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码填写错误")
    user=User()
    user.nick_name=mobile
    user.mobile=mobile
    # user.password_hash=password
    user.password=password
    user.last_login=datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="用户数据保存异常")
    session["user_id"]=user.id
    session[mobile] = mobile
    session["nick_name"]=mobile
    return jsonify(errno=RET.OK,errmsg="注册成功")

@passport_bp.route('login',methods=['POST'])
def login():
    param_dict=request.json
    mobile=param_dict.get('mobile')
    password=param_dict.get('password')
    if not all([mobile,password]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")
    if not re.match("1[35789][0-9]{9}",mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR,errmsg="手机格式错误")
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在")
    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR,errmsg="填写密码错误")
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    user.last_login=datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存用户数据异常")
    return jsonify(errno=RET.OK,errmsg="登陆成功")
@passport_bp.route("login_out",methods=["POST"])
def login_out():
    session.pop("user_id",None)
    session.pop("mobile",None)
    session.pop("nick_name",None)
    session.pop("is_admin",None)
    return jsonify(errno=RET.OK,errmsg="退出登录成功")

