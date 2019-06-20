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
    total = app.find({'platform': platform}).count()
    offset = random.randint(0, total - cou - 1)
    return app.find({'platform': platform}, {'_id': 0}).limit(cou).skip(offset)



if __name__ == '__main__':
    publish(3)
