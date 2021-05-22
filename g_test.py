
# encoding=utf-8
from flask import Flask
from flask import g
import random

app = Flask(__name__)


@app.before_request
def set_on_g_object():
    x = random.randint(0, 9)
    app.logger.debug('before request g.x is {x}'.format(x=x))
    g.x = x


@app.route("/")
def test():
    g.x = 1000
    return str(g.x)


@app.after_request
def get_on_g_object(response):
    app.logger.debug('after request g.x is{g.x}'.format(g=g))
    return response