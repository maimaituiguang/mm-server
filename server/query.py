# -*- coding: UTF-8 -*-

import conn
import json
import time
from bson import ObjectId

def apps(offset):
    site = conn.db['apps']
    re = site.find({}, {'_id': 0}).limit(10).skip(offset)
    return json.dumps(list(re))


def task(request):
    phone = __parsePhone(__zc_0(request))

    task = conn.db['task']
    finished = conn.db['finished_task']

    ret = task.find({'end_time': {'$gt': int(time.time())}})
    taskIds = []
    tasks = list(ret)
    for t in tasks:
        taskIds.append(t['_id'])

    ref = finished.find({'task_id': {'$in': taskIds}, 'phone': phone})
    finisheds = list(ref)

    re = []
    for t in tasks:
        have = False
        for one in finisheds:
            if one['task_id'] == t['_id']:
                have = True
                break
        if have == False:
            t['_id'] = str(t['_id'])
            t['status'] = 1 # 进行中的任务
            re.append(t)

    return json.dumps(re)


def all_task(offset):
    task = conn.db['task']
    re = task.find({}, {'_id': 0}).limit(10).skip(offset)
    list = []
    for item in re:
        item['status'] = 0
        list.append(item)
    return json.dumps(list)

def submit_task(request):
    phone = __parsePhone(__zc_0(request))
    dic = json.loads(request.get_data())
    dic['task_id'] = ObjectId(dic['task_id'])
    dic['phone'] = phone
    dic['status'] = 0
    dic['create_time'] = int(time.time())

    finished_task = conn.db['finished_task']
    re = finished_task.insert_one(dic)
    if re.inserted_id != None:
        return True

    return False


def account(request):
    phone = __parsePhone(__zc_0(request))

    re = conn.db['account'].find_one({'phone': phone}, {'_id': 0})
    vip = conn.db['member'].find_one({'type': re['role']})
    re['role_name'] = vip['name']
    re['reward'] = vip['reward']

    return re


def register(request):
    data = json.loads(request.get_data())
    dic = {'phone': int(data['phone']), 'nick': data['nick'], 'task_status': 0, 'account_status': 0, 'role': 0}

    account = conn.db['account']
    re = account.find_one({'phone': int(data['phone'])})
    if re == None:
        # 未注册过
        re = account.insert_one(dic)
        if re.inserted_id == None:
            return False
    else:
        if re['account_status'] != 0:
            # 判断是否被封号
            return False

        # 更新账号数据
        account.update_one({'phone': re['phone']}, {'$set': {'nick': data['nick']}})

    vip = conn.db['member'].find_one({'type': re['role']})
    re['role_name'] = vip['name']
    re['reward'] = vip['reward']
    re['_id'] = str(re['_id'])

    return re


def wallet(request):
    phone = __parsePhone(__zc_0(request))

    wallet = conn.db['wallet']
    re = wallet.find_one({'phone': phone}, {'_id': 0})
    if re != None:
        return re

    return False


def take(request):
    phone = __parsePhone(__zc_0(request))
    data = json.loads(request.get_data())

    take = conn.db['take_record']
    count = float(data['count'])
    dic = {'phone': phone, 'count': count, 'status': 0, 'create_time': int(time.time())}
    re = take.insert_one(dic)

    wallet = conn.db['wallet']
    wre = wallet.update_one({'phone': phone}, {'$inc': {'un_take': -count, 'has_take': count}})
    wallet.update_one({'phone': phone}, {'$set': {'update_time': int(time.time())}})

    if re.inserted_id != None and wre != None:
        return True

    return False


def record(request):
    phone = __parsePhone(__zc_0(request))
    finished = conn.db['finished_task']
    take = conn.db['take_record']

    fre = finished.find({'phone': phone, 'status': 1}, {'_id': 0, 'reward': 1, 'create_time': 1})
    tre = take.find({'phone': phone}, {'_id': 0, 'count': 1, 'create_time': 1})

    lists = []
    times = []
    for i in fre:
        lists.append({'count': i['reward'], 'create_time': i['create_time'], 'type': 0})
        times.append(i['create_time'])

    for item in tre:
        lists.append({'count': item['count'], 'create_time': item['create_time'], 'type': 1})
        times.append(item['create_time'])

    times.sort()
    times.reverse()

    sort_list = []
    for t in times:
        for item in lists:
            if item['create_time'] == t:
                sort_list.append(item)
                break

    return json.dumps(sort_list)


def view_task(req, status):
    phone = __parsePhone(__zc_0(req))
    f_task = conn.db['finished_task']

    re = f_task.find({'phone': phone, 'status': status}).limit(20)
    taskIds = []
    tasks = list(re)
    for t in tasks:
        taskIds.append(t['task_id'])

    task = conn.db['task']
    ref = task.find({'_id': {'$in': taskIds}}, {'_id': 0})

    return json.dumps(list(ref))


def members():
    m = conn.db['member']
    re = m.find({}, {'_id': 0})

    return json.dumps(list(re))

def update_account(req):
    phone = __parsePhone(__zc_0(req))
    account = conn.db['account']
    data = json.loads(req.get_data())

    dic = {}
    if data.has_key('task_status'):
        dic['task_status'] = data['task_status']
    if data.has_key('nick'):
        dic['nick'] = data['nick']
    if data.has_key('role'):
        dic['role'] = data['role']
    if data.has_key('account_status'):
        dic['account_status'] = data['account_status']
    if data.has_key('alipay'):
        dic['alipay'] = data['alipay']

    re = account.update_one({'phone': phone}, {'$set': dic})
    return re != None









def __headers(req, key):
    return req.headers[key]

def __zc_0(req):
    return __headers(req, 'zc_0')


def __parsePhone(phone):
    return int(phone) / 12345