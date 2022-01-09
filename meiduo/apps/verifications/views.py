from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
import logging
from django_redis import get_redis_connection
from urllib3 import HTTPResponse

from meiduo.libs.yuntongxun.sms import CCP
from . import constants

logger = logging.getLogger("dy")
class SMSCodeView(APIView):
    """发送短信验证码"""
    def get(self, request,mobile):
        #生成验证码
        sms_code = '%06d'% randint(0,999999)
        logger.info(sms_code)
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES//60],1)
        return HttpResponse("ok")
