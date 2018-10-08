import json
import requests
import pymysql
from http.cookiejar import Cookie
#下面三行为getcookie添加
import os
import sqlite3
from win32.win32crypt import CryptUnprotectData
import time
from pymysql.times import Timestamp
from matplotlib._constrained_layout import _in_same_column
 
def getcookiefromchrome(host='.xueqiu.com'):
  cookiepath=os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
  sql="select host_key,name,encrypted_value from cookies where host_key='%s'" % host
  with sqlite3.connect(cookiepath) as conn:
    cu=conn.cursor()    
    cookies={name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
    #print(cookies)
    return cookies


# mysql_coon 主要的功能就是, 将链接数据库的操作变成只连接一次
#
class mysql_conn(object):
    # 魔术方法, 初始化, 构造函数
    def __init__(self):
        self.db = pymysql.connect(host="localhost",user="test",password="test",db="stock",port=3311, charset="utf8mb4" )
        self.cursor = self.db.cursor()
    # 执行modify(修改)相关的操作
    def execute_modify_mysql(self, sql):
        self.cursor.execute(sql)
    def execute_commit(self):
        self.db.commit()    
    # 获取查询结果集
    def execute_select(self,sql):
        result=[]
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    # 魔术方法, 析构化 ,析构函数
    def __del__(self):
        self.cursor.close()
        self.db.close()



headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'stock.xueqiu.com',
    'Referer': 'https://xueqiu.com/S',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


#股票日线数据
#symble=股票代码
#begin=开始时间
#end=结束时间
#period=期间--day、week、month、quarter、year
#type=before，afte，normal 前除权，后，不除权
#indicator=kline，K线数据，ma-均线....kline,ma,macd,kdj,boll,rsi,wr,bias,cci,psy'


url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={symbol}&begin=600000000000&end={timestamp}&period=day&type=before&indicator=kline'


#获取股票代码、实时行情

#连接数据库
mc = mysql_conn()
stock_symbol_list = mc.execute_select('select a.symbol from stocks a LEFT JOIN kline_log b on a.symbol=b.symbol where b.symbol is null order by a.symbol asc')
stock_count=0


#获取股票基础信息
for (stock_symbol,) in stock_symbol_list:
    
    stock_count=stock_count+1
    timestp=int(round(time.time() * 1000))
    #降低速度
    #time.sleep(0.3)
       
    print('第%d支，%s-获取日线数据中...'%(stock_count,stock_symbol))
    
    response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
    #print(response.status_code)
    #重复读取，直到成功
    while response.status_code != requests.codes.ok:
        print('重复读取第%d支股票，%s'%(stock_count,stock_symbol))
        time.sleep(0.3)
        timestp=int(round(time.time() * 1000))
        response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
    else:
        #存储数据
        pass
    
    res_dict = json.loads(response.text)
    kline_json = res_dict['data']
    error_code=res_dict['error_code']
    error_description=res_dict['error_description']
    
    #print(kline_json['symbol'])
    #print(kline_json['column'])
    #print(kline_json['item'][0])

    for kline_item in kline_json['item']:
        #print(kline_item)
        data={}
        data['symbol']=stock_symbol
        data['timestamp']=kline_item[0]/1000
        data['volume']=kline_item[1]
        data['open']=round(kline_item[2],2)
        data['high']=round(kline_item[3],2)
        data['low']=round(kline_item[4],2)
        data['close']=round(kline_item[5],2)
        data['chg']=round(kline_item[6],2)
        data['percent']=round(kline_item[7],2)
        data['turnoverrate']=round(kline_item[8],2) #换手率
        data['period']='day'    #日线
        data['type']='before'   #前复权
        
        try:
            sql = 'insert into kline(symbol,timestamp,volume,open,high,low,close,chg,percent,turnoverrate,period,type) \
                   values("{symbol}", from_unixtime("{timestamp}"),"{volume}","{open}","{high}","{low}","{close}","{chg}","{percent}","{turnoverrate}","{period}","{type}") \
                   on duplicate key update volume="{volume}",open="{open}",high="{high}",low="{low}",close="{chg}",chg="{chg}",percent="{percent}",turnoverrate="{turnoverrate}",period="{period}",type="{type}"'.format(**data)
            #print(sql)
            mc.execute_modify_mysql(sql)
            #print('第%d支——%s %s 日线爬取成功 ' %(stock_count,stock_symbol,time.strftime('%Y-%m-%d',time.localtime(data['timestamp']))))
        except Exception as e :
            print('以上内容出错，没有存到数据库')
            print('-' * 50)
            print(e)
                #记录日志
    sql = 'insert into kline_log (symbol,timestamp) values("%s",CURRENT_TIMESTAMP)'%(stock_symbol) 
    mc.execute_modify_mysql(sql)
    mc.execute_commit() #一支股票数据采集完整一次提交
#关闭数据库连接 
print("OVER")
del mc
