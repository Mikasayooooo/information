from . import passport_blue
from info.utils.captcha.captcha import captcha
# 注意导包路径

from flask import request, current_app, make_response, jsonify
from info import constants

import json
import re
from info.libs.yuntongxun.sms import CCP

from captcha.image import ImageCaptcha
from random import randint


# 功能: 获取短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile,image_code,image_code_id
# 返回值: errno,errmsg
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    # 1.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get('mobile')
    image_code = dict_data.get('image_code')
    image_code_id = dict_data.get('image_code_id')

    # 2.验证参数,图片验证码
    from info import redis_store
    redis_image_code = redis_store.get('image_code: {}'.format(image_code_id))
    if image_code.lower() != redis_image_code.lower():
        redis_store.delete('image_code')
        return jsonify(errno=10000, errmsg='图片验证码填写错误')

    # 3.校验参数,手机格式
    if not re.match('1[3-9]\d{9}', mobile):
        return jsonify(errno=20000, errmsg='手机号码格式不匹配')

    # 4.发送短信,调用封装好的cpp
    ccp = CCP()
    result = ccp.send_template_sms('19941064060', ['666233', 5], 1)
    if result == -1:
        return jsonify(errno=30000, errmsg='短信发送失败')

    # 5.返回发送的状态
    return jsonify(errno=0, errmsg='短信发送成功')





# 功能: 获取图片验证码
# 请求路径: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id,pre_id
# 返回值: 图片验证码
@passport_blue.route('/image_code')
def image_code():
    # list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    #         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
    #         'v', 'w', 'x', 'y', 'z',
    #         '', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
    #         'W', 'X', 'Y', 'Z']
    # chars = ''
    #
    # for i in range(4):
    #     chars += list[randint(0, 62)]
    # image_data = ImageCaptcha().generate_image(chars)
    # image_data.show()

    # 获取前端传递的参数
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')

    # 调用generate_captcha 获取图片验证码编号,验证码值,图片(二进制)
    name, text, image_data = captcha.generate_captcha()

    from info import redis_store
    # 采用局部导入的方式,因为redis_store声明了全局变量为None,redis_store = None,
    # 在上面导入的话,此时redis_store还只是个none值,需要等执行create_app函数之后才有值

    # 将图片验证码的值保存在redis中
    # 参数1: key,参数2: value,参数3: 有效期
    redis_store.set('image_code: {}'.format(cur_id), text, constants.IMAGE_CODE_REDIS_EXPIRES)

    # 判断是否有上一次的图片验证码
    try:
        # 判断是否有上一次的图片验证码
        if pre_id:
            redis_store.delete('image_code: {}'.format(pre_id))
    except Exception as e:
        current_app.logger.error(e)
        return '图片验证码操作失败'

    # 返回图片
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response

# image_code()
