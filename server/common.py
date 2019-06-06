# -*- coding: UTF-8 -*-

import hashlib


def md5(text='123456'):
    m2 = hashlib.md5()
    m2.update(text.encode('utf-8'))
    return m2.hexdigest()
