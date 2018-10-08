import json
import requests
import pymysql
from http.cookiejar import Cookie
#下面三行为getcookie添加
import os
import sqlite3
from win32.win32crypt import CryptUnprotectData
#import win32crypt
 
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
        self.db = pymysql.connect(host="localhost",user="test",password="test",db="stocks",port=3311, charset="utf8mb4" )
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
    #'Host': 'xueqiu.com',
    #'Referer': 'https://xueqiu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #'X-Requested-With': 'XMLHttpRequest',
    #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

# urllib 的相关操作如下
url = 'https://xueqiu.com/v4/statuses/public_timeline_by_category.json?since_id=-1&max_id=-1&count=10&category=111' 
#"https://xueqiu.com/stock/f10/compinfo.json?symbol=SZ000001"  


response = requests.get(url, headers=headers,cookies=getcookiefromchrome('.xueqiu.com'))
res_dict = json.loads(response.text)

print(res_dict)

list_list = res_dict['list']
#print(list_list)
# 遍历 list_list
data = {}
for list_item_dict in list_list:
    # list 列表内的一个item, 他是一个dict
    data_str = list_item_dict['data']
    data_dict = json.loads(data_str)
    data['ids'] = data_dict['id']
    data['title'] = data_dict['title']
    data['description'] = data_dict['description']
    data['target'] = data_dict['target']
    print(data_dict['id'])
    print(data_dict['title'])
    print(data_dict['description'])
    print(data_dict['target'])

    # print(list_item_dict)
    try:
        sql = 'insert into xueqiu(ids,title,description,target) values("{ids}","{title}","{description}","{target}")'.format(**data)
        mc = mysql_conn()
        mc.execute_modify_mysql(sql)
        print('以上内容爬取成功')
        print('-' * 50)
    except:
        print('以上内容出错，没有存到数据库')
        print('-' * 50)
