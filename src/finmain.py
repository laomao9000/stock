import json
import requests
import pymysql
from http.cookiejar import Cookie
#下面三行为getcookie添加
import os
import sqlite3
from win32.win32crypt import CryptUnprotectData
#降低爬网速度
import time
from pymysql.times import Timestamp

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

# 因为不能访问, 所以我们加个头试试
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'xueqiu.com',
    'Referer': 'https://xueqiu.com/S',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

# urllib 的相关操作如下
url = 'https://xueqiu.com/stock/f10/finmainindex.json?symbol={symbol}&page=1&size=100_={timestamp}'

##股票基础信息
#'https://xueqiu.com/stock/f10/compinfo.json?symbol={symbol}&page=1&size=4&_={timestamp}'

#股票列表
#https://xueqiu.com/stock/cata/stocklist.json?page=1&size=30&order=desc&orderby=percent&type=11%2C12&_=1538234389909

#连接数据库
mc = mysql_conn()
stock_symbol_list = mc.execute_select('select a.symbol from stocks a LEFT JOIN finmain_log b on a.symbol=b.compcode where b.compcode is null order by a.symbol asc')
stock_count=0

#获取股票主要财务信息
for (stock_symbol,) in stock_symbol_list:
    
    stock_count=stock_count+1
    timestp=int(round(time.time() * 1000))
    #降低速度
    #time.sleep(0.3)
       
    print('第%d支股票，%s'%(stock_count,stock_symbol))

    response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))

    #重复读取，直到成功
    while response.status_code != requests.codes.ok:
        print('重复读取第%d支股票，%s'%(stock_count,stock_symbol))
        time.sleep(0.3)
        timestp=int(round(time.time() * 1000))
        response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
       
    else:
        pass
    #存储数据
    res_dict = json.loads(response.text.replace('null', '0'))
    reps = res_dict['list']
    #print(reps)
    # 
    data = {}
    for reps_item in reps:
        try:
            #用股票代码替换雪球内部编号
            reps_item['compcode']=stock_symbol
            sql = 'insert into finmain(compcode,reportdate,basiceps,epsdiluted,epsweighted,naps,opercashpershare,peropecashpershare,netassgrowrate,dilutedroe,weightedroe,mainbusincgrowrate,netincgrowrate,totassgrowrate,salegrossprofitrto,mainbusiincome,mainbusiprofit,totprofit,netprofit,totalassets,totalliab,totsharequi,operrevenue,invnetcashflow,finnetcflow,chgexchgchgs,cashnetr,cashequfinbal)\
                values("{compcode}","{reportdate}","{basiceps}","{epsdiluted}","{epsweighted}","{naps}","{opercashpershare}","{peropecashpershare}","{netassgrowrate}","{dilutedroe}","{weightedroe}","{mainbusincgrowrate}","{netincgrowrate}","{totassgrowrate}","{salegrossprofitrto}","{mainbusiincome}","{mainbusiprofit}","{totprofit}","{netprofit}","{totalassets}","{totalliab}","{totsharequi}","{operrevenue}","{invnetcashflow}","{finnetcflow}","{chgexchgchgs}","{cashnetr}","{cashequfinbal}")\
                on duplicate key update basiceps="{basiceps}",epsdiluted="{epsdiluted}",epsweighted="{epsweighted}",naps="{naps}",opercashpershare="{opercashpershare}",peropecashpershare="{peropecashpershare}",netassgrowrate="{netassgrowrate}",dilutedroe="{dilutedroe}",weightedroe="{weightedroe}",mainbusincgrowrate="{mainbusincgrowrate}",netincgrowrate="{netincgrowrate}",totassgrowrate="{totassgrowrate}",salegrossprofitrto="{salegrossprofitrto}",mainbusiincome="{mainbusiincome}",mainbusiprofit="{mainbusiprofit}",totprofit="{totprofit}",netprofit="{netprofit}",totalassets="{totalassets}",totalliab="{totalliab}",totsharequi="{totsharequi}",operrevenue="{operrevenue}",invnetcashflow="{invnetcashflow}",finnetcflow="{finnetcflow}",chgexchgchgs="{chgexchgchgs}",cashnetr="{cashnetr}",cashequfinbal="{cashequfinbal}"'.format(**reps_item) 
            #print(sql)    
            mc.execute_modify_mysql(sql)
            print('%s*%s*财报 爬取成功' %(stock_symbol,reps_item['reportdate']))
            sql = 'insert into finmain_log (compcode,reportdate,timestamp) \
                values("{compcode}","{reportdate}",CURRENT_TIMESTAMP)'.format(**reps_item) 
            mc.execute_modify_mysql(sql)    
        except Exception as e :
            print('以上内容出错，没有存到数据库')
            print(e)
            print('-' * 50)
    print('-' * 50)
