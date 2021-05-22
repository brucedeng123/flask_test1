from multiprocessing import Process
from multiprocessing import Lock
import time
import json


class Foo(object):
    def search(self, name):
        with open("db.txt", "r") as f_read:
            dic = json.load(f_read)

            time.sleep(1)  # 模拟读数据的网络延迟
            print("<%s>用户 查看剩余票数为 [%s]" % (name, dic["count"]))

    def get(self, name):
        with open("db.txt", "r") as f_read:
            dic = json.load(f_read)
            if dic["count"] > 0:
                dic["count"] -= 1
                time.sleep(1)  # 模拟写数据的网络延迟
                with open("db.txt", "w") as f_write:
                    json.dump(dic, f_write)
                    print("<%s> 购票成功" % name)
                    print("剩余票数为 [%s]" % dic["count"])
            else:
                print("没票了，抢光了")

    def task(self, name, mutex):
        self.search(name)
        with mutex:  # 相当于lock.acquire(),执行完自代码块自动执行lock.release()
            self.get(name)


if __name__ == "__main__":
    mutex = Lock()
    obj = Foo()
    for i in range(1, 11):  # 模拟并发10个客户端抢票
        p = Process(target=obj.task, args=("路人%s" % i, mutex))
        p.start()