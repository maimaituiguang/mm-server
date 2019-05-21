# -*- coding: UTF-8 -*-

import conn
import json, time, hashlib
from bson import ObjectId


def verify_user(phone, password):
    m2 = hashlib.md5()
    m2.update(password.encode('utf-8'))

    account = conn.db['account']
    re = account.find_one({'phone': int(phone)})

    if re is not None and re['password'] == m2.hexdigest():
        return True

    return False

