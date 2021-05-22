import unittest

from BeautifulReport import BeautifulReport


"""
使用run文件执行unittest 文件时, 可以直接导入
这时 unittest 会自动查找导入问价中类去执行
但是文件的开头以test 文件的类和函数也必须以test开头
"""

if __name__ == '__main__':
   """
   defaultTestLoader
   使用unittest.defaultTestLoader()类, 这个类的作用就是,调用这个类的discover()方法, 搜索指定目录下指定开头的.py文件,
   并将搜索到的测试用例组装成一个测试集合, 听上去是不是和 TestSuite 的作用差不多
   """
   # 先确定一个要搜索的路径
   test_dir = "."
   # 然后创建集合对象
   dis = unittest.defaultTestLoader.discover(test_dir, pattern='test_bilibili.py')

   runner = BeautifulReport(dis)
   runner.report(
       description="b站登录",
       filename="bilibili_login"  # 生成测试报告的文件名
   )