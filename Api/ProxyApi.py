# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import platform
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

sys.path.append('../')

from Config.ConfigGetter import config
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an useful proxy , options params:check_count,resp_seconds,type',
    # 'refresh': u'refresh proxy pool',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
    'get_status': u'proxy number',
    'get_trash': u'get all trash proxy from proxy pool'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/')
def get():
    cnt = request.args.get('check_count')              # 代理验证成功次数 check_count
    if cnt is None:
        cnt = request.args.get('cnt')                  # 代理验证成功次数 check_count
    proxy_type = request.args.get('type')              # 代理类型: http/https/socks4/socks5/socks
    resp_time = request.args.get('resp_seconds')       # 应答时间 : 单位秒数
    if resp_time is None:
        resp_time = request.args.get('time')           # 应答时间 : 单位秒数

    count = 1 if cnt is None or int(cnt) < 1 else int(cnt)
    if proxy_type is None or proxy_type.upper() not in ["HTTP", "HTTPS", "SOCKS", "SOCKS5", "SOCKS4"]:
        proxy_type = "HTTP"

    resp_seconds = 10 if resp_time is None or int(resp_time) < 1 else int(resp_time)

    proxy = ProxyManager().get(check_count=count, proxy_type=proxy_type, resp_seconds=resp_seconds)
    return proxy.info_json if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    # ProxyManager().refresh()
    pass
    return 'success'


@app.route('/get_all/')
def getAll():
    proxies = ProxyManager().getAll()
    return [_.info_dict for _ in proxies]


@app.route('/get_trash/')
def getTrash():
    proxies = ProxyManager().getTrash()
    return [_.info_dict for _ in proxies]


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    ProxyManager().delete(proxy)
    return {"code": 0, "src": "success"}


@app.route('/get_status/')
def getStatus():
    status = ProxyManager().getNumber()
    return status


if platform.system() != "Windows":
    import gunicorn.app.base
    from gunicorn.six import iteritems

    class StandaloneApplication(gunicorn.app.base.BaseApplication):

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            _config = dict([(key, value) for key, value in iteritems(self.options)
                            if key in self.cfg.settings and value is not None])
            for key, value in iteritems(_config):
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application


def runFlask():
    app.run(host=config.host_ip, port=config.host_port)


def runFlaskWithGunicorn():
    _options = {
        'bind': '%s:%s' % (config.host_ip, config.host_port),
        'workers': 4,
        'accesslog': '-',  # log to stdout
        'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
    }
    StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    if platform.system() == "Windows":
        runFlask()
    else:
        runFlaskWithGunicorn()
