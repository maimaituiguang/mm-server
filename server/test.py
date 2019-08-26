# -*- coding: UTF-8 -*-

import conn
import time
import datetime


def run():
    yao = conn.db['yao_record']
    re = yao.find({})
    # print(len(list(re)))
    for item in re:
        stamp = time.mktime(datetime.datetime.strptime(item['create_time'], "%Y-%m-%d %H:%M:%S").timetuple())
        yao.update_one({'_id': item['_id']}, {'$set': {'create_timestamp': int(stamp)}})
        print(stamp)

if __name__ == '__main__':
    pass
    # run()