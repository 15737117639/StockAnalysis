#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   scrapy.py
@Time    :   2020/07/01 11:35:00
@Author  :   sui mingyang 
@Version :   0.0.1
@Contact :   suimingyang123@gmail.com
@License :   (C)Copyright 2018-2019, weidian
@Desc    :   None
'''

# here put the import lib

import requests as req
import pandas as pd
import numpy as np
import json
import datetime
import os
import time
import shutil
import threading
from threadpool import ThreadPool,makeRequests
from Config.base import conf
import token

class Stock(object):
    def __init__(self):
        self.lock = threading.Lock()

    def __get_namecode__(self):
        if os.path.exists(conf.get('file','name')):
            ts_name_code=pd.read_csv(conf.get('file','name'))
        else:
            ts_name_code=token.get_namecode()

        self.ts_code = ts_name_code['ts_code']
        self.name_code=ts_name_code['name']
        self.industry=ts_name_code['industry']
        self.area=ts_name_code['area']
        start=datetime.datetime.now()
        self.priord=datetime.timedelta(days=int(conf.get('var','timerank')))
        self.__get_timerank__(start)

    def __get_timerank__(self,start):
        self.timerank=[]
        for i in range(int(conf.get('var','for_time'))):
            t=[]
            st=start-datetime.timedelta(days=int(conf.get('var','backday')))
            et=st-self.priord
            t.append(et.strftime(conf.get('var','format')))
            t.append(st.strftime(conf.get('var','format')))
            start=et
            self.timerank.append(t)

        #self.timerank=timerank[::-1]

    def program(self):
        self.__get_namecode__()

        if os.path.exists(conf.get('dir','stock')):
            shutil.rmtree(conf.get('dir','stock'))
            os.mkdir(conf.get('dir','stock'))
        else:
            os.mkdir(conf.get('dir','stock'))

        pool = ThreadPool(10)
        param=[]
        for i,code in enumerate(self.ts_code):
            for [st,et] in self.timerank:
                url=conf.get('config','req_url').format(code,st,et,'ts_code')
                param.append(([i,code,url,st,et],None))
        
        reqs = makeRequests(self.get_data,param)

        [pool.putRequest(req) for req in reqs] 

        pool.wait()

    def get_data(self,i,code,url,st,et):
        #for i,code in enumerate(ts_code):
        res=req.get(url)
        print(code,self.name_code[i],self.industry[i],len(res.json()['list']))
        jsonfile=conf.get('dir','stock')+'{}_{}_{}_{}_{}.json'.format(code,self.name_code[i],self.industry[i],st,et)

        with open(jsonfile,"w",encoding="utf-8") as f:
            f.write(json.dumps(res.json()['list']))

        filename=conf.get('dir','stock')+'{}_{}_{}.csv'.format(code,self.name_code[i],self.industry[i])

        data = pd.read_json(jsonfile,encoding="utf-8", orient='records')
        data = data.drop_duplicates(['id','ts_code','trade_date'])
        self.lock.acquire(1)
        if os.path.exists(filename):
            data.to_csv(filename,header=None,mode='a',index=None)
        else:
            data.to_csv(filename,index=None)
        self.lock.release()
        #time.sleep(1)
        os.remove(jsonfile)

if __name__ == "__main__":
    stock=Stock()
    stock.program()