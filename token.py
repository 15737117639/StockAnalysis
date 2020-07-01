import tushare as ts
from Config.base import conf

def get_namecode():
    pro = ts.pro_api(conf.get('dir','token'))
    ts_name_code = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    #pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    #pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    ts_name_code.to_csv(conf.get('file','name'),index=None)

    return ts_name_code

