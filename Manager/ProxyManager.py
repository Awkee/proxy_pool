# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import random
import json
import traceback

from ProxyHelper import Proxy
from DB.DbClient import DbClient
from Config.ConfigGetter import config
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = config.db_name + 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = config.db_name + 'useful_proxy'
        self.trash_proxy_queue = config.db_name + 'trash_proxy'

    def fetch(self):
        """
        fetch proxy into db by ProxyGetter
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        proxy_set = set()
        self.log.info("ProxyFetch : start")
        for proxyGetter in config.proxy_getter_functions:
            self.log.info("ProxyFetch - {func}: start".format(func=proxyGetter))
            try:
                for proxy_info in getattr(GetFreeProxy, proxyGetter.strip())():
                    proxy = json.dumps(proxy_info)
                    if not proxy or not verifyProxyFormat(proxy):
                        self.log.error('ProxyFetch - {func}: '
                                       '{proxy} illegal'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        continue
                    elif proxy in proxy_set:
                        self.log.info('ProxyFetch - {func}: {proxy} exist'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        continue
                    else:
                        self.log.info('ProxyFetch - {func}: '
                                      '{proxy} success'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        proxy_obj = Proxy(**proxy_info, source=proxyGetter)
                        self.db.put(proxy_obj)
                        proxy_set.add(proxy_info['proxy'])
            except Exception as e:
                self.log.error("ProxyFetch - {func}: error : {err}".format(func=proxyGetter, err=str(e)))
                traceback.print_exc()

    def get(self, proxy_str=None, type = 0, check_count=1, resp_seconds=10, proxy_type="HTTP"):
        """
        return a useful proxy
        :return:
        """
        if type == 0:
            self.db.changeTable(self.useful_proxy_queue)
        else:
            self.db.changeTable(self.trash_proxy_queue)
        if proxy_str:
            item = self.db.get(proxy_str)
            if item:
                return Proxy.newProxyFromJson(item)
        else:
            item_list = self.db.getAll()
            # 过滤列表，找到符合要求列表 #
            for i  in item_list[:]:
                jdata=json.loads(i)
                if jdata['check_count'] < check_count or jdata['resp_seconds'] > resp_seconds or jdata['type'] != proxy_type.upper() :
                    item_list.remove(i)
            if item_list is not None and len(item_list) > 0:
                random_choice = random.choice(item_list)
                return Proxy.newProxyFromJson(random_choice)
        return None

    def delete(self, proxy_obj, type=0):
        """
        delete proxy from pool
        :param proxy_str:
        :param type: 0: move to trash , 1： trash_proxy_queue , 2：useful_proxy_queue,default 0
        :return:
        """
        if type == 0:
            self.db.changeTable(self.trash_proxy_queue)
            if not self.db.exists(proxy_obj.proxy):
                self.db.put(proxy_obj)
            self.db.changeTable(self.useful_proxy_queue)
        elif type == 1:
            self.db.changeTable(self.useful_proxy_queue)
        else:
            self.db.changeTable(self.trash_proxy_queue)
        self.db.delete(proxy_obj.proxy)

    def put(self, proxy_obj, type=0):
        """
        put proxy to db table
        :param proxy_obj:
        :param type: 0: move from trash to useful queue, 1： trash_proxy_queue , 2：useful_proxy_queue,default 0
        :return:
        """
        if type == 0:
            self.db.changeTable(self.trash_proxy_queue)
            self.db.delete(proxy_obj.proxy)
            # 保存到UsefulProxy中 #
            self.db.changeTable(self.useful_proxy_queue)
        elif type == 1:
            self.db.changeTable(self.useful_proxy_queue)
        else:
            self.db.changeTable(self.trash_proxy_queue)

        #if not self.db.exists(proxy_obj.proxy):
        self.db.put(proxy_obj)

    def exists(self, proxy_str, type=1):
        """
        check proxy exists
        :return:
        """
        if type == 0:
            self.db.changeTable(self.raw_proxy_queue)
        elif type == 1:
            self.db.changeTable(self.useful_proxy_queue)
        else:
            self.db.changeTable(self.trash_proxy_queue)
        return self.db.exists(proxy_str)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_list = self.db.getAll()
        return [Proxy.newProxyFromJson(_) for _ in item_list]

    def getTrash(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.trash_proxy_queue)
        item_list = self.db.getAll()
        return [Proxy.newProxyFromJson(_) for _ in item_list]

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        self.db.changeTable(self.trash_proxy_queue)
        total_trash_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue, 'trash_proxy': total_trash_queue }


if __name__ == '__main__':
    pp = ProxyManager()
    pp.fetch()
