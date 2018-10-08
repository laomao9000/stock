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
    # 魔术方法, 析构化 ,析构函数
    def __del__(self):
        self.cursor.close()
        self.db.close()




# 因为不能访问, 所以我们加个头试试
headers = {
    #'Accept': '*/*',
    #'Accept-Encoding': 'gzip, deflate, br',
    #'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #'Connection': 'keep-alive',
    #'Cookie': 'aliyungf_tc=AQAAALoQF3p02gsAUhVFebQ3uBBNZn+H; xq_a_token=584d0cf8d5a5a9809761f2244d8d272bac729ed4; xq_a_token.sig=x0gT9jm6qnwd-ddLu66T3A8KiVA; xq_r_token=98f278457fc4e1e5eb0846e36a7296e642b8138a; xq_r_token.sig=2Uxv_DgYTcCjz7qx4j570JpNHIs; _ga=GA1.2.516718356.1534295265; _gid=GA1.2.1050085592.1534295265; u=301534295266356; device_id=f5c21e143ce8060c74a2de7cbcddf0b8; Hm_lvt_1db88642e346389874251b5a1eded6e3=1534295265,1534295722; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1534295722',
    #'Cookie':'Hm_lpvt_1db88642e346389874251b5a1eded6e3=1538206459;Hm_lvt_1db88642e346389874251b5a1eded6e3=1538120732,1538144989,1538206010,1538206459', '_ga': 'GA1.2.1715450264.1532421729', '_gid': 'GA1.2.1367684432.1537964115', 'bid': '9bff933477b6c75b2ff40032e613edb6_jjzgesh9', 'device_id': '61f5d2eff7db22470fda980ead33cda9', 'remember': '1', 'remember.sig': 'K4F3faYzmVuqC0iXIERCQf55g2Y', 's': 'er17v6p058', 'snbim_minify': 'true', 'u': '1781168269', 'u.sig': 'cMmZfQkGyfjC5lehGsI4jsHDp-w', 'xq_a_token': '8a8848e34abe1b04ab2fb720b9d124b2368ec1b4', 'xq_a_token.sig': 'gUjJ-JIAMsQ2dcAIqZKMZbpclYU', 'xq_is_login': '1', 'xq_is_login.sig': 'J3LxgPVPUzbBg3Kee_PquUfih7Q', 'xq_r_token': '2827c657061f1072f18dd4208a8e548799fdf31b', 'xq_r_token.sig': 'y3_9YXXKVvXnZeppIJoOCI923S4'}'
    'Host': 'xueqiu.com',
    'Referer': 'https://xueqiu.com/hq',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

    #'X-Requested-With': 'XMLHttpRequest',
}


url = 'https://xueqiu.com/stock/quote_order.json?page={page}&size=90&order=asc&exchange=CN&stockType={stocktype}&column=symbol%2Cname%2Ccurrent%2Cchg%2Cpercent%2Clast_close%2Copen%2Chigh%2Clow%2Cvolume%2Camount%2Cmarket_capital%2Cpe_ttm%2Chigh52w%2Clow52w%2Chasexist&orderBy=symbol&_={timestamp}'

#https://xueqiu.com/stock/quote_order.json?page=1&size=90&order=desc&exchange=CN&stockType=sza&column=symbol%2Cname%2Ccurrent%2Cchg%2Cpercent%2Clast_close%2Copen%2Chigh%2Clow%2Cvolume%2Camount%2Cmarket_capital%2Cpe_ttm%2Chigh52w%2Clow52w%2Chasexist&orderBy=percent&_=1538830252423

#获取股票代码、实时行情

data={}
stock_count=0 #计数器
mc = mysql_conn() #数据库连接
for stock_type in ('sha','sza'):
    timestp=int(round(time.time() * 1000))
    response = requests.get(url.format(page=1,stocktype=stock_type,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
    res_dict = json.loads(response.text)
    
    stock_count=0 #计数器
    #股票数量计数
    count_val = int(res_dict['count'])
    pagemax=count_val//90
    #count计数为json时使用
    #count_val = res_dict['count']
    
    
    for p in range(1,pagemax+2):
        timestp=int(round(time.time() * 1000))
        response = requests.get(url.format(page=p,stocktype=stock_type,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
        while response.status_code != requests.codes.ok:
            print('重复读取第%d页数据'%(p))
            time.sleep(0.3)
            timestp=int(round(time.time() * 1000))
            response = requests.get(url.format(page=p,stocktype=stock_type,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
           
        else:
            pass

        print('page--%d %s ' %(p,stock_type))
        #为空替换为0，防止出错
        res_dict = json.loads(response.text.replace('null', '0'))
        #print(res_dict)
        stock_list = res_dict['data']
        for stock_list_item in stock_list:
            #字段为数字
            data['symbol']=stock_list_item[0]
            data['code']=stock_list_item[0]
            data['name'] = stock_list_item[1]
            data['current']=stock_list_item[2]
            data['percent']=stock_list_item[4]
            data['high52w'] = stock_list_item[13]
            data['low52w'] = stock_list_item[14]
            data['marketcapital']=stock_list_item[11]
            data['amount']=stock_list_item[10]
            data['volume']=stock_list_item[9]
            data['pe_ttm']=stock_list_item[12]
           
            try:
                sql = 'insert into stocks(symbol,compcode,compsname,current,percent,high52w,low52w,marketcapital,amount,volume,pe_ttm) \
                       values("{symbol}","{code}","{name}","{current}","{percent}","{high52w}","{low52w}","{marketcapital}","{amount}","{volume}","{pe_ttm}")\
                        on duplicate key update current="{current}",percent="{percent}",high52w="{high52w}",low52w="{low52w}",marketcapital="{marketcapital}",amount="{amount}",volume="{volume}",pe_ttm="{pe_ttm}",timestamp=CURRENT_TIMESTAMP'.format(**data)

                mc.execute_modify_mysql(sql)
                stock_count=stock_count+1
                print('%s*共计%d支，获取第%d支——%s*%s 爬取成功' %(stock_type,count_val,stock_count,data['code'],data['name']))
                #print('-' * 50)
            except Exception as e :
                print('以上内容出错，没有存到数据库')
                print('-' * 50)
                print(e)
#关闭数据库连接 
del mc
