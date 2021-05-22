import logging

from redis import StrictRedis


class Config(object):
    """项目配置类"""
    #开启debug模式
    DEBUG = True
    #mysql数据库配置信息
    #mysql数据库链接配置
    SQLALCHEMY_DATABASE_URI="mysql://root:chuanzhi@127.0.0.1:3306/information21"
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379
    SECRET_KEY="fagfjkasfsh87e22DHJS"
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    SESSION_TYPE= 'redis'
    SESSION_REDIS=StrictRedis(REDIS_HOST,REDIS_PORT)
    # SESSION_KEY_PREFIX=""
    SESSION_USE_SIGNER=True
    SESSION_PERMANENT=False
    PERMANENT_SESSION_LIFETIME=86400


class DevlopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL=logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING


config_dict={"development":DevlopmentConfig,
             "production":ProductionConfig}