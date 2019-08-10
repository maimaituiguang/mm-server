# -*- coding: UTF-8 -*-

import conn
import time
import random

def publish(cou):
    task = conn.db['task']
    re = list(makeTask('android', cou)) + list(makeTask('iOS', cou))

    endTime = int(time.time()) + 24*60*60
    dict = []
    for item in re:
        temp = {'count': 9999, 'end_time': endTime, 'reward': 2, 'detail': item}
        dict.append(temp)

    task.insert(dict)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ': insert task ' + str(cou))


def makeTask(platform, cou):
    app = conn.db['apps']
    task = conn.db['task']

    last = task.find_one({'detail.platform': platform}, sort=[("end_time", -1)])
    detail = last['detail']

    if detail.has_key('index'):
        index = detail['index']
        total = app.count({'platform': platform})
        index = index if index + cou <= total else 0
    else:
        index = 0

    return app.find({'platform': platform, 'index': {'$gt': index}}, {'_id': 0}).limit(cou)


if __name__ == '__main__':
    publish(3)

    # acc = conn.db['account']
    # re = acc.find()
    # for item in re:
    #     acc.update_one({'_id': item['_id']}, {'$set': {'most_phone': item['super_phone']}})
    #     print item['super_phone']