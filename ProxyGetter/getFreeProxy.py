# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------
"""
import json
import re
import sys
import requests
from time import sleep
import execjs
from lxml import etree

sys.path.append('..')

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

def get_ano(anonymity):
    if re.search(r'^高匿.*|(?i)elite.*', anonymity) : return "HA"
    if re.search(r'^匿名|(?i)anony', anonymity) : return "A"
    if re.search(r'透明|(?i)trans', anonymity) : return "T"
    return None

class GetFreeProxy(object):
    """
    proxy getter
    """

    @staticmethod
    def free01_data5u():
        """
        无忧代理 PROXY : freeProxy01 : http://www.data5u.com/
        几乎没有能用的
        :return:
        """
        url_list = [
            'http://www.data5u.com/'
        ]
        key = 'ABCDEFGHIZ'
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    ip = ul.xpath('./span[1]/li/text()')[0]
                    classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                    classname = classnames.split(' ')[1]
                    port_sum = 0
                    for c in classname:
                        port_sum *= 10
                        port_sum += key.index(c)
                    port = port_sum >> 3
                    ano = ul.xpath('./span[3]/li/text()')[0]
                    anonymity = get_ano(ano)
                    type = ul.xpath('./span[4]/li/text()')[0].upper()
                    region = ul.xpath('./span[5]/li/text()')[0]

                    jsdata = {}
                    jsdata['proxy'] = f'{ip}:{port}'
                    jsdata['proxy_type']  = type
                    jsdata['anonymity'] = anonymity
                    jsdata['region'] = region
                    yield jsdata
                except Exception as e:
                    print(e)

    @staticmethod
    def free02_66ip(count=50):
        """
        代理66 PROXY: free02_66ip : http://www.66ip.cn/
        :param count: 提取数量
        :return:
        """
        urls = [
            f'http://www.66ip.cn/1.html',
            f'http://www.66ip.cn/2.html',
        ]
        try:
            for url in urls:
                html_tree = getHtmlTree(url)
                tr_list = html_tree.xpath('//tr')
                jsdata = {}
                for td in tr_list[2:]:
                    jsdata['proxy'] = td.xpath('td[1]/text()')[0] + ":" + td.xpath('td[2]/text()')[0]
                    jsdata['proxy_type'] = "HTTP"
                    jsdata['anonymity'] = get_ano(td.xpath('./td[4]/text()')[0])
                    yield jsdata
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy04():
        """
        guobanjia PROXY: freeProxy04: http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//tbody/tr')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """./td[1]//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        jsdata = {}
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))

                # HTML中的port是随机数，真正的端口编码在class后面的字母中。
                # 比如这个：
                # <span class="port CFACE">9054</span>
                # CFACE解码后对应的是3128。
                port = 0
                for _ in each_proxy.xpath("./td[1]/span[contains(@class, 'port')]"
                                          "/attribute::class")[0]. \
                        replace("port ", ""):
                    port *= 10
                    port += (ord(_) - ord('A'))
                port /= 8
                anonymity = get_ano(each_proxy.xpath("./td[2]/a/text()")[0])
                proxy_type = each_proxy.xpath("./td[3]/a/text()")[0].upper()
                jsdata['proxy'] = '{}:{}'.format(ip_addr, int(port))
                jsdata['proxy_type'] = proxy_type
                jsdata['anonymity'] = anonymity
                print(jsdata)
                yield jsdata 
            except Exception as e:
                print(e)
                pass

    @staticmethod
    def freeProxy05():
        """
        快代理 PROXY: freeProxy05： https://www.kuaidaili.com
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/',
            'https://www.kuaidaili.com/free/intr/'
        ]
        jsdata = {}
        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                jsdata['proxy'] = ':'.join(tr.xpath('./td/text()')[0:2])
                jsdata['anonymity'] = get_ano(tr.xpath('./td[3]/text()')[0])
                jsdata['proxy_type'] = tr.xpath('./td[4]/text()')[0]
                yield jsdata

    @staticmethod
    def freeProxy07():
        """
        云代理 PROXY: freeProxy07: http://www.ip3366.net/free
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1']
        jsdata = {}
        for url in urls:
            tree = getHtmlTree(url)
            tr_list = tree.xpath('//tbody/tr')
            for tr in tr_list:
                jsdata['proxy'] = ':'.join(tr.xpath('./td/text()')[0:2])
                jsdata['anonymity'] = get_ano(tr.xpath('./td[3]/text()')[0])
                jsdata['proxy_type'] = tr.xpath('./td[4]/text()')[0]
                yield jsdata

    @staticmethod
    def freeProxy10():
        """
        墙外网站 cn-proxy
        :return:
         """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        jsdata = {}
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                jsdata['proxy'] = ':'.join(proxy)
                jsdata['anonymity'] = "T"
                jsdata['proxy_type'] = "HTTP"
                yield jsdata

    @staticmethod
    def freeProxy11():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        jsdata = {}
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                jsdata['proxy'] = base64.b64decode(proxy).decode()
                jsdata['anonymity'] = "T"
                jsdata['proxy_type'] = "HTTP"
                yield jsdata

    @staticmethod
    def freeProxy12():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        jsdata = {}
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                jsdata['proxy'] = ':'.join(proxy)
                jsdata['anonymity'] = "T"
                jsdata['proxy_type'] = "HTTP"
                yield jsdata

    @staticmethod
    def freeProxy13(max_page=4):
        """
        齐云代理 PROXY: freeProxy13: http://www.qydaili.com/free/?action=china&page=1
        :param max_page:
        :return:
        """
        base_url = 'https://www.qydaili.com/free/?page='
        jsdata = {}
        request = WebRequest()
        for page in range(1, max_page + 1):
            url = base_url + str(page)
            r = request.get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td.*?>(\d+)</td>[\s\S]*?<td.*?>(.*?)</td>[\s\S]*?<td.*?>(.*?)</td>',
                r.text)
            for proxy in proxies:
                jsdata['proxy'] = ':'.join(proxy[0:2])
                jsdata['anonymity'] = get_ano(proxy[2])
                jsdata['proxy_type'] = proxy[3].upper()
                yield jsdata

    @staticmethod
    def freeProxy14(max_page=2):
        """
        89免费代理 PROXY: freeProxy14: http://www.89ip.cn/index.html
        :param max_page:
        :return:
        """
        base_url = 'http://www.89ip.cn/index_{}.html'
        jsdata = {}
        request = WebRequest()
        for page in range(1, max_page + 1):
            url = base_url.format(page)
            r = request.get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies:
                jsdata['proxy'] = ':'.join(proxy)
                jsdata['anonymity'] = "T"
                jsdata['proxy_type'] = "HTTP"
                yield jsdata

    @staticmethod
    def freeProxy15(max_page=1):
        """
        PROXY: freeProxy15: https://www.sslproxies.org
        :param max_page:
        :return:
        """
        url = 'https://www.sslproxies.org'
        request = WebRequest()
        r = request.get(url, timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        jsdata = {}
        for proxy in proxies:
            jsdata['proxy'] = ':'.join(proxy)
            jsdata['anonymity'] = "T"
            jsdata['proxy_type'] = "HTTP"
            yield jsdata

    @staticmethod
    def freeA02_proxyList():
        """
        proxyList PROXY: freeA02_proxyList: https://free-proxy-list.net/anonymous-proxy.html
        :return:
        """
        url = 'https://free-proxy-list.net/anonymous-proxy.html'
        request = WebRequest()
        r = request.get(url, timeout=10)
        proxies = re.findall(
            r'<tr.*>[\s\S].*?<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>(\d+)</td>[\s\S]*?<td>.*?</td>[\s\S]*?<td>.*?</td>[\s\S]*?<td>(.*?)</td><td>.*?</td>[\s\S]*?[\s\S]*?<td>(.*?)</td>.*?</tr>',
            r.text)
        jsdata = {}
        for proxy in proxies:
            jsdata['proxy'] = ':'.join(proxy[0:2])
            jsdata['anonymity'] = get_ano(proxy[2])
            jsdata['proxy_type'] = "HTTP" if proxy[3] == "no" else "HTTPS"
            yield jsdata

    @staticmethod
    def freeProxySunny9577():
        """
        普通代理 PROXY: freeProxySunny9577: https://sunny9577.github.io/proxy-scraper/proxies.json
        :return:
        """
        import json
        url = 'https://sunny9577.github.io/proxy-scraper/proxies.json'
        request = WebRequest()
        resp = request.get(url, timeout=10)
        data = resp.json()
        proxies = [(i['ip'] , i['port'], i['anonymity'], i['type']) for i in data['usproxy']]
        jsdata = {}
        for proxy in proxies:
            jsdata['proxy'] = ":".join(proxy[0:2])
            jsdata['anonymity'] = get_ano(proxy[3])
            jsdata['proxy_type'] = 'HTTP'
            yield jsdata
    @staticmethod
    def freeApi_proxylist():
        """
            免费代理API PROXY: freeApi_proxylist https://api.getproxylist.com/proxy?protocol=http
        """
        url = 'https://api.getproxylist.com/proxy?protocol=http'
        req = WebRequest()
        for i in range(0, 10):
            resp = req.get(url, timeout=10)
            data = resp.json()
            yield {
                'proxy' : data['ip']+":"+data['port'],
                'anonymity' : get_ano(data['anonymity']),
                'proxy_type': data['protocol'].upper()
            }


    @staticmethod
    def free_premproxy():
        """
        免费代理 PROXY: free_premproxy : https://premproxy.com/list/time-01.htm
        :param count: 提取数量
        :return:
        """
        countries = [
            'China-01', 'China-02', 'China-03', 
            'Taiwan-01',
            'United-States-01','United-States-02',
            'Japan-01','Korea-Republic-of-01'
        ]
        try:
            for i in countries:
                start_url = 'https://premproxy.com/proxy-by-country/{}.htm'.format(i)
                req = WebRequest()
                resp = req.get(start_url, timeout=10)
                doc = etree.HTML(resp.text)
                jsscript = doc.xpath('//head/script')
                if jsscript:
                    jsdata1 = jsscript[0].xpath('string(.)')
                if resp:
                    ip_address = re.compile('<td data-label="IP:port ">(.*?)</td>')
                    re_ip_address = ip_address.findall(resp.text)
                    for address_port in re_ip_address:
                        data = re.findall(r'(.*)<scripttype="text/javascript">document.write\((.*)\)</script>', address_port.replace(' ',''))
                        if data and len(data[0]) == 2:
                            jsport = execjs.compile( jsdata1 )
                            port = jsport.eval(data[0][1])
                            proxy = data[0][0] + port
                        else:
                            proxy = address_port.replace(' ','')
                        yield {
                            'proxy' : proxy,
                            'anonymity' : 'T',
                            'proxy_type' : 'HTTP'
                        }
        except Exception as e:
            print(e)


    @staticmethod
    def free_spysone():
        """
        免费代理 PROXY: free_spysone : http://spys.one/en/free-proxy-list/
        :param count: 提取数量
        :return:
        """
        urls = [
            'http://spys.one/en/free-proxy-list'
        ]
        try:
            for url in urls:
                req = WebRequest()
                resp = req.get(url, timeout=10)
                doc = etree.HTML(resp.text)
                jsscript = doc.xpath('//body/script')
                if jsscript:
                    jsdata1 = jsscript[0].xpath('string(.)')
                tr_list = doc.xpath('//body/table//table/tbody')
                for tr in tr_list[2:]:
                    ip = tr.xpath(r'./td[1]/text()')[0]
                    jsport = tr.xpath(r'./td[1]//script')[0].xpath('string(.)')
                    data = re.findall(r'.*document.write.*\"(\+.*\))\)$', jsport)
                    print(ip,jsport,data)
                    if data and len(data[0]) == 1:
                        myjs = execjs.compile(jsdata1)
                        port = myjs.eval(":" + data[0][0])
                        proxy = ip + port
                    else:
                        proxy = ip
                    proxy_type = tr.xpath(r'./td[2]')[0].xpath('string(.)')
                    yield {
                        'proxy' : proxy,
                        'anonymity' : 'T',
                        'proxy_type' : proxy_type.upper()
                    }
        except Exception as e:
            print(e)


if __name__ == '__main__':
    from CheckProxy import CheckProxy

    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy01)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy02)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy03)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy04)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy05)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy06)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy07)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy08)
    CheckProxy.checkGetProxyFunc(GetFreeProxy.free_premproxy)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy13)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxy14)

    # CheckProxy.checkAllGetProxyFunc()
