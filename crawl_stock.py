

from matplotlib import font_manager
from urllib import request
import json
import pandas as pd
from datetime import datetime
from threading import Timer

def Time_threading(inc):
    print(datetime.now())
    t = Timer(inc,Time_threading,(inc,))
    t.start()
    df = get_stock_data('sz000829',30,30)
    #导入到excel
    df.to_csv("~/Desktop/000829_stock.csv", encoding="gbk", index=False)
    print(df)
    df.head()


def get_stock_data(id,scale,data_len):
    symsol = '股票代码'
    scale = scale
    data_len = data_len
    url = 'http://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={0}&scale={1}&datalen={2}'.format(id, scale, data_len)
    req = request.Request(url)
    rsp = request.urlopen(req)
    res = rsp.read()
    res_json = json.loads(res)
    bar_list = []
    res_json.reverse()
    print(res_json)
    for dict in res_json:
        bar = {}
        bar['date'] = dict['day']
        bar['open'] = float(dict['open'])
        bar['high'] = float(dict['high'])
        bar['low'] = float(dict['low'])
        bar['close'] = float(dict['close'])
        bar['volume'] = int(dict['volume'])
        bar_list.append(bar)
    df = pd.DataFrame(data=bar_list)
    # show_k_line(bar_list,bar_list2,high_list,high_list2)
    return df

#函数调用 60标识一分钟
Time_threading(60)