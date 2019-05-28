# -*- coding: UTF-8 -*-

import conn
import json, time, hashlib
from bson import ObjectId


def verify_user(phone, password):
    m2 = hashlib.md5()
    m2.update(password.encode('utf-8'))
    account = conn.db['account']
    try:
        re = account.find_one({'phone': int(phone)})
        return re != None and re.has_key('password') and re['password'] == m2.hexdigest()  
    except:
        return False

def search(phone):
    try:
        account = conn.db['account']
        member = conn.db['member']
        re = account.find_one({'phone': int(phone)}, {'_id': 0})
        mre = member.find_one({'type': re['role']}, {'_id': 0})
        if re != None and mre != None:
            re['member'] = dict(mre)
            return json.dumps([dict(re)])
    except:
        return json.dumps([])

def update_role(role, phone):
    try:
        account = conn.db['account']
        account.update_one({'phone': int(phone)}, {'$set':{'role': int(role), 'update_time': int(time.time())}})
        return search(phone)
    except:
        return json.dumps([])
        
def update_status(task_status, phone):
    try:
        account = conn.db['account']
        account.update_one({'phone': int(phone)}, {'$set':{'task_status': int(task_status)}})
        return json.dumps({'success': True})
    except:
        return json.dumps({'success': False})

def all_task(offset=0):
    try:
        task = conn.db['finished_task']
        re = task.find({'status': 0}, {'_id': 0, 'task_id': 0}).limit(10).skip(offset).sort('create_time', -1)
        return json.dumps(list(re))
    except:
        return json.dumps([])



