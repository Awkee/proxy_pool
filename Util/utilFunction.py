# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     utilFunction.py
   Description :  tool function
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: 添加robustCrawl、verifyProxy、getHtmlTree
-------------------------------------------------
"""
import json
import datetime
import re
import requests
from lxml import etree
from Util.WebRequest import WebRequest


def robustCrawl(func):
    def decorate(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            pass
            # logger.info(u"sorry, 抓取出错。错误原因:")
            # logger.info(e)

    return decorate

def check_proxy_type(type):
    return  True if type in ["HTTP", "HTTPS", "SOCKS", "SOCKS4", "SOCKS5"] else False

def check_ip(ip):
    for i in ip:
        if int(i) < 0 or int(i) > 255:
            return False
    return True

def check_port(port):
    return True if port > 0 and port < 65535 else False

def check_anonymity(anonymity):
    return True if anonymity in ["HA","A","T"] else False

def verifyProxyFormat(proxy):
    """
    检查代理格式
    :param proxy: json数据字符串格式:'{"proxy": "ip:port", "type":"HTTP" , "anonymity": "HA", "region": "China" }'
    :return:
    """
    data = json.loads(proxy)
    verify_regex = r"(\d{1,})\.(\d{1,})\.(\d{1,})\.(\d{1,}):(\d+)"
    if data.get('proxy'):
        type = data['type'] if data.get('type') else "HTTP"
        anonymity = data['anonymity'] if data.get('anonymity') else "T"
        region = data.get('region') 
        host = re.search(verify_regex, data['proxy'])
        return True if host and check_ip(host.group(1,2,3,4)) and check_port(int(host[5])) and check_proxy_type(type) and check_anonymity(anonymity) else False
    return False


def verifyProxyFormat1(proxy):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    import re
    verify_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
    _proxy = re.findall(verify_regex, proxy)
    return True if len(_proxy) == 1 and _proxy[0] == proxy else False


def getHtmlTree(url, **kwargs):
    """
    获取html树
    :param url:
    :param kwargs:
    :return:
    """

    header = {'Connection': 'keep-alive',
              'Cache-Control': 'max-age=0',
              'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept-Language': 'zh-CN,zh;q=0.8',
              }
    # TODO 取代理服务器用代理服务器访问
    wr = WebRequest()
    html = wr.get(url=url, header=header).content
    return etree.HTML(html)


def tcpConnect(proxy):
    """
    TCP 三次握手
    :param proxy:
    :return:
    """
    from socket import socket, AF_INET, SOCK_STREAM
    s = socket(AF_INET, SOCK_STREAM)
    ip, port = proxy.split(':')
    result = s.connect_ex((ip, int(port)))
    return True if result == 0 else False


def validUsefulProxy(proxy, proxy_type="HTTP"):
    """
    检验代理是否可用
    :param proxy:
    :return:
    """
    if isinstance(proxy, bytes):
        proxy = proxy.decode('utf-8')
    proxy_uri = proxy_type.lower() + "://" + proxy
    proxies = {
        'http': proxy_uri,
        "https": proxy_uri
    }
    try:
        begin = datetime.datetime.now()
        r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        end = datetime.datetime.now()
        k = end - begin
        if r.status_code == 200 and proxy.startswith(r.json()['origin']):
            return True, k.total_seconds()
    except Exception as e:
        #print(e)
        pass
    return False, 0

