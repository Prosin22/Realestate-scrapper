# -*- coding: utf-8 -*-
import sqlite3
from pandas.io.json import json_normalize
import json

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class RealestatePipeline:
    def __init__(self):
        self.items = []

    def open_spider(self, spider):
        self.conn = sqlite3.connect("houses.db")
        self.curr = self.conn.cursor()

    def process_item(self, item, spider):
        self.items.append(dict(item))

    def create_table(self, name, columns):
        print("CREATE TABLE IF NOT EXISTS {} (\n".format(name, name)
                          +
                          "".join(["{} text\n".format(col) for col in columns])
                          +
                          ")")
        self.curr.execute("CREATE TABLE IF NOT EXISTS {} (\n".format(name, name)
                          +
                          "".join(["{} text\n".format(col) for col in columns])
                          +
                          ")"
                          )

    def insert_elem(self, name, df):
        for line in df.values:
            print("INSERT INTO {} values (".format(name) + "".join(["'{}',".format(str(elem)) for elem in line]) + ")")
            self.curr.execute(
                "INSERT INTO {} values (".format(name) + "".join(["'{}',".format(str(elem)) for elem in line]) + ")")
        self.conn.commit()
        self.conn.close

    def close_spider(self, spider):

        json_str = json.loads(str(self.items))
        json_format = json_normalize(json_str)
        print(json_format)
        self.create_table(spider.name, json_format.columns)
        self.insert_elem(spider.name, json_format)
