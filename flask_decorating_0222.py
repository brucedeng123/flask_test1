from flask_script import Manager
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
app=create_app("production")
manager = Manager(app)

@manager.command
def music():
    """
    小妞，给爷唱一个
    """
    print("客官不可以，不可以摸我那里....")


if __name__ == '__main__':
    manager.run()