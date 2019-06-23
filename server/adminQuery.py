# -*- coding: UTF-8 -*-

import conn, common
import json, time, datetime
from bson import ObjectId


def verify_user(phone, password):
    account = conn.db['account']
    try:
        re = account.find_one({'phone': int(phone)})
        return re is not None and re.has_key('password') and re['password'] == common.md5(password) and re.has_key('super_member') and re['super_member'] == 1
    except:
        return False

def search(phone):
    # phone 参数的值可表示 userID 或 phone

    where = {}
    if len(phone) == 11:
        where = {'phone': int(phone)}
    else:
        where = {'user_id': phone}

    try:
        account = conn.db['account']
        member = conn.db['member']
        re = account.find_one(where, {'_id': 0})
        mre = member.find_one({'type': re['role']}, {'_id': 0})
        if re is not None and mre is not None:
            re['member'] = dict(mre)
            return json.dumps([dict(re)])
    except:
        return json.dumps([])

def update_role(role, phone):
    try:
        account = conn.db['account']
        account.update_one({'phone': int(phone)}, {'$set':{'role': int(role), 'update_time': int(time.time())}})

        re = account.find_one({'phone': int(phone)})
        re = account.find_one({'user_id': re['yao_code']})

        ms = conn.db['member'].find_one({'type': int(role)})
        price = ms['price'] * 5.0 / 100.0

        conn.db['yao_record'].insert_one({'phone': int(re['phone']), 'yao_phone': int(phone), 'price': price, 'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        conn.db['wallet'].wallet.update_one({'phone': int(re['phone'])}, {'$inc': {'un_take': price}})

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

def finished_task(offset=0):
    try:
        task = conn.db['finished_task']
        re = task.find({'status': 0}, {'task_id': 0}).limit(10).skip(offset).sort('create_time', -1)
        lists = []
        for item in re:
            item['_id'] = str(item['_id'])
            timeArray = datetime.datetime.utcfromtimestamp(item['create_time'] + 28800) 
            item['create_time'] = timeArray.strftime("%Y-%m-%d %H:%M:%S")
            lists.append(item)
        return json.dumps(lists)
    except:
        return json.dumps([])


def task_pass(request):
    data = json.loads(request.get_data())

    task = conn.db['finished_task']
    re = task.update_one({'_id': ObjectId(data['_id'])}, {'$set': {'status': int(data['status'])}})
    if re.modified_count == 1:
        if int(data['status']) == 2:
            return json.dumps({'success': True})

        # 更新钱包数据
        wallet = conn.db['wallet']
        re = wallet.update_one({'phone': int(data['phone'])}, {'$inc': {'un_take': int(data['reward'])}})
        if re.modified_count == 1:
            return json.dumps({'success': True})

    return json.dumps({'success': False, 'info': '操作失败，请重试'})
    

def all_take(offset=0):
    wallet = conn.db['wallet']
    take = conn.db['take_record']

    tt = take.find({'status': 0}).limit(10).skip(offset).sort('create_time', -1)
    phones = []
    ttre = []
    for item in tt:
        item['_id'] = str(item['_id'])
        timeArray = datetime.datetime.utcfromtimestamp(item['create_time'] + 28800) 
        item['create_time'] = timeArray.strftime("%Y-%m-%d %H:%M:%S")
        ttre.append(item)
        if item['phone'] in phones:
            continue
        phones.append(item['phone'])

    ww = wallet.find({'phone': {'$in': phones}}, {'_id': 0})
    for wal in ww:
        for ta in ttre:
            if ta['phone'] == wal['phone']:
                ta['totals'] = float(wal['un_take'] + wal['has_take'])

    return json.dumps(ttre)


def take_finished(_id, status):
    take = conn.db['take_record']
    re = take.update_one({'_id': ObjectId(_id)}, {'$set':{'status': status}})
    if re.modified_count == 1:
        return json.dumps({'success': True})
    
    return json.dumps({'success': False, 'info': '更新失败，请重试'})
