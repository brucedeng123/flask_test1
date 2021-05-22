from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate

from zlbbs import create_app
from exts import db
# 导入以后他会把这个models所有的表都会印刷到数据库当中
from apps.cms import models as cms_models

# 把cms_models下的CMSUser这个表类, 赋值给CMSUser
CMSUser = cms_models.CMSUser
CMSRole = cms_models.CMSRole
CMSPersmission = cms_models.CMSPersmission

# 创建flask里app
app = create_app()

# 创建数据库迁移工具对象的步足有3步
# 1. 创建flask脚本管理工具对象
manager = Manager(app)

# 2. 创建数据库迁移工具对象
Migrate(app, db)

# 3. 向manager对象中添加数据库的操作命令
# 第一个参数是给这条命令取的名字叫什么,关于数据库的我们通常叫db
# 第二个参数就是具体的命令
manager.add_command("db", MigrateCommand)


# 创建管理员  --manager的作用: 是在终端使用命令, option的作用:装饰的之后,可以传递参数
@manager.option("-u", "--username", dest="username")
@manager.option("-p", "--password", dest="password")
@manager.option("-e", "--email", dest="email")
def create_cms_user(username, password, email):
    """创建管理员用户"""
    user = CMSUser(username=username, password=password, email=email)
    # 添加
    db.session.add(user)
    try:
        # 提交到数据库
        db.session.commit()
        print("cms 用户添加成功")
    except Exception as e:
        print(e)
        db.session.rollback()
        print("cms 用户添加失败")


# @manager.add_command 这是一个函数
@manager.command # 添加自定命令create_role  终端运行 python manage.py create_role
def create_role():
    # 1. 访问者(可以修改个人信息)
    visitor = CMSRole(name="访问者", desc="只能相关数据, 不能修改.")
    visitor.permissions = CMSPersmission.VISITOR

    # 2. 运营角色(修改个人信息, 管理帖子, 管理评论, 管理前台用户)
    operator = CMSRole(name="运营", desc="管理帖子, 管理评论, 管理里前台用户, 管理后台用户权限.")
    operator.permissions = CMSPersmission.VISITOR | CMSPersmission.POSTER | \
                           CMSPersmission.COMMENTER | CMSPersmission.FRONTUSER | \
                           CMSPersmission.CMSUSER

    # 3. 管理员(拥有大部分权限)
    admin = CMSRole(name="管理员", desc="拥有本系统所有权限.")
    admin.permissions = CMSPersmission.VISITOR | CMSPersmission.POSTER | \
                        CMSPersmission.CMSUSER | CMSPersmission.COMMENTER | \
                        CMSPersmission.FRONTUSER | CMSPersmission.BOARDER

    # 4. 开发者权限(管理后台管理员)
    developer = CMSRole(name="开发者", desc="开发人员专用角色.")
    developer.permissions = CMSPersmission.ADMINER

	# 添加的数据
    db.session.add_all([visitor, operator, admin, developer])

    try:
    	# 提交到数据库
        db.session.commit()
        print("添加成功")
    except Exception as e:
    	# 回滚到提交前
        db.session.rollback()
        print("添加失败")


if __name__ == "__main__":
    manager.run()