from flask_script import Manager, prompt_bool
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
# import sqlalchemy
#0.自定义的项目配置类



app=create_app("production")
from flask_seprating_0222 import db_manager

manager = Manager(app)

# db是前缀 执行命令方式 python manage.py db migrate
manager.add_command('db', db_manager)
@db_manager.command
def drop_data():
    if prompt_bool("你真的要删除这些数据吗？后果自负哦..\t\n"
                   "输入y删除,n取消"):
        print('数据已删除...')
    else:
        print("就知道你不敢")

if __name__ == '__main__':
    manager.run()