# -*- coding: UTF-8 -*-
from pymongo import MongoClient

__client = MongoClient('167.179.116.178', 27000, connect=False)

db = __client['qimaidb']