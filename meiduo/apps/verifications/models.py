from django.db import models
from rest_framework.views import APIView
# Create your models here.

class SMSCodeView(object):
    def get(self, request, mobile):