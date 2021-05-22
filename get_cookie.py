import requests
class  ccedu(object):
    def get_cookie(self):
        #创建session对象
        session = requests.Session()
        url = "http://10.206.14.***:8080/ccsedu/a/login.do"
        payload = {'args': None, 'usertype':2, 'username':'********', 'password':'********'}
        #使用session发送post请求获取cookie
        session.post(url,data=payload)
        print(session.cookies.get_dict())
        return  session.cookies.get_dict()
    def  addteacher(self,name,masterCourse,externalUnit,position):
        url = "http://10.206.14.***:8080/ccsedu/a/js/jsgl/saveLecturer "
        payload = {'name': name, 'sex': 1, 'levels': 1, 'type': 2, 'masterCourse': masterCourse,
                   'externalUnit': externalUnit, 'position': position}
        res = requests.post(url,data=payload,cookies=c.get_cookie())
        print(res.json())
if __name__ == '__main__':
    c = ccedu()
    c.addteacher("李睿",'数学','未知机构','职务数学老师')