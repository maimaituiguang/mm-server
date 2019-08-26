# -*- coding: UTF-8 -*-

import datetime
import json
import time
import random

from bson import ObjectId

import common
import conn


def apps(offset):
    site = conn.db['apps']
    re = site.find({}, {'_id': 0}).limit(10).skip(offset)
    return json.dumps(list(re))


# 同时支持 iOS / Android 的不同数据
def task(request):
    phone = __parsePhone(__zc_0(request))
    account = conn.db['account'].find_one({'phone': int(phone)})
    if account['task_status'] == 1:
        return json.dumps({'message': '警告：由于您提交虚假任务被系统识别，已停止您的任务权限，如有疑问请联系客服～'})

    # 当前的请求来源 android/iOS
    agent = request.headers['User-Agent']
    platform = 'android'
    pre_url = 'https://www.qimai.cn/andapp/baseinfo/appid/'
    if 'iPhone' in agent:
        platform = 'iOS'
        pre_url = 'https://www.qimai.cn/app/baseinfo/appid/'

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
        if have is True:
            continue
        detail = t['detail']
        t['_id'] = str(t['_id'])
        t['status'] = 1  # 进行中的任务, 用于不同 cell 状态的展示
        t['pageUrl'] = pre_url + str(detail['appId'])
        if detail.has_key('platform'):
            if detail['platform'] == platform:
                re.append(t)
        else:
            re.append(t)

    return json.dumps(re)


def all_task(offset):
    task = conn.db['task']
    re = task.find({'end_time': {'$lt': int(time.time())}}, {'_id': 0}).limit(10).skip(offset).sort('end_time', -1)
    list = []
    for item in re:
        item['status'] = 0
        list.append(item)
    return json.dumps(list)


def submit_task(request):
    phone = __parsePhone(__zc_0(request))

    today = datetime.date.today()
    today_time = int(time.mktime(today.timetuple()))

    ref = conn.db['finished_task'].find({'create_time': {'$gt': today_time}, 'phone': int(phone)})
    if len(list(ref)) >= 3:
        return False

    dic = json.loads(request.get_data())
    dic['task_id'] = ObjectId(dic['task_id'])
    dic['phone'] = phone
    dic['status'] = 0
    # 这里的时间戳只能用 time.time(), 和 crontab 有关
    dic['create_time'] = int(time.time())
    try:
        task = conn.db['task']
        info = task.find_one({'_id': dic['task_id']})
        dic['detail'] = info['detail']

        finished_task = conn.db['finished_task']
        re = finished_task.insert_one(dic)
        if re.inserted_id is not None:
            return True
    except:
        return False

    return False


def account(request):
    phone = __parsePhone(__zc_0(request))
    re = conn.db['account'].find_one({'phone': int(phone)}, {'_id': 0})

    vip = conn.db['member'].find_one({'type': re['role']})
    re['role_name'] = vip['name']
    re['reward'] = vip['reward']

    return re


def register(request):
    data = json.loads(request.get_data())
    dic = {'task_status': 0, 'account_status': 0, 'role': 0}

    account = conn.db['account']
    re = account.find_one({'super_phone': int(data['phone']), 'most_phone': int(data['phone'])})
    if re is None:
        # 未注册用户
        # 最后统一为 re 付值
        re = dic
        if data.has_key('nick'):
            re['nick'] = data['nick']
        else:
            re['nick'] = '注册用户'

        if data.has_key('password'):
            re['password'] = common.md5(data['password'])

        if data.has_key('yaoCode'):
            re['yao_code'] = data['yaoCode']

        identifier = __makeIdentifier()

        re['super_phone'] = int(data['phone'])
        re['most_phone'] = int(data['phone'])
        re['user_id'] = identifier
        re['phone'] = int(identifier)
        re['create_time'] = common.currentTime()

        ire = account.insert_one(dic)
        if ire.inserted_id is None:
            return False
        else:
            # 新用户送 19 元
            wallet = conn.db['wallet']
            w_dic = {'phone': re['phone'], 'un_take': 19.0, 'has_take': 0.0, 'update_time': int(time.time())}
            wallet.insert_one(w_dic)
    else:
        if re['account_status'] != 0:
            # 判断是否被封号
            return False

        # 更新账号数据
        update_data = {'nick': re['nick']}
        if data.has_key('nick'):
            update_data['nick'] = data['nick']
        if data.has_key('password'):
            update_data['password'] = common.md5(data['password'])

        account.update_one({'most_phone': re['most_phone']}, {'$set': update_data})

    vip = conn.db['member'].find_one({'type': re['role']})
    if vip is None:
        return False

    re['role_name'] = vip['name']
    re['reward'] = vip['reward']
    re['_id'] = str(re['_id'])

    return re


def client_login(request):
    data = json.loads(request.get_data())

    account = conn.db['account']
    re = account.find_one(
        {'super_phone': int(data['phone']), 'password': common.md5(data['password']), 'most_phone': int(data['phone'])})
    if re is None:
        return '账号或密码错误'

    if re['account_status'] != 0:
        return '由于您严重违反了「麦麦推广」用户协议第 2.3 条，平台将永久封禁您的账号，如有疑问请联系客服 QQ：2241294891'

    vip = conn.db['member'].find_one({'type': re['role']})
    if vip is None:
        return '登录失败，请重试'

    re['role_name'] = vip['name']
    re['reward'] = vip['reward']
    re['_id'] = str(re['_id'])
    return re


def sub_account_list(request):
    phone = __parsePhone(__zc_0(request))
    accs = conn.db['account'].find({'super_phone': int(phone)}, {'_id': 0})
    members = conn.db['member'].find()
    mbs = {}
    for m in members:
        mbs[m['type']] = {'name': m['name'], 'reward': m['reward']}

    sub_list = []
    for item in accs:
        item['role_name'] = mbs[item['role']]['name']
        item['reward'] = mbs[item['role']]['reward']
        item['account_status_name'] = '' if item['task_status'] == 0 else '禁任务'
        if item['account_status'] != 0:
            item['account_status_name'] = '封号'
        sub_list.append(item)

    return sub_list


def add_account(request):
    phone = __parsePhone(__zc_0(request))
    return create_account(phone)


def create_account(super_phone, role=0):
    acc = conn.db['account']
    accs = list(acc.find({'super_phone': int(super_phone)}))
    if len(accs) == 0:
        return {'success': False, 'message': '没有找到主账号，请联系客户！'}

    yao_code = ''
    for item in accs:
        if item['role'] == 0:
            return {'success': False, 'message': u'ID 为 %s 的账号还未升级会员，不可再次创建子账号! ' % item['user_id']}
        if item.has_key('most_phone'):
            yao_code = item['user_id']

    dic = accs[0]
    identifier = __makeIdentifier()

    dic['nick'] = '子账号 0%d' % len(accs)
    dic['phone'] = int(identifier)
    dic['user_id'] = identifier
    dic['yao_code'] = yao_code
    dic['role'] = role
    dic['task_status'] = 0
    dic['account_status'] = 0
    dic['create_time'] = common.currentTime()

    dic.pop('most_phone')
    dic.pop('password')
    dic.pop('_id')

    re = acc.insert_one(dic)
    if re is None or re.inserted_id is None:
        return {'success': False, 'message': '创建失败，请重试！'}

    wallet = conn.db['wallet']
    w_dic = {'phone': dic['phone'], 'un_take': 0.0, 'has_take': 0.0, 'update_time': int(time.time())}
    wallet.insert_one(w_dic)

    return {'success': True, 'message': dic}


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

    account = conn.db['account']
    acc = account.find_one({'phone': phone})

    take = conn.db['take_record']
    count = float(data['count'])
    dic = {'phone': phone, 'count': count, 'status': 0, 'create_time': int(time.time())}
    if acc.has_key('card'):
        dic['card'] = acc['card']

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
    dic = {}
    tasks = list(re)
    for t in tasks:
        taskIds.append(t['task_id'])
        dic[str(t['task_id'])] = t

    task = conn.db['task']
    ref = task.find({'_id': {'$in': taskIds}}).sort('end_time', -1)
    tasks = []
    for item in ref:
        item['_id'] = str(item['_id'])
        item['reward'] = dic[item['_id']]['reward']
        item['number'] = dic[item['_id']]['app_number']
        item['password'] = dic[item['_id']]['app_password']
        tasks.append(item)

    return json.dumps(tasks)


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
    if data.has_key('card'):
        dic['card'] = data['card']

    re = account.update_one({'phone': phone}, {'$set': dic})
    return re != None


def __headers(req, key):
    return req.headers[key]


def __zc_0(req):
    return __headers(req, 'zc_0')


def __parsePhone(phone):
    return int(phone) / 12345


def __makeIdentifier():
    return str(int(time.time()))