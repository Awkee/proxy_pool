# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/8/5: ProxyScheduler
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.append('../')

from Schedule import doRawProxyCheck, doUsefulProxyCheck, doTrashProxyCheck
from Manager import ProxyManager
from Util import LogHandler
import time


class DoFetchProxy(ProxyManager):
    """ fetch proxy"""

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('fetch_proxy')

    def main(self):
        self.log.info("start fetch proxy")
        self.fetch()
        self.log.info("finish fetch proxy")


def rawProxyScheduler():
    DoFetchProxy().main()
    doRawProxyCheck()


def usefulProxyScheduler():
    doUsefulProxyCheck()


def trashProxyScheduler():
    doTrashProxyCheck()

def runScheduler():
    rawProxyScheduler()
    usefulProxyScheduler()
    trashProxyScheduler()

    scheduler_log = LogHandler("scheduler_log")
    scheduler = BackgroundScheduler(logger=scheduler_log)

    scheduler.add_job(rawProxyScheduler, 'interval', minutes=5, id="raw_proxy_check", name="raw_proxy定时采集")
    scheduler.add_job(usefulProxyScheduler, 'interval', minutes=1, id="useful_proxy_check", name="useful_proxy定时检查")
    scheduler.add_job(trashProxyScheduler, 'interval', minutes=2, id="trash_proxy_check", name="trash_proxy定时回收检查")

    scheduler.start()
    try:
        while True:
            time.sleep(30)
            print('scheduler sleep a moment!')
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('scheduler shutdown.')


if __name__ == '__main__':
    runScheduler()
