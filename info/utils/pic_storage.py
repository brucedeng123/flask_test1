import qiniu
from flask import current_app, jsonify

from info.utils.response_code import RET

access_key, secret_key="9gESVSSQOCoPkDT_5vSgyvYDC4lABTUlZ9OlIncQ","_awlQZzUGmJKTEd6fmD_SfUIobSbM8VggBV4V5b2"
bucket_name="information0429"
def pic_storage(data):
    q = qiniu.Auth(access_key, secret_key)
    # key = 'hello'
    # data = 'hello qiniu!'
    token = q.upload_token(bucket_name)
    if not data:
        return AttributeError("图片数据为空")
    try:
        ret, info = qiniu.put_data(token, None, data)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(e)
        # return jsonify(errno=RET.THIRDERR,errmsg="上传到七牛云失败")
    # if ret is not None:
    #     print('All is OK')
    # else:
    #     print(info)  # error message in info
    print(ret,"------------")
    print(info)
    if info.status_code != 200:
        raise Exception("图片上传失败")
    return ret["key"]

if __name__ == "__main__":
    file=input(r"请输入图片地址")
    with open(file,"rb")as f:
        data=f.read()
        pic_storage(data)