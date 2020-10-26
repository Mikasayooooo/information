from . import index_blue


@index_blue.route('/', methods=["GET", "POST"])
def hello_world():
    # 测试redis存取数据
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))
    #
    # #测试session存取
    # session["name"] = "zhangsan"
    # print(session.get("name"))

    return "helloworld"
