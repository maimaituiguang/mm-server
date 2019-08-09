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
        wallet = conn.db['wallet']

        re = account.find_one({'phone': int(phone)})
        old_role = 0
        if re.has_key('role'):
            old_role = int(re['role'])

        account.update_one({'phone': int(phone)}, {'$set':{'role': int(role), 'update_time': int(time.time())}})
        # if int(role) == 4 and old_role == 0:
        #     wallet.update_one({'phone': int(phone)}, {'$inc': {'un_take': 298.0}})

        ms = conn.db['member'].find({})
        old_price = 0
        new_price = 0
        for m in ms:
            if m['type'] == old_role:
                old_price = m['price']
                continue
            if m['type'] == int(role):
                new_price = m['price']
                continue

        price = (new_price - old_price) * 5.0 / 100.0

        yao_user = None
        if re.has_key('yao_code'):
            yao_user = account.find_one({'user_id': re['yao_code']})

        role_phone = "0"
        if yao_user is not None and yao_user.has_key('phone'):
            role_phone = yao_user['phone']
            wallet.update_one({'phone': int(role_phone)}, {'$inc': {'un_take': price}})

        conn.db['yao_record'].insert_one({'phone': int(role_phone), 'yao_phone': int(phone), 'price': price, 'create_time': common.currentTime(), 'create_timestamp': int(time.time())})
 
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

def update_account_status(account_status, phone):
    try:
        account = conn.db['account']
        account.update_one({'phone': int(phone)}, {'$set':{'account_status': int(account_status)}})
        return json.dumps({'success': True})
    except:
        return json.dumps({'success': False})


def finished_task(offset=0):
    try:
        task = conn.db['finished_task']
        re = task.find({'status': 0}, {'task_id': 0}).limit(10).skip(offset).sort('create_time', -1)
        lists = []
        phones = []
        for item in re:
            item['_id'] = str(item['_id'])
            timeArray = datetime.datetime.utcfromtimestamp(item['create_time'] + 28800) 
            item['create_time'] = timeArray.strftime("%Y-%m-%d %H:%M:%S")
            lists.append(item)
            if item['phone'] in phones:
              continue
            phones.append(item['phone'])

        users = conn.db['account'].find({'phone': {'$in': phones}})
        for us in users:
            for ta in lists:
                if ta['phone'] == us['phone'] and us.has_key('mark'):
                    ta['mark'] = us['mark']

        return json.dumps(lists)
    except:
        return json.dumps([])


def task_pass(request):
    data = json.loads(request.get_data())

    task = conn.db['finished_task']
    re = task.update_one({'_id': ObjectId(data['_id'])}, {'$set': {'status': int(data['status'])}})
    if re.modified_count != 1:
        return json.dumps({'success': False, 'info': '操作失败，请重试'})

    if int(data['status']) != 1:
        return json.dumps({'success': True})

    # 更新钱包数据
    wallet = conn.db['wallet']
    wallet.update_one({'phone': int(data['phone'])}, {'$inc': {'un_take': int(data['reward'])}})

    account = conn.db['account']
    ac = account.find_one({'phone': int(data['phone'])}, {'_id': 0, 'yao_code': 1})
    if ac is not None and ac.has_key('yao_code') and len(ac['yao_code']) > 0:
        yao_ac = account.find_one({'user_id': ac['yao_code']}, {'_id': 0, 'phone': 1, 'role': 1})

    # 合伙人
    if yao_ac is not None and yao_ac['role'] == 10:
        wallet.update_one({'phone': int(yao_ac['phone'])}, {'$inc': {'un_take': int(data['reward']) * 20 / 100}})

    return json.dumps({'success': True})


    

def all_take(offset=0):
    wallet = conn.db['wallet']
    take = conn.db['take_record']
    acc = conn.db['account']

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

    users = acc.find({'phone': {'$in': phones}})
    for us in users:
        for ta in ttre:
            if ta['phone'] == us['phone'] and us.has_key('mark'):
                ta['mark'] = us['mark']

    return json.dumps(ttre)


def take_finished(_id, status):
    take = conn.db['take_record']
    re = take.update_one({'_id': ObjectId(_id)}, {'$set':{'status': status}})
    if re.modified_count == 1:
        return json.dumps({'success': True})
    
    return json.dumps({'success': False, 'info': '更新失败，请重试'})



def wallet_list():
    white_list = ['15236657589', '17127122655', '13044744473', '18338911968']

    wallet = conn.db['wallet']
    account = conn.db['account']
    record = conn.db['yao_record']

    re = list(wallet.find({}, {'_id': 0}))
    record = record.find({}, {'_id': 0, 'price': 1, 'yao_phone': 1})

    phone_list = []
    record_dic = {}
    for cord in record:
        phone = str(cord['yao_phone'])
        if phone not in phone_list:
            phone_list.append(phone)
            record_dic[phone] = cord['price']
            continue
        else:
            record_dic[phone] = record_dic[phone] + cord['price']
            continue

    are = account.find({'role': {'$gt': 0}}).sort('update_time', 1)
    account_result = list(are)
    
    result = []
    for item_cnt in account_result:
        if str(item_cnt['phone']) in white_list:
            continue
        for item in re:
            if item['phone'] != item_cnt['phone']:
                continue

            item['account_status'] = item_cnt['account_status']
            item['task_status'] = item_cnt['task_status']
            item['all_reward'] = item['has_take'] + item['un_take']
            if item_cnt.has_key('card'):
                item['name'] = item_cnt['card']['userName']
            if record_dic.has_key(str(item['phone'])):
                item['input'] = record_dic[str(item['phone'])] / 0.05
                if item['input'] > 10:
                    item['rate'] = item['all_reward'] / item['input'] * 100
            result.append(item)

    return json.dumps(result)


def remark(phone, mark):
    acc = conn.db['account']
    acc.update_one({'phone': int(phone)}, {'$set': {'mark': mark}})
    return search(phone)
    
