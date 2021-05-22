#文件db.txt的内容为：{"count":1}
#注意一定要用双引号，不然json无法识别
from multiprocessing import Process
import time
import json
class Foo(object):
  def search(self, name):
    with open("db.txt", "r") as f_read:
      dic = json.load(f_read)
      time.sleep(1) # 模拟读数据的网络延迟
      print("<%s>用户 查看剩余票数为 [%s]" % (name, dic["count"]))
  def get(self, name):
    with open("db.txt", "r") as f_read:
      dic = json.load(f_read)
      if dic["count"] > 0:
        dic["count"] -= 1
        time.sleep(1) # 模拟写数据的网络延迟
        with open("db.txt", "w") as f_write:
          json.dump(dic, f_write)
          print("<%s> 购票成功" % name)
          print("剩余票数为 [%s]" % dic["count"])
      else:
        print("没票了，抢光了")
  def task(self, name):
    self.search(name)
    self.get(name)
if __name__ == "__main__":
  obj = Foo()
  for i in range(1,11):  # 模拟并发10个客户端抢票
    p = Process(target=obj.task, args=("路人%s" % i,))
    p.start()