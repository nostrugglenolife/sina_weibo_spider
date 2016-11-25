# -*- coding: utf-8 -*-
import pymongo
from sina_spider.items import InformationItem, ContentsItem


class MongoDBPipleline(object):
    def __init__(self):
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["SinaWeibo"]
        self.Information = db["Information"]
        self.Contents = db["Contents"]
        self.Follows = db["Follows"]
        self.Fans = db["Fans"]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, InformationItem):
            try:
                self.Information.insert(item['informations'])
            except Exception:
                pass
        elif isinstance(item, ContentsItem):
            try:
                self.Contents.insert(item['contents'])
            except Exception:
                pass
        return item
