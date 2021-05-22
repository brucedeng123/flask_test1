from flask_script import Manager

# 不作为主命令模块，也就是说命令行是python manage.py xxx..
# 使用manage.py 而不是当前模块，这里的Manager()就不用传如Flask对象了
db_manager = Manager()

@db_manager.command
def migrate():
    """
    数据迁移命令
    """
    print("执行数据迁移...")