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
from Config.base import conf
import token

def program():

    if os.path.exists(conf.get('file','name')):
        ts_name_code=pd.read_csv(conf.get('file','name'))
    else:
        ts_name_code=token.get_namecode()

    ts_code = ts_name_code['ts_code']
    name_code=ts_name_code['name']
    industry=ts_name_code['industry']
    area=ts_name_code['area']
    start=datetime.datetime.now()
    priord=datetime.timedelta(days=int(conf.get('var','timerank')))

    timerank=[]
    for i in range(int(conf.get('var','for_time'))):
        t=[]
        st=start-datetime.timedelta(days=int(conf.get('var','backday')))
        et=st-priord
        t.append(et.strftime(conf.get('var','format')))
        t.append(st.strftime(conf.get('var','format')))
        start=et
        timerank.append(t)

    timerank=timerank[::-1]

    if os.path.exists(conf.get('dir','stock')):
        shutil.rmtree(conf.get('dir','stock'))
        os.mkdir(conf.get('dir','stock'))
    else:
        os.mkdir(conf.get('dir','stock'))

    for i,code in enumerate(ts_code):
        for [st,et] in timerank:
            res=req.get(conf.get('config','req_url').format(code,st,et,'ts_code'))

            print(len(res.json()['list']))
            with open(conf.get('file','json'),"w",encoding="utf-8") as f:
                f.write(json.dumps(res.json()['list']))

            data = pd.read_json(conf.get('file','json'),encoding="utf-8", orient='records')
            data = data.drop_duplicates(['id','ts_code','trade_date'])
            filename=conf.get('dir','stock')+'{}_{}_{}.csv'.format(code,name_code[i],industry[i])
            if os.path.exists(filename):
                data.to_csv(filename,header=None,mode='a',index=None)
            else:
                data.to_csv(filename,index=None)
            #time.sleep(1)

if __name__ == "__main__":
    program()