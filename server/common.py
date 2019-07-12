# -*- coding: UTF-8 -*-

import hashlib, time, datetime


def md5(text='123456'):
    m2 = hashlib.md5()
    m2.update(text.encode('utf-8'))
    return m2.hexdigest()


def currentTime():
    # return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    timeArray = datetime.datetime.utcfromtimestamp(time.time() + 28800)
    return timeArray.strftime("%Y-%m-%d %H:%M:%S")
