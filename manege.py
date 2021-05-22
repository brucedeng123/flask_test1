from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
# import sqlalchemy
#0.自定义的项目配置类
from info.models import User

app=create_app("development")
manager=Manager(app)
Migrate(app,db)
manager.add_command("db",MigrateCommand)
@manager.option("-n","--name",dest="name")
@manager.option("-p","--password",dest="password")
def create_super_user(name,password):
    if not all([name,password]):
        return "参数不足"
    user=User()
    user.mobile=name
    user.password=password
    user.nick_name=name
    user.is_admin=True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "保存管理员用户异常"
    return "创建管理员用户成功"


# @app.route("/")
# def index():
#     return """
#         <html>
#             <body>
#                 <h1>Hello,user</h1>
#             </body>
#         </html>
# """

if __name__=='__main__':
    # app.run()
    manager.run()
