"""
测试用例
测试对象: B站 (B站登录)  https://passport.bilibili.com/login
"""

import unittest
import time

from parameterized import parameterized
from selenium import webdriver


class TestLogin(unittest.TestCase):
    """
    1. 打开浏览器   :  就使用 setUp(self)方法打开浏览器
    2. 查找用户名输入框
    3. 查找密码的输入框
    4. 点击登录
    5. 断言登录成功与否  使用登录后的页面上的用户名进行断言
    """
    # 创建登录数据, 这里可以写多个账号进行测试
    data = [
        ('账号', '密码'),
        ('账号', '密码'),
        ('账号', '密码'),
    ]
    def setUp(self) -> None:
        # 创建一个浏览器对象
        self.driver = webdriver.Chrome("../chromedriver.exe")
        # 发送请求
        self.driver.get("https://passport.bilibili.com/login")

    def tearDown(self) -> None:
        self.driver.close()  # 关闭浏览器
        self.driver.quit()  # 退出浏览器

    @parameterized.expand(data)
    def test_login(self, username, password):
        # 查找输入账号的文本框, 并输入账号
        time.sleep(1)
        self.driver.find_element_by_id("login-username").clear()  # 先清空文本框内容
        self.driver.find_element_by_id("login-username").send_keys(username)  # 输入账号
        # 查找出入密码的文本框, 并输入密码
        time.sleep(1)
        self.driver.find_element_by_id("login-passwd").clear()  # 先清空文本框的内容
        self.driver.find_element_by_id("login-passwd").send_keys(password)  # 输入密码
        # 查找登录的按钮, 点击登录
        time.sleep(0.5)
        self.driver.find_element_by_class_name("btn-login").click()
        # 代码写到一半, 我发现登录需要一个图片验证码, 所以我决定图片验证码手动点一下
        time.sleep(10)
        # 断言登录是否成功
        handle = self.driver.current_window_handle
        self.driver.switch_to.window(handle)
        index = self.driver.find_element_by_xpath('//*[@id="primaryPageTab"]/ul/li[1]/a/span').text
        #  # 进行断言, 如果在登录后的界面出现"首页"二字,就代表成功.否则视为失败
        self.assertEqual(index, "首页", msg='登录失败')