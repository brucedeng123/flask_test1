from flask_script import Manager, Command
# from app import app  # Flask对象
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
# import sqlalchemy
#0.自定义的项目配置类



app=create_app("production")


class TestCommand(Command):
    """
    测试命令
    """

    def run(self):  # 重写Command的run方法
        # 使用命令在控制台输出信息
        print("server run on xxx:80...")


manager = Manager(app) # 将flask_script与Flask联系起来
manager.add_command('test', TestCommand())
print("start travelsal")

if __name__ == '__main__':
    print("start run manager")
    manager.run()