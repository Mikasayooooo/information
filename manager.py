from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


class Config(object):

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.36.129:3306/info'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return 'ok'


if __name__ == '__main__':
    app.run()

