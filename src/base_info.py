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
from goto import with_goto
#import win32crypt

from goto import with_goto
 
 

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
    #'Cookie': 'aliyungf_tc=AQAAALoQF3p02gsAUhVFebQ3uBBNZn+H; xq_a_token=584d0cf8d5a5a9809761f2244d8d272bac729ed4; xq_a_token.sig=x0gT9jm6qnwd-ddLu66T3A8KiVA; xq_r_token=98f278457fc4e1e5eb0846e36a7296e642b8138a; xq_r_token.sig=2Uxv_DgYTcCjz7qx4j570JpNHIs; _ga=GA1.2.516718356.1534295265; _gid=GA1.2.1050085592.1534295265; u=301534295266356; device_id=f5c21e143ce8060c74a2de7cbcddf0b8; Hm_lvt_1db88642e346389874251b5a1eded6e3=1534295265,1534295722; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1534295722',
    #'Cookie':'Hm_lpvt_1db88642e346389874251b5a1eded6e3=1538206459;Hm_lvt_1db88642e346389874251b5a1eded6e3=1538120732,1538144989,1538206010,1538206459', '_ga': 'GA1.2.1715450264.1532421729', '_gid': 'GA1.2.1367684432.1537964115', 'bid': '9bff933477b6c75b2ff40032e613edb6_jjzgesh9', 'device_id': '61f5d2eff7db22470fda980ead33cda9', 'remember': '1', 'remember.sig': 'K4F3faYzmVuqC0iXIERCQf55g2Y', 's': 'er17v6p058', 'snbim_minify': 'true', 'u': '1781168269', 'u.sig': 'cMmZfQkGyfjC5lehGsI4jsHDp-w', 'xq_a_token': '8a8848e34abe1b04ab2fb720b9d124b2368ec1b4', 'xq_a_token.sig': 'gUjJ-JIAMsQ2dcAIqZKMZbpclYU', 'xq_is_login': '1', 'xq_is_login.sig': 'J3LxgPVPUzbBg3Kee_PquUfih7Q', 'xq_r_token': '2827c657061f1072f18dd4208a8e548799fdf31b', 'xq_r_token.sig': 'y3_9YXXKVvXnZeppIJoOCI923S4'}'
    'Cookie':'device_id=61f5d2eff7db22470fda980ead33cda9; _ga=GA1.2.1715450264.1532421729; s=er17v6p058; bid=9bff933477b6c75b2ff40032e613edb6_jjzgesh9; remember=1; remember.sig=K4F3faYzmVuqC0iXIERCQf55g2Y; xq_a_token=8a8848e34abe1b04ab2fb720b9d124b2368ec1b4; xq_a_token.sig=gUjJ-JIAMsQ2dcAIqZKMZbpclYU; xq_r_token=2827c657061f1072f18dd4208a8e548799fdf31b; xq_r_token.sig=y3_9YXXKVvXnZeppIJoOCI923S4; xq_is_login=1; xq_is_login.sig=J3LxgPVPUzbBg3Kee_PquUfih7Q; u=1781168269; u.sig=cMmZfQkGyfjC5lehGsI4jsHDp-w; _gid=GA1.2.1367684432.1537964115; aliyungf_tc=AQAAAHiOFxzQvAkAnHQGcEZiz5DUijt0; snbim_minify=true; __utmc=1; __utmz=1.1538233687.73.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; Hm_lvt_1db88642e346389874251b5a1eded6e3=1538233575,1538233656,1538233685,1538276572; __utma=1.1715450264.1532421729.1538270997.1538281139.76; __utmt=1; __utmb=1.23.10.1538281139; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1538283036',
    'Host': 'xueqiu.com',
    'Referer': 'https://xueqiu.com/S',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

# urllib 的相关操作如下
url = 'https://xueqiu.com/stock/f10/compinfo.json?symbol={symbol}&page=1&size=4&_={timestamp}'

#股票列表
#https://xueqiu.com/stock/cata/stocklist.json?page=1&size=30&order=desc&orderby=percent&type=11%2C12&_=1538234389909

#股票基础信息
#"https://xueqiu.com/stock/f10/compinfo.json?symbol=SZ000001"   

#连接数据库
mc = mysql_conn()
stock_symbol_list = mc.execute_select('select symbol from stocks order by symbol asc')
stock_count=0


#获取股票基础信息
for (stock_symbol,) in stock_symbol_list:
    
    stock_count=stock_count+1
    timestp=int(round(time.time() * 1000))
    #降低速度
    #time.sleep(0.3)
       
    print('第%d支股票，%s'%(stock_count,stock_symbol))
    #print(url.format(symbol=stock_symbol,timestamp=timestp))
    response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers)
    #response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
    #print(response.status_code)
    #重复读取，直到成功
    while response.status_code != requests.codes.ok:
        print('重复读取第%d支股票，%s'%(stock_count,stock_symbol))
        time.sleep(0.3)
        timestp=int(round(time.time() * 1000))
        response = requests.get(url.format(symbol=stock_symbol,timestamp=timestp), headers=headers)
    else:
        #存储数据
        res_dict = json.loads(response.text)
        #continue
    #print(res_dict)
    
    compinfo = res_dict['tqCompInfo']
    #print(compinfo)
    # 
    data = {}
    
    #data_dict = json.loads(data_str)
    data['compcode'] = stock_symbol
    data['compname'] = compinfo['compname']
    data['engname'] = compinfo['engname']
    data['founddate'] = compinfo['founddate']
    data['regcapital'] = compinfo['regcapital']
    data['chairman'] = compinfo['chairman']
    data['manager'] = compinfo['manager']
    data['leconstant'] = compinfo['leconstant']
    data['accfirm'] = compinfo['accfirm']
    data['regaddr'] = compinfo['regaddr']
    data['officeaddr'] = compinfo['officeaddr']
    data['compintro'] = compinfo['compintro'].replace('"',' ')
    data['bizscope'] = compinfo['bizscope'].replace('"',' ')
    data['majorbiz'] = compinfo['majorbiz'].replace('"',' ')
    data['compsname'] = compinfo['compsname']
    data['region'] = compinfo['region']
    #print(data)
    try:
        sql = 'insert into comp(compname,engname,founddate,regcapital,chairman,manager,leconstant,accfirm,regaddr,officeaddr,compintro,bizscope,majorbiz,compcode,compsname,region) \
               values("{compname}","{engname}","{founddate}","{regcapital}","{chairman}","{manager}","{leconstant}","{accfirm}","{regaddr}","{officeaddr}","{compintro}","{bizscope}","{majorbiz}","{compcode}","{compsname}","{region}")\
                on duplicate key update compname="{compname}",engname="{engname}",regcapital="{regcapital}",chairman="{chairman}",manager="{manager}",leconstant="{leconstant}",accfirm="{accfirm}",regaddr="{regaddr}",\
                officeaddr="{officeaddr}",compintro="{compintro}",bizscope="{bizscope}",majorbiz="{majorbiz}",compsname="{compsname}",region="{region}",timestamp=CURRENT_TIMESTAMP'.format(**data)
        mc.execute_modify_mysql(sql)
        print('%s*%s 爬取成功' %(data['compcode'],data['compsname']))
        #print('-' * 50)
    except Exception as e :
        print('以上内容出错，没有存到数据库')
        print('-' * 50)
        print(e)
