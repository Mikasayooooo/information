from . import passport_blue
# from info.utils.captcha.captcha import captcha
# 注意导包路径

from captcha.image import ImageCaptcha
from random import randint


# 功能: 获取图片验证码
@passport_blue.route('/image_code')
def image_code():
    # 调用generate_captcha 获取图片验证码编号,验证码值,图片(二进制)
    # name,text,image_data = captcha.generate_captcha()

    list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z',
            '', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z']
    chars = ''

    for i in range(4):
        chars += list[randint(0, 62)]
    image_data = ImageCaptcha().generate_image(chars)
    # image_data.show()

    # 返回图片
    return image_data

# image_code()
