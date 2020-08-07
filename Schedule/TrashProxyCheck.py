# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     TrashProxyCheck
   Description :   check useful proxy
   Author :        JHao
   date：          2019/8/7
-------------------------------------------------
   Change Activity:
                   2019/8/7: check useful proxy
-------------------------------------------------
"""
__author__ = 'JHao'

from threading import Thread

try:
    from Queue import Queue, Empty  # py2
except:
    from queue import Queue, Empty  # py3

from Util import LogHandler
from Manager import ProxyManager
from ProxyHelper import checkProxyUseful, Proxy

FAIL_COUNT = 3  # 清理时间= 调度时间间隔 * FAIL_COUNT
CHECK_COUNT = 100 # 有效使用次数代理，失效后写入日志文件中记录
RECYCLE_COUNT=10

class TrashProxyCheck(ProxyManager, Thread):
    def __init__(self, queue, thread_name):
        ProxyManager.__init__(self)
        Thread.__init__(self, name=thread_name)

        self.queue = queue
        self.log = LogHandler('trash_proxy_check')
        self.proxy_log = LogHandler('purge_trash_proxy')

    def run(self):
        self.log.info("TrashProxyCheck - {}  : start".format(self.name))
        self.db.changeTable(self.trash_proxy_queue)
        while True:
            try:
                proxy_str = self.queue.get(block=False)
            except Empty:
                self.log.info("TrashProxyCheck - {}  : exit".format(self.name))
                break

            proxy_obj = Proxy.newProxyFromJson(proxy_str)
            proxy_obj, status = checkProxyUseful(proxy_obj)
            if status:
                if proxy_obj.check_count > RECYCLE_COUNT:
                    self.put(proxy_obj) # recycle proxy to useful proxy queue
                    self.log.info('TrashProxyCheck - {}  : {} validation pass recycle to usefulQueue.'.format(self.name, proxy_obj.proxy.ljust(20)))
                else:
                    self.log.info('TrashProxyCheck - {}  : {} validation pass but doesnt recycle count{}.'.format(self.name, proxy_obj.proxy.ljust(20),proxy_obj.check_count))
            elif proxy_obj.fail_count >= FAIL_COUNT:
                self.log.info('TrashProxyCheck - {}  : {} validation fail purge permanently.'.format(self.name,
                                                                                  proxy_obj.proxy.ljust(20)))
                self.delete(proxy_obj, type=2)  # remove proxy permanently
                if proxy_obj.check_count >= CHECK_COUNT:
                    self.proxy_log.info('proxy: {} check_count: {}'.format(proxy_obj.proxy, proxy_obj.check_count))
            else:
                self.log.info('TrashProxyCheck - {}  : {} validation fail count:{}.'.format(self.name,
                                                                                  proxy_obj.proxy.ljust(20), proxy_obj.fail_count))
                self.put(proxy_obj, type=2) # update failed_count
            self.queue.task_done()


def doTrashProxyCheck():
    proxy_queue = Queue()

    pm = ProxyManager()
    pm.db.changeTable(pm.trash_proxy_queue)
    for _proxy in pm.db.getAll():
        proxy_queue.put(_proxy)

    thread_list = list()
    for index in range(20):
        thread_list.append(TrashProxyCheck(proxy_queue, "thread_%s" % index))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


if __name__ == '__main__':
    doTrashProxyCheck()
