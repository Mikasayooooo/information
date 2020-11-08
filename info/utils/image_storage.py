from qiniu import Auth, put_file, etag,put_data
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'QQYV54o8u2_ahyaSEzlopqmTGZXeKudtPlO3A2L6'
secret_key = 'pmdYfZDpD9CmVuNSWY1PQDtXwj59GMqeV8v8AQgR'

def image_storage(image_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'infoinfo'

    # 上传到七牛云后保存的文件名，如果不指定，name名字由七牛云维护
    # key = 'my-python-logo.png'
    key = None

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = './aaa.jpg'

    # ret, info = put_file(token, key, image_data)  # 上传文件路径
    ret, info = put_data(token, key, image_data)  # 上传二进制流
    # print(info)
    # print(ret)
    # print(type(info.status_code))  # <class 'int'>

    '''
status_code:200, text_body:{"hash":"Fvs_xUnfM768ncYMYkQiYlSFG3jU","key":"Fvs_xUnfM768ncYMYkQiYlSFG3jU"}, _ResponseInfo__response:<Response [200]>, exception:None, x_log:X-Log, req_id:578AAACawh1NkEUW

{'key': 'Fvs_xUnfM768ncYMYkQiYlSFG3jU', 'hash': 'Fvs_xUnfM768ncYMYkQiYlSFG3jU'}

<class 'int'>
    '''

    # 处理上传的结果，如果上传成功，返回图片名称，否则返回None
    if info.status_code == 200:
        return ret.get(key)
    else:
        return None


# 用来测试图片上传的
if __name__ == '__main__':

    # 使用with测试，可以自动关闭流
    with open('./aaa.jpg','rb') as f:
        image_storage(f.read())


