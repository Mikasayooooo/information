from . import passport_blue
from info.utils.captcha.captcha import captcha
# 注意导包路径

from flask import request, current_app, make_response
from info import constants

from captcha.image import ImageCaptcha
from random import randint


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
    redis_store.set('image_store: {}'.format(cur_id), text, constants.IMAGE_CODE_REDIS_EXPIRES)

    # 判断是否有上一次的图片验证码
    try:
        # 判断是否有上一次的图片验证码
        if pre_id:
            redis_store.delete('image_store: {}'.format(pre_id))
    except Exception as e:
        current_app.logger.error(e)
        return '图片验证码操作失败'

    # 返回图片
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response

# image_code()
