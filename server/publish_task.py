# -*- coding: UTF-8 -*-

import conn
import time
import random

def publish(cou):
    app = conn.db['apps']
    task = conn.db['task']

    total = app.count()
    offset = random.randint(0, total - cou - 1)

    re = app.find({}, {'_id': 0}).limit(cou).skip(offset)

    endTime = int(time.time()) + 24*60*60

    dict = []
    for item in re:
        temp = {'count': 9999, 'end_time': endTime, 'reward': 2, 'detail': item}
        dict.append(temp)

    task.insert(dict)

    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ': insert task ' + str(cou)


if __name__ == '__main__':
    publish(3)